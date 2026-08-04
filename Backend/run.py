"""Local dev server.

On Windows psycopg's async mode rejects the ProactorEventLoop that Python installs by
default, and ``uvicorn.run()`` builds its own loop that ignores a pre-set policy — so the
server is driven directly on a SelectorEventLoop instead. Logging is turned up to INFO so
retrieval decisions (``rag.search``, ``rag.grounding``) are visible while you use the app.

    python run.py
"""

import asyncio
import logging
import sys

from uvicorn import Config, Server


def main() -> None:
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    config = Config("app.main:app", host="127.0.0.1", port=8000, loop="asyncio")
    asyncio.run(Server(config).serve())


if __name__ == "__main__":
    main()
