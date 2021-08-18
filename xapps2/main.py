__all__ = ["main"]

import asyncio
import logging
import re
from typing import Coroutine, List, Optional

import yaml

from .apkdl import ApkDL
from .utils import resolve_name

LOG = logging.getLogger(__name__)


async def limit_coro(
    file_name: str, sem: asyncio.Semaphore, coro: Coroutine
) -> Optional[str]:
    async with sem:
        try:
            if res := await coro:
                return f"{file_name}|{res}"
        except Exception as e:
            LOG.error(f"{e.__class__.__name__}: {e}")


async def main():
    re.compile(r"[^A-Za-z0-9]")
    async with ApkDL() as apk_dl:

        with open("config.yaml", "r") as f:
            apps_conf = yaml.load(f, Loader=yaml.FullLoader)

        tasks: List = []

        sem = asyncio.Semaphore(8)

        for addon in apps_conf["addons"]:
            if func := getattr(apk_dl, addon, None):
                file_ext = ".zip" if "nikgapps" in addon else ".apk"
                tasks.append(
                    (
                        addon.replace("@", "_") + file_ext,
                        sem,
                        func(*addon.split("@", 1)[1:]),
                    )
                )

        for app in apps_conf["custom"]:
            apk_name = resolve_name(app["app"])
            source = app["source"]
            if source in ("fdroid", "playstore"):
                tasks.append((apk_name, sem, getattr(apk_dl, source)(app["package"])))
            elif source == "github":
                tasks.append((apk_name, sem, apk_dl.github(*app["args"])))

        urls = await asyncio.gather(*map(lambda x: limit_coro(*x), tasks))

        with open("apk_urls.txt", "w") as outfile:
            outfile.write("\n".join(filter(None, urls)))
