import os

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models import Notification
from app.sse.backplane import push_unread_to_user
from app.sse.registry import registry


@pytest_asyncio.fixture
async def maker(migrated_db):
    return async_sessionmaker(migrated_db, class_=AsyncSession, expire_on_commit=False)


@pytest.mark.asyncio
async def test_push_unread_publishes_to_subscriber(maker):
    if not os.getenv("TEST_DATABASE_URL"):
        pytest.skip("TEST_DATABASE_URL not set")
    async with maker() as s:
        s.add(Notification(user_sub="sub-42", type="ticket_created", title="Created", body="KAN-1"))
        await s.commit()
    sub = registry.subscribe("sub-42")
    try:
        await push_unread_to_user(maker, "sub-42")
        event = sub._queue.get_nowait()
        assert event["type"] == "notification"
        assert event["title"] == "Created"
    finally:
        registry.unsubscribe("sub-42", sub)
