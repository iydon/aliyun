# https://help.aliyun.com/document_detail/101645.html
import json
import pathlib as p

from lib.nls import NLS


paths = [
    p.Path('config', 'private.json'),
    p.Path('config', 'public.json'),
]
config = json.loads(next(filter(lambda p: p.exists(), paths)).read_text())
NLS.register(**config['auth'], **config['nls'])

format = 'mp3'
nls = NLS(format=format, speaker='lydia', verbose=True)
for src in p.Path('data', 'tts').iterdir():
    if src.is_file() and src.suffix=='.txt' and not (src.parent/src.stem).exists():
        print(f'Path: {src}')
        directory = src.parent / src.stem
        directory.mkdir(parents=True, exist_ok=True)

        for ith, line in enumerate(src.read_text().splitlines()):
            if line:
                nls.tts(line, directory/f'{ith+1}.{format}')
