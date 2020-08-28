import asyncio

from tgvoip import VoIPServerConfig
from tgvoip_pyrogram import VoIPFileStreamService
import pyrogram


VoIPServerConfig.set_bitrate_config(80000, 100000, 60000, 5000, 5000)
client = pyrogram.Client('session')
loop = asyncio.get_event_loop()

voip_service = VoIPFileStreamService(client, receive_calls=False)


@client.on_message(pyrogram.filters.command('callme'))
async def callme(cl, message: pyrogram.types.Message):
    call = await voip_service.start_call(message.from_user.id)
    call.play('input.raw')
    call.play_on_hold(['input.raw'])
    call.set_output_file('output.raw')


async def main():
    await client.start()
    print(await client.export_session_string())
    await pyrogram.idle()

loop.run_until_complete(main())
