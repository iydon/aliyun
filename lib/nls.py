__all__ = ['NLS']


import pathlib as p
import typing as t

from .third_party import nls


class NLS:
    Self = __qualname__

    _config = None

    @classmethod
    def register(cls, access_key_id: str, access_key_secret: str, app_key: str) -> type:
        cls._config = {
            'akid': access_key_id,
            'aksecret': access_key_secret,
            'appkey': app_key,
        }
        return cls

    def __init__(
        self,
        format: str = 'mp3', speaker: str = 'andy', volume: int = 50,
        sample_rate: int = 16000, speech_rate: int = 0, pitch_rate: int = 0,
        verbose: bool = True,
    ) -> None:
        self._default = {
            'aformat': format,
            'voice': speaker,
            'volume': volume,
            'sample_rate': sample_rate,
            'speech_rate': speech_rate,
            'pitch_rate': pitch_rate,
        }
        self._tts = nls.NlsSpeechSynthesizer(
            on_metainfo=self._on_metainfo,
            on_data=self._on_data,
            on_completed=self._on_completed,
            on_error=self._on_error,
            on_close=self._on_close,
            **self._config,
        )
        self._verbose = verbose
        self._file = None

    def tts(self, text: str, path: t.Union[str, p.Path], **kwargs) -> bool:
        self._file = open(path, 'wb')
        return self._tts.start(text=text, **self._default, **kwargs)

    def close(self) -> None:
        self._tts.shutdown()

    def _on_metainfo(self, message: t.Dict[str, t.Any], *args: t.Any) -> None:
        if self._verbose:
            print(f'on_metainfo: message={message}, *args={args}')

    def _on_data(self, data: bytes, *args: t.Any) -> None:
        if self._verbose:
            print(f'on_data: data=..., *args={args}')
        self._file.write(data)

    def _on_completed(self, message: t.Dict[str, t.Any], *args: t.Any) -> None:
        if self._verbose:
            print(f'on_completed: message={message}, *args={args}')

    def _on_error(self, message: t.Dict[str, t.Any], *args: t.Any) -> None:
        if self._verbose:
            print(f'on_error: message={message}, *args={args}')

    def _on_close(self, *args: t.Any) -> None:
        if self._verbose:
            print(f'on_close: *args={args}')
        self._file.close()
