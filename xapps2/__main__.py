import asyncio
import sys

from .main import main

if __name__ == "__main__":
    if sys.platform == "win32":
        policy = asyncio.WindowsProactorEventLoopPolicy()
        asyncio.set_event_loop_policy(policy)
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(main())
            # https://github.com/encode/httpx/issues/914
            loop.run_until_complete(asyncio.sleep(1))
        finally:
            loop.close()
    else:
        try:
            import uvloop
        except ImportError:
            policy = asyncio.DefaultEventLoopPolicy()
        else:
            policy = uvloop.EventLoopPolicy()
        asyncio.set_event_loop_policy(policy)
        asyncio.run(main())
