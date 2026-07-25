"""POST /chat/send: start or resume an agent turn; stream results over SSE."""

import uuid

from fastapi import APIRouter, Depends
from langgraph.types import Command
from pydantic import BaseModel

from app.agent.checkpointer import build_checkpointer
from app.agent.graph import build_graph, enqueue_job
from app.auth import AuthContext, require_auth
from app.db.base import async_session
from app.db.repositories import append_message, create_conversation
from app.sse.registry import registry

router = APIRouter()

_AFFIRMATIVE = {"yes", "y", "yeah", "yep", "yup", "confirm", "ok", "okay", "sure", "create", "approve", "go"}


class SendRequest(BaseModel):
    """A user's message on a given surface."""

    conversation_id: str | None = None
    surface: str
    text: str


def _is_affirmative(text: str) -> bool:
    """Interpret a free-text confirmation answer as a boolean decision."""
    normalized = text.strip().lower()
    return normalized in _AFFIRMATIVE or normalized.startswith("yes")


def _resume_value(interrupt_value: dict, text: str):
    """Shape the user's free text into the value the paused node expects.

    A gather interrupt (carrying ``missing``) resumes with a field->value dict;
    a confirm interrupt resumes with a boolean decision.
    """
    if "missing" in interrupt_value:
        missing = interrupt_value.get("missing") or []
        field = missing[0] if missing else "detail"
        return {field: text}
    return _is_affirmative(text)


def _confirm_prompt(interrupt_value: dict) -> str:
    """Author the confirmation question shown before a ticket is created."""
    dedupe_key = interrupt_value.get("dedupe_key")
    if dedupe_key:
        return f"This looks similar to {dedupe_key}. Create the ticket anyway? (yes/no)"
    return "Ready to create this ticket. Shall I go ahead? (yes/no)"


def _surface(result: dict, turn_id: str, conversation_id: str) -> tuple[dict, bool]:
    """Translate a graph result into an SSE delta and whether it reached enqueue.

    Returns the delta event to publish and a flag indicating the confirmed path
    completed (so the caller enqueues the durable creation job).
    """
    base = {"type": "delta", "turn_id": turn_id, "conversation_id": conversation_id}
    interrupts = result.get("__interrupt__")
    if interrupts:
        value = interrupts[0].value
        if "missing" in value:
            return {**base, "text": value.get("question", ""), "stage": "question"}, False
        return {**base, "text": _confirm_prompt(value), "stage": "confirm"}, False
    return {**base, "text": result.get("reply", ""), "stage": "reply"}, bool(result.get("confirmed"))


async def _start_turn(user_sub: str, conversation_id: str | None, surface: str, text: str) -> str:
    """Create the conversation if needed and persist the user message; return its id."""
    async with async_session() as session:
        if conversation_id is None:
            conversation = await create_conversation(session, user_sub, surface)
            conversation_id = conversation.id
        await append_message(session, conversation_id, "user", text)
        await session.commit()
    return conversation_id


async def _run_or_resume_graph(conversation_id: str, surface: str, user_sub: str, text: str) -> dict:
    """Run a fresh turn, or resume a paused interrupt, over the checkpointed graph.

    The graph is keyed by ``thread_id = conversation_id``. A paused thread resumes with
    the user's text (a gather answer or a confirm decision); otherwise a fresh turn starts.
    """
    async with build_checkpointer() as saver:
        graph = build_graph().compile(checkpointer=saver)
        config = {"configurable": {"thread_id": conversation_id}}
        snapshot = await graph.aget_state(config)
        if snapshot.interrupts:
            resume = _resume_value(snapshot.interrupts[0].value, text)
            return await graph.ainvoke(Command(resume=resume), config)
        return await graph.ainvoke(
            {
                "messages": [text],
                "surface": surface,
                "user_sub": user_sub,
                "conversation_id": conversation_id,
                "fields": {},
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
                "dedupe_key": result.get("dedupe_key"),
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


async def run_turn(user_sub: str, conversation_id: str | None, surface: str, text: str) -> tuple[str, str]:
    """Persist the user message, run/resume the graph, publish a delta; return ids.

    Builds the compiled graph over the Postgres checkpointer keyed by
    ``thread_id = conversation_id``. The surfaced output is persisted as an assistant
    message and pushed to the user's SSE channel; on the confirmed path a durable job
    is enqueued for the worker.
    """
    turn_id = uuid.uuid4().hex
    conversation_id = await _start_turn(user_sub, conversation_id, surface, text)
    result = await _run_or_resume_graph(conversation_id, surface, user_sub, text)

    delta, reached_enqueue = _surface(result, turn_id, conversation_id)
    if reached_enqueue:
        await _enqueue_confirmed(user_sub, conversation_id, result)
    if delta["text"]:
        await _persist_assistant(conversation_id, turn_id, delta)

    await registry.publish(user_sub, delta)
    return conversation_id, turn_id


@router.post("/chat/send")
async def chat_send(body: SendRequest, auth: AuthContext = Depends(require_auth)) -> dict:
    """Start or resume a turn and return its identifiers; results stream over /events."""
    conversation_id, turn_id = await run_turn(auth.user_sub, body.conversation_id, body.surface, body.text)
    return {"conversation_id": conversation_id, "turn_id": turn_id}
