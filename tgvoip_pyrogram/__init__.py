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

from tgvoip_pyrogram.service import VoIPService
from tgvoip_pyrogram.incoming_call import VoIPIncomingCall
from tgvoip_pyrogram.outgoing_call import VoIPOutgoingCall
from tgvoip_pyrogram.file_stream_call import VoIPFileStreamCallMixin, VoIPIncomingFileStreamCall, \
    VoIPOutgoingFileStreamCall, VoIPFileStreamService
from tgvoip_pyrogram.native_io_call import VoIPNativeIOCallMixin, VoIPIncomingNativeIOCall, \
    VoIPOutgoingNativeIOCall, VoIPNativeIOService


__all__ = ['VoIPService',
           'VoIPIncomingCall', 'VoIPOutgoingCall',
           'VoIPFileStreamService',
           'VoIPFileStreamCallMixin', 'VoIPIncomingFileStreamCall', 'VoIPOutgoingFileStreamCall',
           'VoIPNativeIOService',
           'VoIPNativeIOCallMixin', 'VoIPIncomingNativeIOCall', 'VoIPOutgoingNativeIOCall']

__version__ = '0.0.8'
