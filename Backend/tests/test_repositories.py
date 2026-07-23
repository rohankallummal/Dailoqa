import os

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.db import repositories as repo


@pytest_asyncio.fixture
async def session(migrated_db):
    maker = async_sessionmaker(migrated_db, class_=AsyncSession, expire_on_commit=False)
    async with maker() as s:
        yield s


@pytest.mark.asyncio
async def test_create_and_list_conversation_scoped(session):
    if not os.getenv("TEST_DATABASE_URL"):
        pytest.skip("TEST_DATABASE_URL not set")
    conv = await repo.create_conversation(session, "sub-1", "panel", "Bug: search")
    await session.commit()
    listed = await repo.list_conversations(session, "sub-1", "panel")
    assert [c.id for c in listed] == [conv.id]
    assert await repo.list_conversations(session, "sub-1", "full") == []


@pytest.mark.asyncio
async def test_append_and_list_messages(session):
    if not os.getenv("TEST_DATABASE_URL"):
        pytest.skip("TEST_DATABASE_URL not set")
    conv = await repo.create_conversation(session, "sub-1", "panel")
    await repo.append_message(session, conv.id, "user", "search is broken")
    await session.commit()
    await repo.append_message(session, conv.id, "assistant", "what are the steps?")
    await session.commit()
    msgs = await repo.list_messages(session, conv.id)
    assert [m.role for m in msgs] == ["user", "assistant"]
