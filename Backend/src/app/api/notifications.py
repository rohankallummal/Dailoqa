"""Notifications listing, delivery acknowledgement, and mark-read."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth import AuthContext, require_auth
from app.db.base import async_session
from app.db.notifications import list_history, list_undelivered, mark_all_read, mark_delivered

router = APIRouter()


def _serialize(notification) -> dict:
    """Render a notification for the client."""
    return {
        "id": notification.id,
        "type": notification.type,
        "title": notification.title,
        "body": notification.body,
        "jira_key": notification.jira_key,
        "conversation_id": notification.conversation_id,
        "read_at": notification.read_at.isoformat() if notification.read_at else None,
        "created_at": notification.created_at.isoformat() if notification.created_at else None,
    }


@router.get("/notifications")
async def get_notifications(auth: AuthContext = Depends(require_auth)) -> list[dict]:
    """Return the notifications still awaiting delivery to a client."""
    async with async_session() as session:
        rows = await list_undelivered(session, auth.user_sub)
        return [_serialize(row) for row in rows]


@router.get("/notifications/history")
async def get_notification_history(auth: AuthContext = Depends(require_auth)) -> list[dict]:
    """Return the user's notifications inside the retention window, newest first."""
    async with async_session() as session:
        rows = await list_history(session, auth.user_sub)
        return [_serialize(row) for row in rows]


class MarkDeliveredRequest(BaseModel):
    """Notification ids that reached the client."""

    ids: list[str]


@router.post("/notifications/mark-delivered")
async def post_mark_delivered(body: MarkDeliveredRequest, auth: AuthContext = Depends(require_auth)) -> dict:
    """Record that the given notifications reached the user's client."""
    async with async_session() as session:
        await mark_delivered(session, auth.user_sub, body.ids)
        await session.commit()
    return {"ok": True}


@router.post("/notifications/mark-all-read")
async def post_mark_all_read(auth: AuthContext = Depends(require_auth)) -> dict:
    """Mark every unread notification read for the user."""
    async with async_session() as session:
        await mark_all_read(session, auth.user_sub)
        await session.commit()
    return {"ok": True}
