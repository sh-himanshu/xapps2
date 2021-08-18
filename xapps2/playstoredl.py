__all__ = ["PlayStoreDL"]

import asyncio
import logging
from typing import Dict, Optional, Union
from urllib.parse import urlencode

import pyppeteer

from .config import DEVICE

LOG = logging.getLogger(__name__)


class PlayStoreDL:
    dl_site: str
    params: Dict[str, Union[str, int]]

    def __init__(self):
        self.dl_site = "https://apkcombo.com/en-in/apk-downloader"
        self.params = {
            "device": "phone",
            "arches": DEVICE.arch,
            "sdkInt": DEVICE.sdk,
            "expanded": "1",
            "format": "apk",
            "dpi": DEVICE.dpi,
            "lang": "en",
        }

    async def _playstore_fetch(self, package_name: str) -> Optional[str]:
        page = await self.browser.newPage()
        await page.setUserAgent(self.ua.random)
        url = f"{self.dl_site}?{urlencode({'package': package_name.strip(), **self.params})}"
        await page.goto(url)
        element = None
        try_count = 0
        while not element:
            if try_count >= 8:
                await page.screenshot(path="error.png", fullPage=True)
                return
            try_count += 1
            await asyncio.sleep(5)
            element = await page.querySelector("ul.file-list a.variant")
            LOG.info(f"Waiting for 5s for page to load")
        try:
            downlink = await page.evaluate("(el) => el.href", element)
        except pyppeteer.errors.ElementHandleError:
            LOG.error(f"Failed to GET [{url}]")
            await page.screenshot(path="error.png", fullPage=True)
        else:
            return downlink

    async def playstore(self, package_name: str) -> Optional[str]:
        try_count = 0
        dl_link = None
        while not dl_link:
            try_count += 1
            LOG.info(f"Trying to connect to server: {try_count}")
            if try_count >= 8:
                break
            try:
                dl_link = await self._playstore_fetch(package_name)
            except Exception as e:
                LOG.exception(f"{e.__class__.__name__}: {e}")
            else:
                break
            # except pyppeteer.errors.PageError:
            #     pass

        if dl_link:
            return dl_link
        LOG.debug(f"Failed to fetch {package_name}\nskipping ...")
