"""Notifications listing and mark-read."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth import AuthContext, require_auth
from app.db.base import async_session
from app.db.notifications import list_unread, mark_read

router = APIRouter()


@router.get("/notifications")
async def get_notifications(auth: AuthContext = Depends(require_auth)) -> list[dict]:
    """Return the user's unread notifications."""
    async with async_session() as session:
        rows = await list_unread(session, auth.user_sub)
        return [{"id": n.id, "type": n.type, "title": n.title, "body": n.body, "jira_key": n.jira_key} for n in rows]


class MarkReadRequest(BaseModel):
    """Notification ids to mark read."""

    ids: list[str]


@router.post("/notifications/mark-read")
async def post_mark_read(body: MarkReadRequest, auth: AuthContext = Depends(require_auth)) -> dict:
    """Mark the given notifications read for the user."""
    async with async_session() as session:
        await mark_read(session, auth.user_sub, body.ids)
        await session.commit()
    return {"ok": True}
