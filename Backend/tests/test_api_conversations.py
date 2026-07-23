import os
import time

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.auth import SERVICE_JWT_AUDIENCE
from app.config import get_settings
from app.main import app

_DB = pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="needs DB")


@pytest.fixture(autouse=True)
def _env(base_env):
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _token(sub="sub-1"):
    return jwt.encode(
        {"sub": sub, "userId": "u1", "aud": SERVICE_JWT_AUDIENCE, "iat": int(time.time()), "exp": int(time.time()) + 60},
        os.environ["SERVICE_JWT_SECRET"],
        algorithm="HS256",
    )


def test_notifications_requires_auth():
    with TestClient(app) as client:
        assert client.get("/notifications").status_code == 401


def test_conversations_requires_auth():
    with TestClient(app) as client:
        assert client.get("/conversations?surface=panel").status_code == 401


@_DB
@pytest.mark.asyncio
async def test_delete_without_job_hard_deletes(migrated_db):
    from app.api.conversations import delete_conversation
    from app.auth import AuthContext
    from app.db.base import async_session
    from app.db.repositories import append_message, create_conversation, list_conversations

    async with async_session() as session:
        conversation = await create_conversation(session, "sub-hard", "panel")
        await append_message(session, conversation.id, "user", "hi")
        await session.commit()
        conversation_id = conversation.id

    result = await delete_conversation(conversation_id, AuthContext(user_sub="sub-hard", user_id="u1"))
    assert result["soft_deleted"] is False
    async with async_session() as session:
        assert await list_conversations(session, "sub-hard", "panel") == []


@_DB
@pytest.mark.asyncio
async def test_delete_with_job_soft_deletes(migrated_db):
    from app.api.conversations import delete_conversation
    from app.auth import AuthContext
    from app.db.base import async_session
    from app.db.models import Conversation, Job
    from app.db.repositories import create_conversation, list_conversations

    async with async_session() as session:
        conversation = await create_conversation(session, "sub-soft", "panel")
        session.add(
            Job(type="create_ticket", status="queued", conversation_id=conversation.id, user_sub="sub-soft", payload={})
        )
        await session.commit()
        conversation_id = conversation.id

    result = await delete_conversation(conversation_id, AuthContext(user_sub="sub-soft", user_id="u1"))
    assert result["soft_deleted"] is True
    async with async_session() as session:
        row = (await session.execute(select(Conversation).where(Conversation.id == conversation_id))).scalar_one()
        assert row.deleted_at is not None
        assert await list_conversations(session, "sub-soft", "panel") == []


@_DB
@pytest.mark.asyncio
async def test_delete_other_users_conversation_404s(migrated_db):
    from fastapi import HTTPException

    from app.api.conversations import delete_conversation
    from app.auth import AuthContext
    from app.db.base import async_session
    from app.db.repositories import create_conversation

    async with async_session() as session:
        conversation = await create_conversation(session, "owner", "panel")
        await session.commit()
        conversation_id = conversation.id

    with pytest.raises(HTTPException) as exc:
        await delete_conversation(conversation_id, AuthContext(user_sub="intruder", user_id="u2"))
    assert exc.value.status_code == 404


@_DB
@pytest.mark.asyncio
async def test_abandon_hides_unconfirmed_but_keeps_jobbed(migrated_db):
    from app.api.conversations import AbandonRequest, abandon_conversations
    from app.auth import AuthContext
    from app.db.base import async_session
    from app.db.models import Conversation, Job
    from app.db.repositories import create_conversation

    async with async_session() as session:
        unconfirmed = await create_conversation(session, "sub-ab", "panel")
        jobbed = await create_conversation(session, "sub-ab", "panel")
        session.add(
            Job(type="create_ticket", status="running", conversation_id=jobbed.id, user_sub="sub-ab", payload={})
        )
        await session.commit()
        unconfirmed_id, jobbed_id = unconfirmed.id, jobbed.id

    result = await abandon_conversations(AbandonRequest(), AuthContext(user_sub="sub-ab", user_id="u1"))
    assert result["abandoned"] == 1
    async with async_session() as session:
        a = (await session.execute(select(Conversation).where(Conversation.id == unconfirmed_id))).scalar_one()
        j = (await session.execute(select(Conversation).where(Conversation.id == jobbed_id))).scalar_one()
        assert a.status == "abandoned"
        assert j.status == "active"


@_DB
@pytest.mark.asyncio
async def test_notifications_list_and_mark_read(migrated_db):
    from app.api.notifications import MarkReadRequest, get_notifications, post_mark_read
    from app.auth import AuthContext
    from app.db.base import async_session
    from app.db.models import Notification

    async with async_session() as session:
        session.add(Notification(user_sub="sub-nl", type="ticket_created", title="Created", body="KAN-1"))
        await session.commit()

    auth = AuthContext(user_sub="sub-nl", user_id="u1")
    rows = await get_notifications(auth)
    assert len(rows) == 1 and rows[0]["title"] == "Created"
    await post_mark_read(MarkReadRequest(ids=[rows[0]["id"]]), auth)
    assert await get_notifications(auth) == []
