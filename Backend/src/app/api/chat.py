"""POST /chat/send: start or resume an agent turn; stream results over SSE."""

import asyncio
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.agent.runner import run_turn
from app.agent.title import generate_title
from app.auth import AuthContext, require_auth
from app.db.base import async_session
from app.db.repositories import (
    append_message,
    create_conversation,
    get_owned_conversation,
    set_conversation_title,
)
from app.evidence.storage import normalize_manifest, validate_manifest

router = APIRouter()

logger = logging.getLogger(__name__)

_title_tasks: set = set()

_turn_tasks: set = set()

_running_turns: set[str] = set()


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


class EvidenceFile(BaseModel):
    """One uploaded evidence file, as reported by the frontend."""

    name: str
    category: str
    size: int


class ClientEnvironmentInput(BaseModel):
    """Device, browser, and operating system as reported by the reporter's browser."""

    device: str = "Unknown"
    browser: str = "Unknown"
    operating_system: str = "Unknown"


class SendRequest(BaseModel):
    """A user's message on a given surface, optionally carrying an evidence manifest."""

    conversation_id: str | None = None
    surface: str
    text: str
    evidence: list[EvidenceFile] | None = None
    client_environment: ClientEnvironmentInput | None = None


async def _require_owned(conversation_id: str, user_sub: str) -> None:
    """Reject a conversation id the caller does not own, as a 404.

    The agent is keyed by ``thread_id = conversation_id``, so without this an attacker
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


async def _finish_turn(
    user_sub: str,
    user_name: str,
    conversation_id: str,
    turn_id: str,
    surface: str,
    text: str,
    evidence: list[dict] | None,
    client_environment: dict | None,
    is_new: bool,
) -> None:
    """Run the turn detached from the accepting request and release the busy marker.

    Runs detached so a client that navigates away, reconnects, or times out cannot
    abandon a half-run turn. ``run_turn`` owns publishing and persistence and never
    raises, so the only job left here is the marker and the title.
    """
    try:
        await run_turn(
            user_sub, user_name, conversation_id, turn_id, surface, text, evidence, client_environment
        )
        if is_new:
            _schedule_title(conversation_id, text)
    finally:
        _running_turns.discard(conversation_id)


def _spawn_turn(*args) -> None:
    """Run a turn in the background, holding a reference so it is not garbage collected."""
    task = asyncio.create_task(_finish_turn(*args))
    _turn_tasks.add(task)
    task.add_done_callback(_turn_tasks.discard)


async def accept_turn(
    user_sub: str,
    user_name: str,
    conversation_id: str | None,
    surface: str,
    text: str,
    evidence: list[dict] | None = None,
    client_environment: dict | None = None,
) -> tuple[str, str]:
    """Persist the user message, start the turn in the background, return its ids.

    Returns as soon as the message is durable, so the caller never waits on the model.
    Raises HTTPException(409) when a turn is already running for the conversation: the
    agent is keyed by ``thread_id = conversation_id``, and two turns racing on one thread
    interleave their interrupts and corrupt the report being collected. That is what a
    user produced by pressing Send repeatedly against the old blocking endpoint.

    The busy check runs before the message is persisted as well as after the id is
    resolved. The early check keeps a rejected duplicate from leaving an orphan user
    message in the history; the later one is the authoritative claim, since a brand-new
    conversation has no id to check until _start_turn has created it.

    _running_turns is process-local, which is sufficient while a single backend instance
    serves a conversation. Running several instances would need the claim moved into
    Postgres, an advisory lock keyed on the conversation being the natural fit.
    """
    turn_id = uuid.uuid4().hex
    is_new = conversation_id is None
    if conversation_id is not None and conversation_id in _running_turns:
        raise HTTPException(status_code=409, detail="a turn is already running")
    conversation_id = await _start_turn(user_sub, conversation_id, surface, text)
    if conversation_id in _running_turns:
        raise HTTPException(status_code=409, detail="a turn is already running")
    _running_turns.add(conversation_id)
    _spawn_turn(
        user_sub,
        user_name,
        conversation_id,
        turn_id,
        surface,
        text,
        evidence,
        client_environment,
        is_new,
    )
    return conversation_id, turn_id


@router.post("/chat/send", status_code=202)
async def chat_send(body: SendRequest, auth: AuthContext = Depends(require_auth)) -> dict:
    """Accept a turn and return immediately; results stream over /events.

    An existing conversation must belong to the caller. An evidence manifest is verified
    against the files on disk before the turn is accepted, so a rejection leaves the
    interrupt unconsumed and the card still shown.

    The response means "accepted", not "answered": ``input_state`` is always ``thinking``
    and the real state arrives as an SSE delta. Nothing here waits on the model, so a slow
    turn can no longer time the caller out or leave the browser and the agent disagreeing
    about what happened.
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
    environment = body.client_environment.model_dump() if body.client_environment else None
    conversation_id, turn_id = await accept_turn(
        auth.user_sub,
        auth.user_name,
        body.conversation_id,
        body.surface,
        body.text,
        manifest,
        environment,
    )
    return {"conversation_id": conversation_id, "turn_id": turn_id, "input_state": "thinking"}
