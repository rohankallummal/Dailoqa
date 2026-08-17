"""FastAPI application entrypoint."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import chat, conversations, events, jira_webhook, notifications
from app.db.base import async_session
from app.sse.backplane import run_listener


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start the LISTEN/NOTIFY backplane for the app's lifetime."""
    task = asyncio.create_task(run_listener(async_session))
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(title="Dailoqa Agent Backend", lifespan=lifespan)
app.include_router(events.router)
app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(notifications.router)
app.include_router(jira_webhook.router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}
