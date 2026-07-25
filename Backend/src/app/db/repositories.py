"""Async persistence helpers for conversations and messages (app schema)."""

from sqlalchemy import select

from app.db.models import Conversation, Message


async def create_conversation(session, user_sub: str, surface: str, title: str | None = None) -> Conversation:
    """Insert and return a new conversation for a user on a given surface."""
    conversation = Conversation(user_sub=user_sub, surface=surface, title=title)
    session.add(conversation)
    await session.flush()
    return conversation


async def append_message(
    session,
    conversation_id: str,
    role: str,
    content: str,
    meta: dict | None = None,
    job_id: str | None = None,
) -> Message:
    """Append a message to a conversation and return it."""
    message = Message(conversation_id=conversation_id, role=role, content=content, meta=meta, job_id=job_id)
    session.add(message)
    await session.flush()
    return message


async def list_conversations(session, user_sub: str, surface: str) -> list[Conversation]:
    """List a user's visible conversations for a surface (excludes deleted/abandoned)."""
    stmt = (
        select(Conversation)
        .where(
            Conversation.user_sub == user_sub,
            Conversation.surface == surface,
            Conversation.deleted_at.is_(None),
            Conversation.status != "abandoned",
        )
        .order_by(Conversation.updated_at.desc())
    )
    return list((await session.execute(stmt)).scalars().all())


async def list_messages(session, conversation_id: str) -> list[Message]:
    """List a conversation's messages in chronological order."""
    stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
    return list((await session.execute(stmt)).scalars().all())
