__all__ = ['OSS']


import hashlib
import pathlib as p
import typing as t

import oss2


Path = t.Union[str, p.Path]


class OSS:
    Self = __qualname__

    _bucket = None
    _domain = None

    @classmethod
    def register(
        cls,
        access_key_id: str, access_key_secret: str,
        endpoint: str, bucket_name: str, bucket_domain: str,
    ) -> type:
        auth = oss2.Auth(access_key_id, access_key_secret)
        cls._bucket = oss2.Bucket(auth, endpoint, bucket_name)
        cls._domain = bucket_domain
        return cls

    def __init__(self, path: Path) -> None:
        self._path = p.Path(path).absolute()
        self._name = self._md5(str(self._path)) + self._path.suffix

    def __enter__(self) -> Self:
        return self.upload()

    def __exit__(self, type, value, traceback) -> None:
        self.delete()

    @property
    def url(self) -> str:
        return f'https://{self._domain}/{self._name}'

    def upload(self) -> Self:
        self._bucket.put_object_from_file(self._name, str(self._path))
        return self

    def delete(self) -> Self:
        self._bucket.delete_object(self._name)
        return self

    def _md5(self, string: str) -> str:
        return hashlib.md5(string.encode()).hexdigest()
