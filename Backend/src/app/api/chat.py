"""POST /chat/send: start or resume an agent turn; stream results over SSE."""

import asyncio
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from langgraph.types import Command
from pydantic import BaseModel

from app import messages
from app.agent.checkpointer import build_checkpointer
from app.agent.graph import build_graph, enqueue_job
from app.agent.title import generate_title
from app.auth import AuthContext, require_auth
from app.db.base import async_session
from app.evidence.storage import normalize_manifest, validate_manifest
from app.db.repositories import (
    append_message,
    create_conversation,
    get_owned_conversation,
    set_conversation_title,
)
from app.sse.registry import registry

router = APIRouter()

logger = logging.getLogger(__name__)

_title_tasks: set = set()


def _schedule_title(conversation_id: str, first_message: str) -> None:
    """Fire-and-forget: generate and persist a title without blocking the turn."""
    task = asyncio.create_task(_generate_and_store_title(conversation_id, first_message))
    _title_tasks.add(task)
    task.add_done_callback(_title_tasks.discard)


async def _generate_and_store_title(conversation_id: str, first_message: str) -> None:
    """Generate a title for a new conversation and store it, swallowing failures."""
    try:
        title = await generate_title(first_message)
        if not title:
            return
        async with async_session() as session:
            await set_conversation_title(session, conversation_id, title)
            await session.commit()
    except Exception as error:
        logger.warning("title generation failed for %s: %s", conversation_id, error)


_AFFIRMATIVE = {"yes", "y", "yeah", "yep", "yup", "confirm", "ok", "okay", "sure", "create", "approve", "go"}


class EvidenceFile(BaseModel):
    """One uploaded evidence file, as reported by the frontend."""

    name: str
    category: str
    size: int


class SendRequest(BaseModel):
    """A user's message on a given surface, optionally carrying an evidence manifest."""

    conversation_id: str | None = None
    surface: str
    text: str
    evidence: list[EvidenceFile] | None = None


def _is_affirmative(text: str) -> bool:
    """Interpret a free-text confirmation answer as a boolean decision."""
    normalized = text.strip().lower()
    return normalized in _AFFIRMATIVE or normalized.startswith("yes")


def _resume_value(interrupt_value: dict, text: str, evidence: list[dict] | None):
    """Shape the user's reply into the value the paused node expects.

    An evidence interrupt resumes with the manifest (an empty list means Cancel); a
    gather interrupt (carrying ``missing``) resumes with a field->value dict; a confirm
    interrupt resumes with a boolean decision.
    """
    if "evidence_request" in interrupt_value:
        return evidence or []
    if "missing" in interrupt_value:
        missing = interrupt_value.get("missing") or []
        field = missing[0] if missing else "detail"
        return {field: text}
    return _is_affirmative(text)


def _confirm_prompt(interrupt_value: dict) -> str:
    """Return the fixed confirmation question for the kind being reported."""
    return messages.confirmation_for(interrupt_value["kind"])


def _surface(result: dict, turn_id: str, conversation_id: str) -> tuple[dict, bool]:
    """Translate a graph result into an SSE delta and whether it reached enqueue.

    Returns the delta event to publish and a flag indicating the confirmed path
    completed (so the caller enqueues the durable creation job). The delta carries
    the input state this turn leaves the conversation in: awaiting a confirmation
    choice, locked pending the worker, or open for typing.
    """
    base = {"type": "delta", "turn_id": turn_id, "conversation_id": conversation_id}
    interrupts = result.get("__interrupt__")
    if interrupts:
        value = interrupts[0].value
        if "evidence_request" in value:
            return {
                **base,
                "text": messages.EVIDENCE_REQUEST,
                "stage": "evidence",
                "input_state": "awaiting_evidence",
            }, False
        if "missing" in value:
            return {**base, "text": value.get("question", ""), "stage": "question", "input_state": "open"}, False
        return {**base, "text": _confirm_prompt(value), "stage": "confirm", "input_state": "awaiting_confirm"}, False
    reached_enqueue = bool(result.get("confirmed"))
    input_state = "pending" if reached_enqueue else "open"
    return {**base, "text": result.get("reply", ""), "stage": "reply", "input_state": input_state}, reached_enqueue


async def _require_owned(conversation_id: str, user_sub: str) -> None:
    """Reject a conversation id the caller does not own, as a 404.

    The graph is keyed by ``thread_id = conversation_id``, so without this an attacker
    could append to, resume, and confirm a paused thread belonging to someone else.
    """
    async with async_session() as session:
        if await get_owned_conversation(session, conversation_id, user_sub) is None:
            raise HTTPException(status_code=404, detail="not found")


async def _start_turn(user_sub: str, conversation_id: str | None, surface: str, text: str) -> str:
    """Create the conversation if needed and persist the user message; return its id."""
    async with async_session() as session:
        if conversation_id is None:
            conversation = await create_conversation(session, user_sub, surface)
            conversation_id = conversation.id
        await append_message(session, conversation_id, "user", text)
        await session.commit()
    return conversation_id


async def _run_or_resume_graph(
    conversation_id: str, surface: str, user_sub: str, text: str, evidence: list[dict] | None = None
) -> dict:
    """Run a fresh turn, or resume a paused interrupt, over the checkpointed graph.

    The graph is keyed by ``thread_id = conversation_id``. A paused thread resumes with
    the user's reply (an evidence manifest, a gather answer, or a confirm decision);
    otherwise a fresh turn starts.

    ``confirmed`` is reset explicitly on a fresh turn. It has no reducer, so a value left
    in the checkpoint by an earlier confirmed report would otherwise still be true on the
    next unrelated message and enqueue a second job with an empty payload.
    """
    async with build_checkpointer() as saver:
        graph = build_graph().compile(checkpointer=saver)
        config = {"configurable": {"thread_id": conversation_id}}
        snapshot = await graph.aget_state(config)
        if snapshot.interrupts:
            resume = _resume_value(snapshot.interrupts[0].value, text, evidence)
            return await graph.ainvoke(Command(resume=resume), config)
        return await graph.ainvoke(
            {
                "messages": [text],
                "surface": surface,
                "user_sub": user_sub,
                "conversation_id": conversation_id,
                "fields": {},
                "confirmed": False,
            },
            config,
        )


async def _enqueue_confirmed(user_sub: str, conversation_id: str, result: dict) -> None:
    """Enqueue the durable ticket-creation job for a confirmed turn."""
    async with async_session() as session:
        await enqueue_job(
            session,
            {
                "user_sub": user_sub,
                "conversation_id": conversation_id,
                "kind": result.get("kind"),
                "fields": result.get("fields", {}),
                "confirmed": True,
            },
        )
        await session.commit()


async def _persist_assistant(conversation_id: str, turn_id: str, delta: dict) -> None:
    """Persist a surfaced assistant delta as a chat message."""
    async with async_session() as session:
        await append_message(
            session,
            conversation_id,
            "assistant",
            delta["text"],
            meta={"stage": delta["stage"], "turn_id": turn_id},
        )
        await session.commit()


async def run_turn(
    user_sub: str,
    conversation_id: str | None,
    surface: str,
    text: str,
    evidence: list[dict] | None = None,
) -> tuple[str, str, str]:
    """Persist the user message, run/resume the graph, publish a delta; return ids and input state.

    Builds the compiled graph over the Postgres checkpointer keyed by
    ``thread_id = conversation_id``. The surfaced output is persisted as an assistant
    message and pushed to the user's SSE channel; on the confirmed path a durable job
    is enqueued for the worker.
    """
    turn_id = uuid.uuid4().hex
    is_new = conversation_id is None
    conversation_id = await _start_turn(user_sub, conversation_id, surface, text)
    result = await _run_or_resume_graph(conversation_id, surface, user_sub, text, evidence)

    delta, reached_enqueue = _surface(result, turn_id, conversation_id)
    if reached_enqueue:
        await _enqueue_confirmed(user_sub, conversation_id, result)
    if delta["text"]:
        await _persist_assistant(conversation_id, turn_id, delta)

    await registry.publish(user_sub, delta)
    if is_new:
        _schedule_title(conversation_id, text)
    return conversation_id, turn_id, delta["input_state"]


@router.post("/chat/send")
async def chat_send(body: SendRequest, auth: AuthContext = Depends(require_auth)) -> dict:
    """Start or resume a turn and return its identifiers; results stream over /events.

    An existing conversation must belong to the caller. An evidence manifest is verified
    against the files on disk before the graph is resumed, so a rejection leaves the
    interrupt unconsumed and the card still shown.
    """
    if body.conversation_id is not None:
        await _require_owned(body.conversation_id, auth.user_sub)
    manifest = [file.model_dump() for file in body.evidence] if body.evidence else None
    if manifest:
        if body.conversation_id is None:
            raise HTTPException(status_code=400, detail="evidence requires an existing conversation")
        errors = validate_manifest(auth.user_sub, body.conversation_id, manifest)
        if errors:
            raise HTTPException(status_code=400, detail={"errors": errors})
        manifest = normalize_manifest(auth.user_sub, body.conversation_id, manifest)
    conversation_id, turn_id, input_state = await run_turn(
        auth.user_sub, body.conversation_id, body.surface, body.text, manifest
    )
    return {"conversation_id": conversation_id, "turn_id": turn_id, "input_state": input_state}
