__all__ = ["ApkDL"]
import logging
import sys
from typing import List

import pyppeteer
from random import choice, sample
from .http import Http
from .miscdl import MiscDL
from .playstoredl import PlayStoreDL

LOG = logging.getLogger(__name__)


class ApkDL(Http, PlayStoreDL, MiscDL):
    browser: pyppeteer.browser.Browser
    user_agents: List[str]

    def __init__(self) -> None:
        super().__init__()

    async def load_useragents(self) -> None:
        async with self.http.get(
            "https://raw.githubusercontent.com/code-rgb/useragent/main"
            + choice(("chrome", "firefox", "safari"))
        ) as resp:
            if resp.status == 200:
                text = await resp.text()
                self.user_agents = sample(text.split("\n"), 10)
            else:
                self.user_agents = [
                    (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/74.0.3729.157 Safari/537.36"
                    )
                ]

    async def start(self) -> None:
        try:
            self.browser = await pyppeteer.launch(headless=True, args=["--no-sandbox"])
        except Exception as e:
            LOG.exception(f"{e.__class__.__name__}: {e}")
            sys.exit("FAILED TO START THE BROWSER !")
        await self.load_useragents()

    async def stop(self) -> None:
        await self.browser.close()
        if self.is_active:
            await self._session.close()

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *_, **__) -> None:
        await self.stop()
