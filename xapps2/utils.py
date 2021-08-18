import asyncio
import re
from functools import partial
from typing import Any, Awaitable, Callable

APK_NAME = re.compile(r"[^A-Za-z0-9]")


def run_sync(func: Callable[..., Any]) -> Awaitable[Any]:
    """Runs the given sync function (optionally with arguments) on a separate thread."""

    async def wrapper(*args: Any, **kwargs: Any):
        return await asyncio.get_event_loop().run_in_executor(
            None, partial(func, *args, **kwargs)
        )

    return wrapper


def resolve_name(name: str) -> str:
    return "_".join(APK_NAME.sub(" ", name).split()) + ".apk"
