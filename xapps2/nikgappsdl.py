__all__ = ["get_nikgapps"]

import re
from typing import Iterator, Literal, Optional

import feedparser


async def iter_releases(android_str: str) -> Iterator[str]:
    for entry in feedparser.parse(
        f"https://sourceforge.net/projects/nikgapps/rss?path=/Releases/NikGapps-{android_str}"
    ).entries:
        yield entry.link


async def get_nikgapps(
    android_str: Literal["P", "Q", "R", "S"],
    varient: Literal["full", "stock", "basic", "omni", "core", "go"],
) -> Optional[str]:
    arch = "arm64"  # Niksgapps has only arm64 varient
    gapp_choice = (f"nikgapps-{varient}-{arch}").lower()
    print("Searching Gapps")
    async for sf_link in iter_releases(android_str):
        if gapp_choice in sf_link.lower():
            break
    else:
        return
    if match := re.match(
        "https://sourceforge\.net/projects/nikgapps/files/(?P<file>\S+\.zip)(?:/download)?",
        sf_link,
    ):

        return f"https://sourceforge.net/settings/mirror_choices?projectname=nikgapps&filename={match.group('file')}"
    print("no Gapps found")
