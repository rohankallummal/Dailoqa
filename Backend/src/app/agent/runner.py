"""Execution of one agent turn, streamed to the caller over SSE."""

import logging

from langchain_core.messages import AIMessageChunk
from langgraph.types import Command

from app.agent.checkpointer import build_checkpointer
from app.agent.context import TurnContext
from app.agent.factory import build_agent
from app.db.base import async_session
from app.db.repositories import append_message, has_active_job
from app.llm import is_unavailable
from app.sse.registry import registry

logger = logging.getLogger(__name__)

TURN_FAILED = "Something went wrong on our side. Please send that again."
SERVICE_UNAVAILABLE = "Unable to connect to the service right now. Please try again in a few minutes."
CONFIRM_WRITE = "Shall I send this to the DailoQA development team?"

_AFFIRMATIVE = {"yes", "y", "yeah", "yep", "yup", "confirm", "ok", "okay", "sure", "create", "approve", "go"}

DECLINED = (
    "Not filed. Nothing was sent to the team and no ticket exists. The user was asked to "
    "confirm and declined, saying: {message}. Do not tell them it was recorded. Ask what "
    "they want changed, or drop it if that is what they meant."
)


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

    An evidence interrupt resumes with the manifest, which ``request_evidence`` reads
    straight off ``interrupt``. A steps interrupt resumes with the user's message
    verbatim, because their own wording is what becomes the ticket's steps. A write gate
    resumes with the ``decisions`` envelope
    HumanInTheLoopMiddleware unwraps, carrying one decision per tool call it is
    holding — it raises if that count disagrees, so the count is read off the request
    rather than assumed to be one.

    A rejection's message becomes the tool result the model reads next, so it says what
    happened rather than passing the user's bare word through. Resuming with "no" alone
    left the model announcing that a report it never filed had reached the team.
    """
    if isinstance(interrupt_value, dict) and "evidence_request" in interrupt_value:
        return evidence or []
    if isinstance(interrupt_value, dict) and "steps_request" in interrupt_value:
        return text
    requests = interrupt_value.get("action_requests") if isinstance(interrupt_value, dict) else None
    held = len(requests) if requests else 1
    if _is_affirmative(text):
        decision = {"type": "approve"}
    else:
        decision = {"type": "reject", "message": DECLINED.format(message=text.strip() or "nothing")}
    return {"decisions": [dict(decision) for _ in range(held)]}


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
    """Describe a pending ticket write in one line, from the args the model drafted.

    A link reads exactly like a fresh filing. The user has no access to the team's
    tracker, so naming the issue their report would join asks them to vouch for
    something they cannot open, and whether we merged or filed is bookkeeping they
    have no use for.
    """
    requests = (value or {}).get("action_requests") or []
    if not requests:
        return CONFIRM_WRITE
    request = requests[0]
    if request.get("name") == "link_to_existing":
        return "Ready to send this to the DailoQA development team. Send it?"
    title = str((request.get("args") or {}).get("title") or "").strip()
    if not title:
        return CONFIRM_WRITE
    return f'Ready to file this as "{title}". Send it?'


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
    if isinstance(value, dict) and "steps_request" in value:
        return "steps", "open", str(value.get("question") or "")
    return "confirm", "awaiting_confirm", _write_summary(value if isinstance(value, dict) else {})


async def _settled_state(conversation_id: str) -> str:
    """Return the composer state for a turn that ended without suspending.

    A turn that approved a filing leaves a queued job behind, and ``get_input_state``
    reports such a conversation as ``pending`` on every later resync. Publishing ``open``
    here would let the composer take a message that a reload then locks out, so the job
    row is consulted rather than assumed absent.
    """
    async with async_session() as session:
        return "pending" if await has_active_job(session, conversation_id) else "open"


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
        if input_state == "open":
            input_state = await _settled_state(conversation_id)
        trailing = "" if stream.text.strip() or not fallback else fallback
        if trailing:
            await stream.token(trailing)
        await _persist(conversation_id, turn_id, stream.text, stage)
        await stream.publish({"text": "", "stage": stage, "input_state": input_state})
    except Exception as error:
        logger.exception("turn %s failed for conversation %s: %s", turn_id, conversation_id, error)
        notice = SERVICE_UNAVAILABLE if is_unavailable(error) else TURN_FAILED
        try:
            await _persist(conversation_id, turn_id, notice, "error")
        except Exception:
            logger.exception("could not persist the failure notice for turn %s", turn_id)
        await stream.publish({"text": notice, "stage": "error", "input_state": "open"})
