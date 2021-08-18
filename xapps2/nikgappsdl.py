__all__ = ["get_nikgapps"]

from typing import Iterator, Optional, Literal
import feedparser
from .config import DEVICE


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
    async for sf_link in iter_releases(android_str):
        if gapp_choice in sf_link.lower():
            dl_link = f"{sf_link}?use_mirror=autoselect"
            break
    else:
        dl_link = None
    return dl_link
