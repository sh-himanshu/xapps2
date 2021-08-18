__all__ = ["ApkDL"]
import logging
import sys

import pyppeteer

from .http import Http
from .miscdl import MiscDL
from .playstoredl import PlayStoreDL

LOG = logging.getLogger(__name__)


class ApkDL(Http, PlayStoreDL, MiscDL):
    browser: pyppeteer.browser.Browser

    def __init__(self) -> None:
        super().__init__()

    async def start(self) -> None:
        try:
            self.browser = await pyppeteer.launch(headless=True, args=["--no-sandbox"])
        except Exception as e:
            LOG.exception(f"{e.__class__.__name__}: {e}")
            sys.exit("FAILED TO START THE BROWSER !")

    async def stop(self) -> None:
        await self.browser.close()
        if self.is_active:
            await self._session.close()

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *_, **__) -> None:
        await self.stop()
