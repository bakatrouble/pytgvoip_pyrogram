# pytgvoip_pyrogram

[![PyPI](https://img.shields.io/pypi/v/pytgvoip_pyrogram.svg?style=flat)](https://pypi.org/project/pytgvoip_pyrogram/)

**Sample usage of [PytgVoIP](https://github.com/bakatrouble/pytgvoip) library with [Pyrogram](https://github.com/bakatrouble/pyrogram)**

Hopefully `pytgvoip` support will be [integrated in Pyrogram itself](https://github.com/pyrogram/pyrogram/pull/218), but this repository would still be available as reference even after merge. 

Detailed `pytgvoip` usage guide is also available [here](https://pytgvoip.readthedocs.io/en/latest/guides/usage.html)  

[Community](https://t.me/pytgvoip)

```python
# making outgoing calls
from pyrogram import Client
from tgvoip_pyrogram import VoIPFileStreamService

app = Client('account')
app.start()

service = VoIPFileStreamService(app, receive_calls=False)
call = service.start_call('@bakatrouble')
call.play('input.raw')
call.play_on_hold(['input.raw'])
call.set_output_file('output.raw')

@call.on_call_ended
def call_ended(call):
    app.stop()
```

```python
# accepting incoming calls
from pyrogram import Client
from tgvoip_pyrogram import VoIPFileStreamService, VoIPIncomingFileStreamCall

app = Client('account')
app.start()

service = VoIPFileStreamService(app)

@service.on_incoming_call
def handle_call(call: VoIPIncomingFileStreamCall):
    call.accept()
    call.play('input.raw')
    call.play_on_hold(['input.raw'])
    call.set_output_file('output.raw')
    
    # you can use `call.on_call_ended(lambda _: app.stop())` here instead
    @call.on_call_ended
    def call_ended(call):
        app.stop()
```

[More examples](examples/README.md)

## Requirements
* Python 3.5 or higher
* PytgVoIP (listed as dependency)
* Pyrogram (listed as dependency)

## Installing
```pip3 install pytgvoip-pyrogram```


## Encoding audio streams
Streams consumed by `libtgvoip` should be encoded in 16-bit signed PCM audio.
```bash
$ ffmpeg -i input.mp3 -f s16le -ac 1 -ar 48000 -acodec pcm_s16le input.raw  # encode
$ ffmpeg -f s16le -ac 1 -ar 48000 -acodec pcm_s16le -i output.raw output.mp3  # decode
```

## Copyright & License
* Copyright (C) 2019 [bakatrouble](https://github.com/bakatrouble)
* Licensed under the terms of the [GNU Lesser General Public License v3 or later (LGPLv3+)](COPYING.lesser)

