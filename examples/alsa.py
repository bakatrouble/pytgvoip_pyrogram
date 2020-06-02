import asyncio

from alsaaudio import PCM, PCM_NONBLOCK, PCM_CAPTURE

from tgvoip import VoIPServerConfig
from tgvoip_pyrogram import VoIPOutgoingCall, VoIPService
import pyrogram


class VoIPAlsaOutgoingCall(VoIPOutgoingCall):
    def __init__(self, *args, **kwargs):
        super(VoIPAlsaOutgoingCall, self).__init__(*args, **kwargs)
        self.playback_device = None
        self.capture_device = None
        self.ctrl.set_send_audio_frame_callback(self._read_frame)
        self.ctrl.set_recv_audio_frame_callback(self._write_frame)

    def build_capture_device(self):
        self.capture_device = PCM(PCM_CAPTURE, PCM_NONBLOCK)
        self.capture_device.setrate(48000)
        self.capture_device.setperiodsize(960)
        self.capture_device.setchannels(1)

    def build_playback_device(self):
        self.playback_device = PCM(mode=PCM_NONBLOCK)
        self.playback_device.setrate(48000)
        self.playback_device.setperiodsize(960)
        self.playback_device.setchannels(1)

    def _read_frame(self, length: int):
        if not self.capture_device:
            self.build_capture_device()
        _, frame = self.capture_device.read()
        return frame

    def _write_frame(self, frame: bytes):
        if not self.playback_device:
            self.build_playback_device()
        self.playback_device.write(frame)


VoIPServerConfig.set_bitrate_config(80000, 100000, 60000, 5000, 5000)
client = pyrogram.Client('session')
loop = asyncio.get_event_loop()
voip_service = VoIPService(client, receive_calls=False)
voip_service.outgoing_call_class = VoIPAlsaOutgoingCall


async def main():
    await client.start()
    call1 = await voip_service.start_call('@bakatrouble')

    # you can use `call.on_call_ended(lambda _: app.stop())` here instead
    @call1.on_call_ended
    async def call_ended(call):
        await client.stop()

    await client.idle()

loop.run_until_complete(main())
