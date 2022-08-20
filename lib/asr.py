__all__ = ['ASR']


import json
import pathlib as p
import time
import typing as t

from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


Path = t.Union[str, p.Path]


class ASR:
    Self = __qualname__

    _client = None
    _appkey = None

    @classmethod
    def register(cls, access_key_id: str, access_key_secret: str, app_key: str) -> type:
        cls._client = AcsClient(
            access_key_id, access_key_secret, 'cn-shanghai',
        )
        cls._appkey = app_key
        return cls

    @classmethod
    def from_backup(cls, path: Path) -> Self:
        data = json.loads(p.Path(path).read_text())
        self = cls(data['url'])
        self._data = data['data']
        return self

    def __init__(self, url: str) -> None:
        self._url = url
        self._data = None
        self._task_id = None

    @property
    def data(self) -> t.Optional[t.Dict[str, t.Any]]:
        return self._data

    @property
    def task_id(self) -> t.Optional[str]:
        return self._task_id

    def upload(self) -> Self:
        request = self._request(post=True)
        task = {
            'appkey': self._appkey, 'file_link': self._url, 'version': '4.0',
            'enable_words': True, 'enable_sample_rate_adaptive': True,
        }
        request.add_body_params('Task', json.dumps(task))
        try:
            response = json.loads(self._client.do_action_with_exception(request))
            if response['StatusText'] == 'SUCCESS':
                self._task_id = response['TaskId']
                print(f'TaskID: {self._task_id}')
                return self
        except (ServerException, ClientException) as e:
            print(e)

    def polling(self, delay: int = 10) -> Self:
        assert self._task_id is not None
        request = self._request(post=False)
        request.add_query_param('TaskId', self._task_id)
        # 提交录音文件识别结果查询请求
        while True:
            try:
                response = json.loads(self._client.do_action_with_exception(request))
                if response['StatusText'] not in ('RUNNING', 'QUEUEING'):
                    self._data = response
                    return self
                time.sleep(delay)
            except (ServerException, ClientException) as e:
                print(e)

    def to(self, *paths: Path, channel_id: int = 0) -> Self:
        mapper = {
            f'.{attr[3:]}': getattr(self, attr)
            for attr in dir(self)
            if attr.startswith('to_')
        }
        for path in map(self._path, paths):
            mapper[path.suffix](path, channel_id)
        return self

    def to_srt(self, path: Path, channel_id: int = 0) -> Self:
        data = filter(lambda x: x['ChannelId']==channel_id, self._data['Result']['Sentences'])
        pattern = '{h:02}:{m:02}:{s:02},{ms:03}'
        with open(self._path(path), 'w') as f:
            for ith, item in enumerate(sorted(data, key=lambda x: x['BeginTime'])):
                start, end = (self._time(item[k], pattern) for k in ('BeginTime', 'EndTime'))
                f.write(f'{ith}\n{start} --> {end}\n{item["Text"]}\n\n')
        return self

    def to_txt(self, path: Path, channel_id: int = 0) -> Self:
        self._path(path).write_text(
            '\n'.join(
                sentence['Text']
                for sentence in self._data['Result']['Sentences']
                if sentence['ChannelId'] == channel_id
            )
        )
        return self

    def to_backup(self, path: Path, channel_id: int = 0) -> Self:
        self._path(path).write_text(
            json.dumps({
                'url': self._url,
                'data': self._data,
            }, ensure_ascii=False)
        )
        return self

    def _request(self, post: bool = True) -> CommonRequest:
        request = CommonRequest()
        request.set_domain('filetrans.cn-shanghai.aliyuncs.com')
        request.set_version('2018-08-17')
        request.set_product('nls-filetrans')
        request.set_action_name('SubmitTask' if post else 'GetTaskResult')
        request.set_method('POST' if post else 'GET')
        return request

    def _time(self, microsecond: int, pattern: str = '{h:02}:{m:02}:{s:02},{ms:03}') -> str:
        def f(microsecond: int) -> t.Iterator[int]:
            for c in (1000, 60, 60, 60):
                yield microsecond % c
                microsecond //= c

        ms, s, m, h = f(microsecond)
        return pattern.format(ms=ms, s=s, m=m, h=h)

    def _path(self, path: Path) -> p.Path:
        path = p.Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
