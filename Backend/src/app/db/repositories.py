"""Async persistence helpers for conversations and messages (app schema)."""

from sqlalchemy import select

from app.db.models import Conversation, Job, Message, Ticket, TicketReporter

ACTIVE_JOB_STATUSES = ("queued", "running")

INTERRUPT_STATES = {"confirm": "awaiting_confirm", "evidence": "awaiting_evidence"}


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


async def get_owned_conversation(session, conversation_id: str, user_sub: str) -> Conversation | None:
    """Return the conversation only when it exists and belongs to user_sub, else None.

    Every entry point that accepts a caller-supplied conversation id goes through this,
    so one user can never read, append to, or resume another user's thread.
    """
    conversation = (
        await session.execute(select(Conversation).where(Conversation.id == conversation_id))
    ).scalar_one_or_none()
    if conversation is None or conversation.user_sub != user_sub:
        return None
    return conversation


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


def _latest_assistant_stage():
    """Correlated subquery yielding a conversation's most recent assistant message stage."""
    return (
        select(Message.meta["stage"].astext)
        .where(Message.conversation_id == Conversation.id, Message.role == "assistant")
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(1)
        .correlate(Conversation)
        .scalar_subquery()
    )


async def list_unfinished_conversation_ids(
    session, user_sub: str, conversation_ids: list[str] | None = None
) -> list[str]:
    """List conversations the agent is still waiting on the user to answer.

    A conversation is unfinished only while it sits at an unanswered evidence or
    confirmation prompt with no job ever enqueued. One that reached a plain reply is
    finished and belongs in history, however it ended: the duplicate-detection path
    deliberately enqueues no job, so treating "has no job" as "never confirmed" hid every
    completed duplicate report from chat history permanently.
    """
    stmt = select(Conversation.id).where(
        Conversation.user_sub == user_sub,
        Conversation.status == "active",
        Conversation.deleted_at.is_(None),
        ~Conversation.id.in_(select(Job.conversation_id)),
        _latest_assistant_stage().in_(tuple(INTERRUPT_STATES)),
    )
    if conversation_ids:
        stmt = stmt.where(Conversation.id.in_(conversation_ids))
    return list((await session.execute(stmt)).scalars().all())


async def list_messages(session, conversation_id: str) -> list[Message]:
    """List a conversation's messages in chronological order."""
    stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
    return list((await session.execute(stmt)).scalars().all())


async def list_evidence_holding_conversation_ids(session) -> frozenset[str]:
    """Return ids of conversations whose evidence the orphan sweep must not delete.

    Two groups qualify. A conversation that is still active and not deleted can be
    returned to, so an open evidence or confirmation prompt is still resumable. A
    conversation with a queued or running job has evidence the worker has not uploaded
    yet. Everything else -- deleted, or abandoned on logout -- is the sweep's business.
    """
    active = await session.execute(
        select(Conversation.id).where(
            Conversation.status == "active",
            Conversation.deleted_at.is_(None),
        )
    )
    pending = await session.execute(
        select(Job.conversation_id).where(Job.status.in_(ACTIVE_JOB_STATUSES))
    )
    return frozenset(active.scalars().all()) | frozenset(pending.scalars().all())


async def has_active_job(session, conversation_id: str) -> bool:
    """Report whether a queued or running job is holding this conversation."""
    row = (
        await session.execute(
            select(Job.id)
            .where(Job.conversation_id == conversation_id, Job.status.in_(ACTIVE_JOB_STATUSES))
            .limit(1)
        )
    ).first()
    return row is not None


async def get_input_state(session, conversation_id: str) -> str:
    """Derive whether the chat input is open, collecting evidence, awaiting a confirmation choice, or locked.

    A job still in flight outranks everything: the confirmed turn writes no message, so
    the confirmation prompt remains the latest assistant message while the worker runs.
    """
    if await has_active_job(session, conversation_id):
        return "pending"

    latest = (
        await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id, Message.role == "assistant")
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if latest is None:
        return "open"
    return INTERRUPT_STATES.get((latest.meta or {}).get("stage"), "open")


async def set_conversation_title(session, conversation_id: str, title: str) -> None:
    """Set a conversation's title; no-op if it was deleted in the meantime."""
    conversation = await session.get(Conversation, conversation_id)
    if conversation is not None:
        conversation.title = title


async def reported_issue_keys(session, user_sub: str, jira_keys: list[str]) -> frozenset[str]:
    """Return which of the given Jira keys this user is already recorded against.

    A ticket_reporters row is written once per (ticket, reporter) and is what generates both
    the Similar Reports spreadsheet and the Reported By section, so it answers "has this user
    already reported this" without reading either artifact back out of Jira.

    Callers pass candidates the JQL has already narrowed to open issues, so a closed ticket
    never reaches this query and a regression is free to file as a new report.
    """
    if not jira_keys:
        return frozenset()
    stmt = (
        select(Ticket.jira_key)
        .join(TicketReporter, TicketReporter.ticket_id == Ticket.id)
        .where(TicketReporter.user_sub == user_sub, Ticket.jira_key.in_(jira_keys))
    )
    return frozenset((await session.execute(stmt)).scalars().all())
