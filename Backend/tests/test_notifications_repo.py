import os

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models import Notification
from app.db.notifications import list_unread, mark_read


@pytest_asyncio.fixture
async def maker(migrated_db):
    return async_sessionmaker(migrated_db, class_=AsyncSession, expire_on_commit=False)


@pytest.mark.asyncio
async def test_unread_then_mark_read(maker):
    if not os.getenv("TEST_DATABASE_URL"):
        pytest.skip("TEST_DATABASE_URL not set")
    async with maker() as s:
        s.add(Notification(user_sub="sub-1", type="ticket_created", title="t", body="b"))
        s.add(Notification(user_sub="sub-2", type="ticket_created", title="t", body="b"))
        await s.commit()
    async with maker() as s:
        unread = await list_unread(s, "sub-1")
        assert len(unread) == 1
        await mark_read(s, "sub-1", [unread[0].id])
        await s.commit()
    async with maker() as s:
        assert await list_unread(s, "sub-1") == []
