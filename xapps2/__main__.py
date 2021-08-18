import asyncio
import sys

from .main import main

if __name__ == "__main__":
    if sys.platform == "win32":
        policy = asyncio.WindowsProactorEventLoopPolicy()
    else:
        try:
            import uvloop
        except ImportError:
            policy = asyncio.DefaultEventLoopPolicy()
        else:
            policy = uvloop.EventLoopPolicy()
    asyncio.set_event_loop_policy(policy)
    asyncio.run(main())
