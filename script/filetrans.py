import json
import pathlib as p

import ffmpeg

from lib import ASR, OSS


paths = [
    p.Path('config', 'private.json'),
    p.Path('config', 'public.json'),
]
config = json.loads(next(filter(lambda p: p.exists(), paths)).read_text())
ASR.register(**config['auth'], **config['asr'])
OSS.register(**config['auth'], **config['oss'])

for src in p.Path('data', 'filetrans').iterdir():
    if src.is_file() and not (src.parent/src.stem).exists():
        print(f'Path: {src}')

        dst = src.parent / f'{src.stem}.wav'
        ffmpeg \
            .input(src.as_posix()) \
            .output(
                dst.as_posix(),
                acodec='pcm_s16le', ac=1, ar=16000, vn=None,
            ) \
            .run()

        with OSS(dst) as oss:
            ASR(oss.url) \
                .upload() \
                .polling() \
                .to(
                    src.parent / src.stem / 'main.srt',
                    src.parent / src.stem / 'main.txt',
                    src.parent / src.stem / 'main.backup',
                )

        dst.unlink()
