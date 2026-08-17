"""Conversation listing, messages, and graceful-exit delete/cleanup."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete, update

from app.agent.checkpointer import reset_thread
from app.auth import AuthContext, require_auth
from app.db.base import async_session
from app.db.models import Conversation, Message
from app.db.repositories import (
    get_input_state,
    get_owned_conversation,
    has_active_job,
    list_conversations,
    list_messages,
    list_unfinished_conversation_ids,
)

logger = logging.getLogger(__name__)

router = APIRouter()


async def _reset_thread_quietly(thread_id: str) -> None:
    """Reset a graph thread, swallowing failures so cleanup never blocks a delete."""
    try:
        await reset_thread(thread_id)
    except Exception as error:
        logger.warning("thread reset failed for %s: %s", thread_id, error)


async def owned_or_404(session, conversation_id: str, user_sub: str) -> Conversation:
    """Return the caller's conversation, or reject the id as a 404.

    Every entry point that takes a caller-supplied conversation id goes through this. The
    agent is keyed by ``thread_id = conversation_id``, so without it an attacker could
    append to, resume, and confirm a paused thread belonging to someone else.
    """
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
        await owned_or_404(session, conversation_id, auth.user_sub)
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
        await owned_or_404(session, conversation_id, auth.user_sub)
        has_job = await has_active_job(session, conversation_id)
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


class CleanupRequest(BaseModel):
    """Discards conversations left at an unanswered agent prompt on logout."""

    conversation_ids: list[str] | None = None


@router.post("/conversations/cleanup")
async def cleanup_conversations(body: CleanupRequest, auth: AuthContext = Depends(require_auth)) -> dict:
    """On logout, delete reports the agent was mid-way through collecting.

    Only a conversation still waiting on an evidence upload or a confirmation choice is a
    draft. Everything that reached a plain reply is kept, whether it filed a ticket, linked
    to one, or told the user they had already reported the issue.

    A draft is deleted outright rather than flagged. Flagging leaves the owner data they
    cannot list, read, or delete, and no chore ever sweeps it, so the rows accumulate for
    the life of the deployment. The messages go with the conversation, the graph thread is
    reset, and the evidence directory falls to the worker's orphan sweep.
    """
    async with async_session() as session:
        ids = await list_unfinished_conversation_ids(session, auth.user_sub, body.conversation_ids)
        if ids:
            await session.execute(delete(Message).where(Message.conversation_id.in_(ids)))
            await session.execute(delete(Conversation).where(Conversation.id.in_(ids)))
            await session.commit()
    for conversation_id in ids:
        await _reset_thread_quietly(conversation_id)
    return {"deleted": len(ids)}
