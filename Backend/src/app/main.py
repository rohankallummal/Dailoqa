"""FastAPI application entrypoint."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from app.api import chat, conversations, events, jira_webhook, notifications
from app.auth import AuthContext, require_auth
from app.db.base import async_session
from app.sse.backplane import run_listener

# Running natively on Windows needs a selector event loop or the LISTEN/NOTIFY backplane dies at
# startup; see app/loop.py. It cannot be fixed from here -- uvicorn picks its loop from a
# hardcoded factory, not the event loop policy, so a set_event_loop_policy call in this module is
# ignored. Pass `--loop app.loop:selector_event_loop` (or `--reload`) instead.


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


@app.get("/me")
async def me(auth: AuthContext = Depends(require_auth)) -> dict[str, str]:
    """Return the identity derived from the caller's service JWT."""
    return {"user_sub": auth.user_sub, "user_id": auth.user_id}
