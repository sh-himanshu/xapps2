__all__ = ["Http"]

from typing import Optional

from aiohttp import ClientSession


class Http:
    def __init__(self) -> None:
        self._session: Optional[ClientSession] = None
        super().__init__()

    @property
    def is_active(self) -> bool:
        return self._session and not self._session.closed

    @property
    def http(self) -> ClientSession:
        if not self.is_active:
            self._session = self.new_session()
        return self._session

    @staticmethod
    def new_session() -> ClientSession:
        return ClientSession()
