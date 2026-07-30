"""Conversation listing, messages, and graceful-exit delete/abandon."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete, select, update

from app.agent.checkpointer import reset_thread
from app.auth import AuthContext, require_auth
from app.db.base import async_session
from app.db.models import Conversation, Job, Message
from app.db.repositories import (
    ACTIVE_JOB_STATUSES,
    get_input_state,
    get_owned_conversation,
    list_conversations,
    list_messages,
)

logger = logging.getLogger(__name__)

router = APIRouter()


async def _reset_thread_quietly(thread_id: str) -> None:
    """Reset a graph thread, swallowing failures so cleanup never blocks a delete."""
    try:
        await reset_thread(thread_id)
    except Exception as error:
        logger.warning("thread reset failed for %s: %s", thread_id, error)


async def _owned_or_404(session, conversation_id: str, user_sub: str) -> Conversation:
    conversation = await get_owned_conversation(session, conversation_id, user_sub)
    if conversation is None:
        raise HTTPException(status_code=404, detail="not found")
    return conversation


@router.get("/conversations")
async def get_conversations(surface: str, auth: AuthContext = Depends(require_auth)) -> list[dict]:
    """List the user's conversations for a surface."""
    async with async_session() as session:
        rows = await list_conversations(session, auth.user_sub, surface)
        return [{"id": c.id, "title": c.title, "updated_at": c.updated_at.isoformat()} for c in rows]


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str, auth: AuthContext = Depends(require_auth)) -> dict:
    """List a conversation's messages with the state its chat input should be in."""
    async with async_session() as session:
        await _owned_or_404(session, conversation_id, auth.user_sub)
        rows = await list_messages(session, conversation_id)
        return {
            "messages": [
                {"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
                for m in rows
            ],
            "input_state": await get_input_state(session, conversation_id),
        }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, auth: AuthContext = Depends(require_auth)) -> dict:
    """Graceful-exit delete: soft-delete if a job is in flight, else hard-delete."""
    async with async_session() as session:
        await _owned_or_404(session, conversation_id, auth.user_sub)
        has_job = (
            await session.execute(
                select(Job.id)
                .where(Job.conversation_id == conversation_id, Job.status.in_(ACTIVE_JOB_STATUSES))
                .limit(1)
            )
        ).first() is not None
        if has_job:
            await session.execute(
                update(Conversation)
                .where(Conversation.id == conversation_id)
                .values(deleted_at=datetime.now(timezone.utc))
            )
        else:
            await session.execute(delete(Message).where(Message.conversation_id == conversation_id))
            await session.execute(delete(Conversation).where(Conversation.id == conversation_id))
        await session.commit()
    if not has_job:
        await _reset_thread_quietly(conversation_id)
    return {"soft_deleted": has_job}


class AbandonRequest(BaseModel):
    """Marks unconfirmed in-progress conversations abandoned on logout."""

    conversation_ids: list[str] | None = None


@router.post("/conversations/abandon")
async def abandon_conversations(body: AbandonRequest, auth: AuthContext = Depends(require_auth)) -> dict:
    """On logout, hide unconfirmed drafts without deleting messages.

    A job row exists only once the user has confirmed, so "has no job at all" is exactly
    "never confirmed". Matching on active jobs instead would abandon conversations whose
    ticket already succeeded, hiding completed reports from chat history for good.
    """
    async with async_session() as session:
        select_stmt = select(Conversation.id).where(
            Conversation.user_sub == auth.user_sub,
            Conversation.status == "active",
            Conversation.deleted_at.is_(None),
            ~Conversation.id.in_(select(Job.conversation_id)),
        )
        if body.conversation_ids:
            select_stmt = select_stmt.where(Conversation.id.in_(body.conversation_ids))
        ids = list((await session.execute(select_stmt)).scalars().all())
        if ids:
            await session.execute(
                update(Conversation).where(Conversation.id.in_(ids)).values(status="abandoned")
            )
            await session.commit()
    for conversation_id in ids:
        await _reset_thread_quietly(conversation_id)
    return {"abandoned": len(ids)}
