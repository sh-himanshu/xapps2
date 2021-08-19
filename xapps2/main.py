__all__ = ["main"]

import asyncio
import logging
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
        except Exception:
            LOG.exception(f"Failed to Downoad '{file_name}'")


async def main():

    async with ApkDL() as apk_dl:

        with open("config.yaml", "r") as f:
            apps_conf = yaml.load(f, Loader=yaml.FullLoader)

        tasks: List = []

        sem = asyncio.Semaphore(4)

        for addon in apps_conf["addons"]:
            addon_split = addon.split("@", 1)
            if func := getattr(apk_dl, addon_split[0], None):
                filename = "_".join(addon_split) + (
                    ".zip" if addon_split[0] == "nikgapps" else ".apk"
                )
                tasks.append(
                    (
                        filename,
                        sem,
                        func(*addon_split[1:]),
                    )
                )

        for app in apps_conf["custom"]:
            apk_name = resolve_name(app["app"])
            source = app["source"]
            if source in ("fdroid", "playstore"):
                tasks.append((apk_name, sem, getattr(apk_dl, source)(app["package"])))
            elif source in ("github", "gcam"):
                tasks.append((apk_name, sem, getattr(apk_dl, source)(*app["args"])))

        urls = await asyncio.gather(*map(lambda x: limit_coro(*x), tasks))

        with open("apk_urls.txt", "w") as outfile:
            outfile.write("\n".join(filter(None, urls)))
