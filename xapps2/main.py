__all__ = ["main"]

from typing import List, Optional
import yaml
from .apkdl import ApkDL
import re
import asyncio
from .utils import resolve_name

sem = asyncio.Semaphore(8)


async def limit_coro(file_name: str, coro) -> Optional[str]:
    async with sem:
        if res := await coro:
            return f"{file_name}|{res}"


async def main():
    re.compile(r"[^A-Za-z0-9]")
    async with ApkDL() as apk_dl:

        with open("config.yaml", "r") as f:
            apps_conf = yaml.load(f, Loader=yaml.FullLoader)

        tasks: List = []
        for addon in apps_conf["addons"]:
            if func := getattr(apk_dl, addon, None):
                file_ext = ".zip" if "nikgapps" in addon else ".apk"
                tasks.append((addon + file_ext, func(*addon.split("@", 1))))

        for app in apps_conf["custom"]:
            apk_name = resolve_name(app["app"])
            source = app["source"]
            if source == "fdroid":
                tasks.append((apk_name, apk_dl.fdroid(app["package"])))
            elif source == "github":
                tasks.append((apk_name, apk_dl.github(*app["args"])))
            elif source == "playstore":
                tasks.append((apk_name, apk_dl.playstore(app["package"])))

        urls = await asyncio.gather(*map(lambda x: limit_coro(*x), tasks))

        with open("apk_urls.txt", "w") as outfile:
            outfile.write("\n".join(filter(None, urls)))
