"""Execution of one agent turn, streamed to the caller over SSE."""

import logging

from langchain_core.messages import AIMessageChunk
from langgraph.types import Command

from app.agent.checkpointer import build_checkpointer
from app.agent.context import TurnContext
from app.agent.factory import build_agent
from app.db.base import async_session
from app.db.repositories import append_message
from app.sse.registry import registry

logger = logging.getLogger(__name__)

TURN_FAILED = "Something went wrong on our side. Please send that again."

_AFFIRMATIVE = {"yes", "y", "yeah", "yep", "yup", "confirm", "ok", "okay", "sure", "create", "approve", "go"}


def _is_affirmative(text: str) -> bool:
    """Interpret a free-text confirmation answer as a boolean decision."""
    normalized = text.strip().lower()
    return normalized in _AFFIRMATIVE or normalized.startswith("yes")


def _chunk_text(chunk) -> str:
    """Extract plain text from a streamed model chunk across content-block shapes."""
    content = chunk.content
    if isinstance(content, str):
        return content
    parts = [block.get("text", "") for block in content if isinstance(block, dict)]
    return "".join(parts)


def _resume_value(interrupt_value, text: str, evidence: list[dict] | None):
    """Shape the user's reply into what the suspended point expects.

    An evidence interrupt resumes with the manifest. A write gate resumes with a
    HumanInTheLoopMiddleware decision list.
    """
    if isinstance(interrupt_value, dict) and "evidence_request" in interrupt_value:
        return evidence or []
    if _is_affirmative(text):
        return [{"type": "approve"}]
    return [{"type": "reject", "message": text}]


class _TurnStream:
    """Accumulates a turn's assistant text and publishes each delta as it arrives."""

    def __init__(self, user_sub: str, conversation_id: str, turn_id: str) -> None:
        self._user_sub = user_sub
        self._base = {"type": "delta", "turn_id": turn_id, "conversation_id": conversation_id}
        self.text = ""

    async def publish(self, event: dict) -> None:
        """Send one delta to the user's subscribers."""
        await registry.publish(self._user_sub, {**self._base, **event})

    async def token(self, text: str) -> None:
        """Publish a token and remember it for the single persisted message."""
        if not text:
            return
        self.text += text
        await self.publish({"text": text, "stage": "token", "input_state": "thinking"})


def _write_summary(value) -> str:
    """Describe a pending ticket write in one line, from the args the model drafted."""
    requests = (value or {}).get("action_requests") or []
    if not requests:
        return "Shall I send this to the DailoQA development team?"
    request = requests[0]
    args = request.get("args") or {}
    if request.get("name") == "link_to_existing":
        target = args.get("issue_key") or "the existing ticket"
        return f"This looks like the same issue as {target}. Add your report to it?"
    title = str(args.get("title") or "").strip()
    if title:
        return f'Ready to file this as "{title}". Send it?'
    return "Shall I send this to the DailoQA development team?"


def _terminal(interrupts) -> tuple[str, str, str]:
    """Return the (stage, input_state, fallback_text) a turn ends in.

    The fallback text matters when the model calls a tool with no preceding prose,
    which it does often enough to matter. Both suspending tools render their own
    control, so the choice is never wholly unexplained — but the conversation turn
    above it would be empty and ``_persist`` would store nothing, leaving a
    reconnecting client an open composer over a suspended thread and no record of
    what it was being asked. The confirm line is built from the drafted arguments
    rather than fixed, so it still describes this particular report.
    """
    if not interrupts:
        return "reply", "open", ""
    value = interrupts[0].value
    if isinstance(value, dict) and "evidence_request" in value:
        return "evidence", "awaiting_evidence", str(value.get("reason") or "")
    return "confirm", "awaiting_confirm", _write_summary(value if isinstance(value, dict) else {})


async def _persist(conversation_id: str, turn_id: str, text: str, stage: str) -> None:
    """Store the turn's assistant text once, carrying the stage resync depends on.

    ``get_input_state`` reads this stage off the latest assistant message, so a turn
    that ends awaiting a choice must persist that fact or a reconnecting client will
    show an open composer over a suspended thread.
    """
    if not text.strip():
        return
    async with async_session() as session:
        await append_message(
            session, conversation_id, "assistant", text, meta={"stage": stage, "turn_id": turn_id}
        )
        await session.commit()


async def run_turn(
    user_sub: str,
    user_name: str,
    conversation_id: str,
    turn_id: str,
    surface: str,
    text: str,
    evidence: list[dict] | None = None,
    client_environment: dict | None = None,
) -> None:
    """Run or resume one turn, streaming tokens and publishing exactly one terminal event."""
    stream = _TurnStream(user_sub, conversation_id, turn_id)
    context = TurnContext(
        user_sub=user_sub,
        conversation_id=conversation_id,
        surface=surface,
        reporter_name=user_name,
        client_environment=client_environment or {},
    )
    try:
        async with build_checkpointer() as saver:
            agent = build_agent(saver, stream.publish)
            config = {"configurable": {"thread_id": conversation_id}}
            snapshot = await agent.aget_state(config)
            if snapshot.interrupts:
                payload = Command(resume=_resume_value(snapshot.interrupts[0].value, text, evidence))
            else:
                payload = {"messages": [{"role": "user", "content": text}]}
            async for mode, chunk in agent.astream(
                payload, config, context=context, stream_mode=["messages", "updates"]
            ):
                if mode == "messages":
                    message_chunk, _ = chunk
                    if isinstance(message_chunk, AIMessageChunk):
                        await stream.token(_chunk_text(message_chunk))
            final = await agent.aget_state(config)
            stage, input_state, fallback = _terminal(final.interrupts)
        trailing = "" if stream.text.strip() or not fallback else fallback
        if trailing:
            await stream.token(trailing)
        await _persist(conversation_id, turn_id, stream.text, stage)
        await stream.publish({"text": "", "stage": stage, "input_state": input_state})
    except Exception as error:
        logger.exception("turn %s failed for conversation %s: %s", turn_id, conversation_id, error)
        try:
            await _persist(conversation_id, turn_id, TURN_FAILED, "error")
        except Exception:
            logger.exception("could not persist the failure notice for turn %s", turn_id)
        await stream.publish({"text": TURN_FAILED, "stage": "error", "input_state": "open"})
