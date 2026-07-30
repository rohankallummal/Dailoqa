"""Single per-tab SSE channel: agent deltas + notifications."""

import asyncio
import json
import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.auth import AuthContext, require_auth
from app.db.base import async_session
from app.sse.backplane import push_undelivered_to_user
from app.sse.registry import registry

logger = logging.getLogger(__name__)

router = APIRouter()

_HEARTBEAT_SECONDS = 15


def _frame(event: dict, event_id: int) -> str:
    """Render an event dict as an SSE frame carrying an id for Last-Event-ID."""
    return f"id: {event_id}\ndata: {json.dumps(event)}\n\n"


@router.get("/events")
async def events(request: Request, auth: AuthContext = Depends(require_auth)) -> StreamingResponse:
    """Stream agent deltas and notifications for the authenticated user."""
    subscriber = registry.subscribe(auth.user_sub)
    try:
        await push_undelivered_to_user(async_session, auth.user_sub)
    except Exception as error:
        logger.warning("on-connect undelivered read failed for %s: %s", auth.user_sub, error)

    async def gen():
        event_id = 0
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(subscriber.get(), timeout=_HEARTBEAT_SECONDS)
                    event_id += 1
                    yield _frame(event, event_id)
                except asyncio.TimeoutError:
                    yield ": heartbeat\n\n"
        finally:
            registry.unsubscribe(auth.user_sub, subscriber)

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
