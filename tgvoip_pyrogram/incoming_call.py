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
import asyncio

import hashlib
from random import randint

import pyrogram
from pyrogram import errors
from pyrogram.raw import types, functions

from tgvoip import CallState
from tgvoip.utils import i2b, b2i, calc_fingerprint
from tgvoip_pyrogram.base_call import VoIPCallBase


class VoIPIncomingCall(VoIPCallBase):
    def __init__(self, call: types.PhoneCallRequested, *args, **kwargs):
        super(VoIPIncomingCall, self).__init__(*args, **kwargs)
        self.call_accepted_handlers = []
        self.update_state(CallState.WAITING_INCOMING)
        self.call = call
        self.call_access_hash = call.access_hash

    async def process_update(self, _, update, users, chats):
        await super(VoIPIncomingCall, self).process_update(_, update, users, chats)
        if isinstance(self.call, types.PhoneCall) and not self.auth_key:
            await self.call_accepted()
            raise pyrogram.StopPropagation
        raise pyrogram.ContinuePropagation

    def on_call_accepted(self, func: callable) -> callable:  # telegram acknowledged that you've accepted the call
        self.call_accepted_handlers.append(func)
        return func

    async def accept(self) -> bool:
        self.update_state(CallState.EXCHANGING_KEYS)
        if not self.call:
            self.call_failed()
            raise RuntimeError('call is not set')
        await self.get_dhc()
        self.b = randint(2, self.dhc.p-1)
        self.g_b = pow(self.dhc.g, self.b, self.dhc.p)
        self.g_a_hash = self.call.g_a_hash
        try:
            self.call = (await self.client.send(functions.phone.AcceptCall(
                peer=types.InputPhoneCall(id=self.call_id, access_hash=self.call_access_hash),
                g_b=i2b(self.g_b),
                protocol=self.get_protocol()
            ))).phone_call
        except errors.Error as e:
            if e.ID == 'CALL_ALREADY_ACCEPTED':
                self.stop()
                return True
            elif e.ID == 'CALL_ALREADY_DECLINED':
                self.call_discarded()
                return False
            raise e
        if isinstance(self.call, types.PhoneCallDiscarded):
            print('Call is already discarded')
            self.call_discarded()
            return False
        return True

    async def call_accepted(self) -> None:
        for handler in self.call_accepted_handlers:
            asyncio.iscoroutinefunction(handler) and asyncio.ensure_future(handler(self), loop=self.client.loop)

        if not self.call.g_a_or_b:
            print('g_a is null')
            self.call_failed()
            return
        if self.g_a_hash != hashlib.sha256(self.call.g_a_or_b).digest():
            print('g_a_hash doesn\'t match')
            self.call_failed()
            return
        self.g_a = b2i(self.call.g_a_or_b)
        self.check_g(self.g_a, self.dhc.p)
        self.auth_key = pow(self.g_a, self.b, self.dhc.p)
        self.key_fingerprint = calc_fingerprint(self.auth_key_bytes)
        if self.key_fingerprint != self.call.key_fingerprint:
            print('fingerprints don\'t match')
            self.call_failed()
            return
        await self._initiate_encrypted_call()
