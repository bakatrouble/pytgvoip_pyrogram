# PytgVoIP-Pyrogram - Pyrogram support module for Telegram VoIP Library for Python
# Copyright (C) 2020 bakatrouble <https://github.com/bakatrouble>
#
# This file is part of PytgVoIP.
#
# PytgVoIP is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PytgVoIP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with PytgVoIP.  If not, see <http://www.gnu.org/licenses/>.
from threading import Thread

import pyrogram
from pyrogram import errors
from pyrogram.api import types, functions

from tgvoip import VoIPController, CallState, CallError, Endpoint, DataSaving, VoIPServerConfig
from tgvoip.utils import i2b, b2i, check_g


class DH:
    def __init__(self, dhc: types.messages.DhConfig):
        self.p = b2i(dhc.p)
        self.g = dhc.g
        self.resp = dhc


class VoIPCallBase:
    min_layer = 65
    max_layer = VoIPController.CONNECTION_MAX_LAYER
    is_outgoing = False

    def __init__(self, client: pyrogram.Client, use_proxy_if_available: bool = True):
        if not client.is_connected:
            raise RuntimeError('Client must be started first')
        self.client = client
        self.ctrl = VoIPController()
        self.ctrl_started = False
        self.call = None
        self.call_access_hash = None
        self.peer = None
        self.state = None
        self.dhc = self.get_dhc()
        self.a = None
        self.g_a = None
        self.g_a_hash = None
        self.b = None
        self.g_b = None
        self.g_b_hash = None
        self.auth_key = None
        self.key_fingerprint = None
        self.call_started_handlers = []
        self.call_discarded_handlers = []
        self.call_ended_handlers = []

        if use_proxy_if_available and client.proxy:
            proxy = self.client.proxy
            self.ctrl.set_proxy(proxy['hostname'], proxy['port'], proxy['username'], proxy['password'])

        self._update_handler = pyrogram.RawUpdateHandler(self.process_update)
        self.client.add_handler(self._update_handler, -1)

    def process_update(self, _, update, users, chats):
        if not isinstance(update, types.UpdatePhoneCall):
            raise pyrogram.ContinuePropagation

        call = update.phone_call
        if not self.call or not call or call.id != self.call.id:
            raise pyrogram.ContinuePropagation
        self.call = call
        if hasattr(call, 'access_hash') and call.access_hash:
            self.call_access_hash = call.access_hash

        if isinstance(call, types.PhoneCallDiscarded):
            self.call_discarded()
            raise pyrogram.StopPropagation

    def on_call_started(self, func: callable) -> callable:  # well, the conversation has started
        self.call_started_handlers.append(func)
        return func

    def on_call_discarded(self, func: callable) -> callable:  # call was discarded, not necessarily started before
        self.call_discarded_handlers.append(func)
        return func

    def on_call_ended(self, func: callable) -> callable:  # call was discarded with non-busy reason
                                                          # (was started and then discarded?)
        self.call_ended_handlers.append(func)
        return func

    def on_call_state_changed(self, func: callable) -> callable:
        if callable(func):
            self.ctrl.call_state_changed_handlers.append(lambda state: func(self, state))
        return func

    @property
    def auth_key_bytes(self) -> bytes:
        return i2b(self.auth_key) if self.auth_key is not None else b''

    @property
    def call_id(self) -> int:
        return self.call.id if self.call else 0

    def get_protocol(self) -> types.PhoneCallProtocol:
        return types.PhoneCallProtocol(min_layer=self.min_layer, max_layer=self.max_layer, udp_p2p=True,
                                       udp_reflector=True, library_versions=["2.4.4", "2.7"])

    def get_dhc(self) -> DH:
        return DH(self.client.send(functions.messages.GetDhConfig(version=0, random_length=256)))

    def check_g(self, g_x: int, p: int) -> None:
        try:
            check_g(g_x, p)
        except RuntimeError:
            self.call_discarded()
            raise

    def stop(self) -> None:
        def _():
            try:
                self.client.remove_handler(self._update_handler, -1)
            except ValueError:
                pass
        Thread(target=_).start()

        del self.ctrl
        self.ctrl = None

        for handler in self.call_ended_handlers:
            callable(handler) and Thread(target=handler, args=(self,)).start()

    def update_state(self, val: CallState) -> None:
        self.state = val
        self.ctrl.update_state(val)

    def call_ended(self) -> None:
        self.update_state(CallState.ENDED)
        self.stop()

    def call_failed(self, error: CallError = None) -> None:
        if error is None:
            error = self.ctrl.get_last_error() if self.ctrl and self.ctrl_started else CallError.UNKNOWN
        print('Call', self.call_id, 'failed with error', error)
        self.update_state(CallState.FAILED)
        self.stop()

    def call_discarded(self):
        # TODO: call.need_debug
        need_rate = self.ctrl and VoIPServerConfig.config.get('bad_call_rating') and self.ctrl.need_rate()
        if isinstance(self.call.reason, types.PhoneCallDiscardReasonBusy):
            self.update_state(CallState.BUSY)
            self.stop()
        else:
            self.call_ended()
        if self.call.need_rating or need_rate:
            pass  # TODO: rate

        for handler in self.call_discarded_handlers:
            callable(handler) and Thread(target=handler, args=(self,)).start()

    def discard_call(self, reason=None):
        # TODO: rating
        if not reason:
            reason = types.PhoneCallDiscardReasonDisconnect()
        try:
            self.client.send(functions.phone.DiscardCall(
                peer=types.InputPhoneCall(id=self.call_id, access_hash=self.call_access_hash),
                duration=self.ctrl.call_duration,
                connection_id=self.ctrl.get_preferred_relay_id(),
                reason=reason
            ))
        except (errors.CallAlreadyDeclined, errors.CallAlreadyAccepted):
            pass
        self.call_ended()

    def _initiate_encrypted_call(self) -> None:
        config = self.client.send(functions.help.GetConfig())  # type: types.Config
        self.ctrl.set_config(config.call_packet_timeout_ms / 1000., config.call_connect_timeout_ms / 1000.,
                             DataSaving.NEVER, self.call.id)
        self.ctrl.set_encryption_key(self.auth_key_bytes, self.is_outgoing)
        endpoints = [Endpoint(e.id, e.ip, e.ipv6, e.port, e.peer_tag) for e in self.call.connections]
        self.ctrl.set_remote_endpoints(endpoints, self.call.p2p_allowed, False, self.call.protocol.max_layer)
        self.ctrl.start()
        self.ctrl.connect()
        self.ctrl_started = True
        self.update_state(CallState.ESTABLISHED)

        for handler in self.call_started_handlers:
            callable(handler) and Thread(target=handler, args=(self,)).start()
