import os
import time

import jwt
import pytest
from fastapi.testclient import TestClient

from app.api.chat import _confirm_prompt, _is_affirmative, _resume_value, _surface
from app.auth import SERVICE_JWT_AUDIENCE
from app.config import get_settings
from app.main import app


@pytest.fixture(autouse=True)
def _env(base_env):
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _token():
    return jwt.encode(
        {
            "sub": "sub-1",
            "userId": "u1",
            "aud": SERVICE_JWT_AUDIENCE,
            "iat": int(time.time()),
            "exp": int(time.time()) + 60,
        },
        os.environ["SERVICE_JWT_SECRET"],
        algorithm="HS256",
    )


class _Interrupt:
    def __init__(self, value):
        self.value = value


def test_is_affirmative():
    assert _is_affirmative("yes")
    assert _is_affirmative("Yes please")
    assert _is_affirmative("  OK ")
    assert not _is_affirmative("no")
    assert not _is_affirmative("not yet")


def test_resume_value_gather_maps_text_to_first_missing_field():
    value = {"question": "which env?", "missing": ["environment", "steps"]}
    assert _resume_value(value, "production") == {"environment": "production"}


def test_resume_value_confirm_returns_bool():
    assert _resume_value({"summary": {}, "dedupe_key": None}, "yes") is True
    assert _resume_value({"summary": {}, "dedupe_key": None}, "no") is False


def test_confirm_prompt_mentions_dedupe_key():
    assert "KAN-9" in _confirm_prompt({"summary": {}, "dedupe_key": "KAN-9"})
    assert "go ahead" in _confirm_prompt({"summary": {}, "dedupe_key": None}).lower()


def test_surface_gather_interrupt():
    result = {"__interrupt__": [_Interrupt({"question": "which env?", "missing": ["environment"]})]}
    delta, reached = _surface(result, "turn-1", "conv-1")
    assert reached is False
    assert delta == {"type": "delta", "turn_id": "turn-1", "conversation_id": "conv-1", "text": "which env?", "stage": "question"}


def test_surface_confirm_interrupt():
    result = {"__interrupt__": [_Interrupt({"summary": {"summary": "x"}, "dedupe_key": "KAN-2"})]}
    delta, reached = _surface(result, "turn-1", "conv-1")
    assert reached is False
    assert delta["stage"] == "confirm"
    assert "KAN-2" in delta["text"]


def test_surface_terminal_reply():
    delta, reached = _surface({"reply": "noted", "kind": "other"}, "turn-1", "conv-1")
    assert reached is False
    assert delta == {"type": "delta", "turn_id": "turn-1", "conversation_id": "conv-1", "text": "noted", "stage": "reply"}


def test_surface_terminal_confirmed_reaches_enqueue():
    result = {"reply": "Creating your ticket in the background.", "confirmed": True, "kind": "bug", "fields": {}}
    delta, reached = _surface(result, "turn-1", "conv-1")
    assert reached is True
    assert delta["stage"] == "reply"


def test_chat_send_requires_auth():
    with TestClient(app) as client:
        assert client.post("/chat/send", json={"surface": "panel", "text": "hi"}).status_code == 401


def test_chat_send_returns_turn_id(monkeypatch):
    async def _fake_run_turn(user_sub, conversation_id, surface, text):
        return conversation_id or "conv-new", "turn-123"

    monkeypatch.setattr("app.api.chat.run_turn", _fake_run_turn)
    with TestClient(app) as client:
        resp = client.post(
            "/chat/send",
            headers={"Authorization": f"Bearer {_token()}"},
            json={"surface": "panel", "text": "search is broken"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["turn_id"] == "turn-123"
        assert body["conversation_id"] == "conv-new"


def _terminal_builder(*args, **kwargs):
    from langgraph.graph import END, START, StateGraph

    from app.agent.state import AgentState

    builder = StateGraph(AgentState)

    async def classify(state):
        return {"kind": "other", "reply": "noted"}

    builder.add_node("classify", classify)
    builder.add_edge(START, "classify")
    builder.add_edge("classify", END)
    return builder


@pytest.mark.asyncio
@pytest.mark.skipif("not __import__('os').getenv('TEST_DATABASE_URL')", reason="needs DB")
async def test_run_turn_fresh_persists_and_publishes(migrated_db, monkeypatch):
    from app.api.chat import run_turn
    from app.db.base import async_session
    from app.db.repositories import list_messages
    from app.sse.registry import registry

    monkeypatch.setenv("DATABASE_URL", os.environ["TEST_DATABASE_URL"])
    get_settings.cache_clear()
    monkeypatch.setattr("app.api.chat.build_graph", _terminal_builder)
    subscriber = registry.subscribe("sub-run")
    try:
        conversation_id, turn_id = await run_turn("sub-run", None, "panel", "hello there")
        assert conversation_id and turn_id
        event = subscriber._queue.get_nowait()
        assert event["type"] == "delta"
        assert event["stage"] == "reply"
        assert event["text"] == "noted"
        async with async_session() as session:
            messages = await list_messages(session, conversation_id)
            assert [m.role for m in messages] == ["user", "assistant"]
            assert messages[0].content == "hello there"
    finally:
        registry.unsubscribe("sub-run", subscriber)
