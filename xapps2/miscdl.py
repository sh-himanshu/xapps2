__all__ = ["MiscDL"]

import json
import re
from typing import Any, Dict, Iterator, List, Optional, Pattern
from bs4 import BeautifulSoup
from aiohttp.client_exceptions import ContentTypeError

from .config import DEVICE
from .nikgappsdl import get_nikgapps


class Sources:
    xda: str = "https://forum.xda-developers.com/"
    mixplorer: str = "https://raw.githubusercontent.com/code-rgb/xapps2/main/resources/mixplorer_V6.56.5-Silver-B21060540.apk"
    fdroid: str = "https://f-droid.org/"
    instander: str = "https://raw.githubusercontent.com/the-dise/the-dise.github.io/master/instander/ota.json"


class Gcam:
    headers: Dict[str, str] = {
        "upgrade-insecure-requests": "1",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "referer": "https://www.celsoazevedo.com/",
        "accept-language": "en-US,en;q=0.9",
    }
    regex: Pattern = re.compile(
        r"(?<=<a\shref=\")https://(?P<cdn>[\w-]+)\.celsoazevedo\.com/file/(?P<path>\w+/(?P<filename>[\w.-]+\.apk))(?=\">)"
    )
    cdns: Dict[str, str] = {
        "1-dontsharethislink": "7-dontsharethislink",
        "f": "temp4-f",
    }
    best: Dict[str, str] = {
        "begonia": "https://www.celsoazevedo.com/files/android/google-camera/dev-wichaya/f/dl3/"
    }


class MiscDL:
    mixplorer_regex: Pattern

    def __init__(self):
        self.mixplorer_regex = re.compile(
            r"(?<=/)attachments/mixplorer_v(?:[6-9]|\d{2,})-[\d-]+api[\w-]+-apk\.\d+"
        )
        super().__init__()

    async def _get_json(self, url: str) -> Optional[Dict]:
        async with self.http.get(url) as resp:
            if resp.status == 200:
                try:
                    return await resp.json()
                except ContentTypeError:
                    return json.loads(await resp.text())

    async def github(self, repo: str, name: str) -> Optional[str]:
        async for apk in self.iter_release_files(repo):
            if apk.get("name") == name:
                return apk.get("browser_download_url")

    async def fdroid(self, pkg_name: str) -> Optional[str]:
        if resp := await self._get_json(f"{Sources.fdroid}api/v1/packages/{pkg_name}"):
            version = resp.get("suggestedVersionCode")
            return f"{Sources.fdroid}repo/{pkg_name}_{version}.apk"

    async def mixplorer(self, varient: str = "") -> Optional[str]:
        if varient == "silver":
            return Sources.mixplorer
        async with self.http.get(f"{Sources.xda}showpost.php?p=23109280") as resp:
            assert resp.status == 200
            text = await resp.text()
        if match := self.mixplorer_regex.search(text):
            return f"{Sources.xda}{match.group(0)}"

    async def json_api(self, link: str, args: List[str]) -> Optional[str]:
        if resp := await self._get_json(link):
            while len(args) != 0:
                try:
                    resp = resp[args.pop(0)]
                except (IndexError, KeyError):
                    return
            return resp

    async def instander(self) -> Optional[str]:
        async with self.http.get(Sources.instander) as resp:
            assert resp.status == 200
            text = await resp.text()
            return json.loads(text).get("link")

    async def iter_release_files(self, repo: str) -> Iterator[Any]:
        if resp := (
            await self._get_json(f"https://api.github.com/repos/{repo}/releases/latest")
        ):
            for k in resp.get("assets"):
                yield k

    async def nekox(self, varient: str = "mini") -> Optional[str]:
        return await self.github(
            "NekoX-Dev/NekoX", f"NekoX-{varient}-{DEVICE.arch}-release.apk"
        )

    async def nikgapps(self, varient: str = "basic") -> Optional[str]:
        if DEVICE.arch != "arm64-v8a":
            return
        if file := await get_nikgapps(DEVICE.android_str, varient):
            async with self.http.get(
                f"https://sourceforge.net/settings/mirror_choices?projectname=nikgapps&filename={file}"
            ) as resp:
                assert resp.status == 200
                text = await resp.text()
                for mirror in (
                    BeautifulSoup(text, "html.parser")
                    .find("ul", {"id": "mirrorList"})
                    .find_all("li")
                ):
                    mirror_id = mirror.get("id")
                    if mirror_id and (mirror_id not in ("autoselect", "udomain")):
                        return f"https://{mirror_id}.dl.sourceforge.net/project/nikgapps/{file}"

    async def gcam(self, *args: Any) -> Optional[str]:
        if not args:
            return

        arg1 = args[0].strip()
        if arg1 == "best":
            gcam_link = Gcam.best.get(DEVICE.codename)
        elif arg1.startswith("https://"):
            gcam_link = arg1

        if not gcam_link:
            return

        async with self.http.get(gcam_link) as resp:
            assert resp.status == 200
            text = await resp.text()
        if match := Gcam.regex.search(text):
            cdn = match.group("cdn")
            if cdn in Gcam.cdns:
                return f"https://{Gcam.cdns[cdn]}.celsoazevedo.com/file/{match.group('path')}"

            async with self.http.get(
                match.group(0),
                allow_redirects=True,
                headers={
                    "authority": f"{cdn}.celsoazevedo.com",
                    "User-Agent": self.ua,
                    **Gcam.headers,
                },
            ) as response:
                return response.url
