"""Read, delivery, and retention helpers for the durable notifications feed."""

from datetime import timedelta

from sqlalchemy import delete, func, select, update

from app.db.models import Notification

RETENTION_DAYS = 30
HISTORY_LIMIT = 50


async def list_undelivered(session, user_sub: str) -> list[Notification]:
    """Return a user's notifications that have not yet reached a client, newest first.

    Delivery is tracked separately from reading so the backplane's periodic sweep falls
    silent once a toast has been shown, instead of republishing the whole unread backlog
    on every pass.
    """
    stmt = (
        select(Notification)
        .where(Notification.user_sub == user_sub, Notification.delivered_at.is_(None))
        .order_by(Notification.created_at.desc())
    )
    return list((await session.execute(stmt)).scalars().all())


async def list_history(session, user_sub: str, limit: int = HISTORY_LIMIT) -> list[Notification]:
    """Return a user's notifications inside the retention window, newest first."""
    stmt = (
        select(Notification)
        .where(
            Notification.user_sub == user_sub,
            Notification.created_at >= func.now() - timedelta(days=RETENTION_DAYS),
        )
        .order_by(Notification.created_at.desc())
        .limit(limit)
    )
    return list((await session.execute(stmt)).scalars().all())


async def mark_delivered(session, user_sub: str, ids: list[str]) -> None:
    """Record that the given notifications reached a client, scoped to the owning user."""
    if not ids:
        return
    await session.execute(
        update(Notification)
        .where(
            Notification.user_sub == user_sub,
            Notification.id.in_(ids),
            Notification.delivered_at.is_(None),
        )
        .values(delivered_at=func.now())
    )


async def mark_all_read(session, user_sub: str) -> None:
    """Mark every unread notification read for the user."""
    await session.execute(
        update(Notification)
        .where(Notification.user_sub == user_sub, Notification.read_at.is_(None))
        .values(read_at=func.now())
    )


async def purge_expired(session, days: int = RETENTION_DAYS) -> int:
    """Delete notifications past the retention window; return how many were removed.

    The cutoff is computed by the database rather than the caller so a worker container
    whose clock or timezone differs from Postgres cannot widen or narrow the window.
    """
    result = await session.execute(
        delete(Notification).where(Notification.created_at < func.now() - timedelta(days=days))
    )
    return result.rowcount or 0
