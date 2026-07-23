"""Entrypoint: python -m app.worker starts the queue drain loop."""

import asyncio

from app.worker.runner import run_forever

if __name__ == "__main__":
    asyncio.run(run_forever())
