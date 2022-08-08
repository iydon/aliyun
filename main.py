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


class api:
    @staticmethod
    def doit(src: p.Path) -> None:
        dst = src.parent / f'{src.stem}.wav'
        ffmpeg \
            .input(src.as_posix()) \
            .output(
                dst.as_posix(),
                acodec='pcm_s16le', ac=1, ar=16000, vn=None,
            ) \
            .run()

        oss = OSS(dst)
        oss.upload()
        asr = ASR(oss.url)
        task_id = asr.upload()
        print(f'{task_id = }')
        asr.polling(task_id)
        asr.to(
            src.parent / src.stem / 'main.srt',
            src.parent / src.stem / 'main.txt',
            src.parent / src.stem / 'main.backup',
        )
        dst.unlink()
        oss.delete()


if __name__ == '__main__':
    for path in p.Path('data').iterdir():
        if path.is_file() and not (path.parent/path.stem).exists():
            print(f'{path = }')
            api.doit(path)
