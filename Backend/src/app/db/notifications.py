"""Read/mark-read helpers for the durable notifications feed."""

from datetime import datetime, timezone

from sqlalchemy import select, update

from app.db.models import Notification


async def list_unread(session, user_sub: str) -> list[Notification]:
    """Return a user's unread notifications, newest first."""
    stmt = (
        select(Notification)
        .where(Notification.user_sub == user_sub, Notification.read_at.is_(None))
        .order_by(Notification.created_at.desc())
    )
    return list((await session.execute(stmt)).scalars().all())


async def mark_read(session, user_sub: str, ids: list[str]) -> None:
    """Mark the given notifications read, scoped to the owning user."""
    if not ids:
        return
    await session.execute(
        update(Notification)
        .where(Notification.user_sub == user_sub, Notification.id.in_(ids))
        .values(read_at=datetime.now(timezone.utc))
    )
