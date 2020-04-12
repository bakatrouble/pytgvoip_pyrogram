import pyrogram

from tgvoip import VoIPServerConfig
from tgvoip_pyrogram import VoIPFileStreamService, VoIPIncomingFileStreamCall,\
    VoIPNativeIOService, VoIPIncomingNativeIOCall

VoIPServerConfig.set_bitrate_config(80000, 100000, 60000, 5000, 5000)
client = pyrogram.Client('session')
client.start()
service = VoIPFileStreamService(client)  # use VoIPNativeIOService for native I/O


@service.on_incoming_call
def process_call(call: VoIPIncomingFileStreamCall):  # use VoIPIncomingNativeIOCall for native I/O
    call.accept()
    call.play('input.raw')
    call.play_on_hold(['input.raw'])
    call.set_output_file('output.raw')

    # you can use `call.on_call_ended(lambda _: app.stop())` here instead
    @call.on_call_ended
    def call_ended(call):
        client.stop()
