"""Durable result delivery: notification row, optional chat message, and a wake hint."""

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert

from app.db.models import Conversation, Message, Notification


async def deliver_result(session, job, notif_type: str, title: str, body: str, jira_key: str | None) -> None:
    """Write a notification (idempotent per job), append a chat message if the
    conversation still exists, then pg_notify the user's channel.
    """
    await session.execute(
        insert(Notification)
        .values(
            user_sub=job.user_sub,
            conversation_id=job.conversation_id,
            type=notif_type,
            title=title,
            body=body,
            jira_key=jira_key,
            job_id=job.id,
        )
        .on_conflict_do_nothing(index_elements=["job_id"])
    )
    conversation = (
        await session.execute(select(Conversation).where(Conversation.id == job.conversation_id))
    ).scalar_one_or_none()
    if conversation is not None and conversation.deleted_at is None:
        await session.execute(
            insert(Message)
            .values(conversation_id=job.conversation_id, role="assistant", content=body, job_id=job.id)
            .on_conflict_do_nothing(index_elements=["job_id"])
        )
    await session.execute(text("SELECT pg_notify('notifications', :payload)"), {"payload": job.user_sub})
