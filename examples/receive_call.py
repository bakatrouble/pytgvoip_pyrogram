import asyncio

import pyrogram

from tgvoip import VoIPServerConfig
from tgvoip_pyrogram import VoIPFileStreamService, VoIPIncomingFileStreamCall,\
    VoIPNativeIOService, VoIPIncomingNativeIOCall

VoIPServerConfig.set_bitrate_config(80000, 100000, 60000, 5000, 5000)
client = pyrogram.Client('session')
loop = asyncio.get_event_loop()
service = VoIPFileStreamService(client)  # use VoIPNativeIOService for native I/O


@service.on_incoming_call
async def process_call(call: VoIPIncomingFileStreamCall):  # use VoIPIncomingNativeIOCall for native I/O
    await call.accept()
    call.play('input.raw')
    call.play_on_hold(['input.raw'])
    call.set_output_file('output.raw')

    # you can use `call.on_call_ended(lambda _: app.stop())` here instead
    @call.on_call_ended
    async def call_ended(call):
        await client.stop()

loop.run_until_complete(client.run())
