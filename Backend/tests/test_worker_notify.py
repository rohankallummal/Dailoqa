import os

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models import Conversation, Message, Notification
from app.worker.notify import deliver_result


@pytest_asyncio.fixture
async def maker(migrated_db):
    return async_sessionmaker(migrated_db, class_=AsyncSession, expire_on_commit=False)


@pytest.mark.asyncio
async def test_deliver_result_is_idempotent_on_job_id(maker):
    if not os.getenv("TEST_DATABASE_URL"):
        pytest.skip("TEST_DATABASE_URL not set")
    from app.db.models import Job
    async with maker() as s:
        conv = Conversation(user_sub="sub-1", surface="panel")
        s.add(conv)
        await s.flush()
        job = Job(type="create_ticket", status="running", conversation_id=conv.id, user_sub="sub-1", payload={})
        s.add(job)
        await s.commit()
        conv_id, job_id = conv.id, job.id

    async with maker() as s:
        job = (await s.execute(select(Job).where(Job.id == job_id))).scalar_one()
        await deliver_result(s, job, "ticket_created", "Ticket created", "KAN-1 created", "KAN-1")
        await s.commit()
    async with maker() as s:
        job = (await s.execute(select(Job).where(Job.id == job_id))).scalar_one()
        await deliver_result(s, job, "ticket_created", "Ticket created", "KAN-1 created", "KAN-1")
        await s.commit()

    async with maker() as s:
        notifs = (await s.execute(select(Notification).where(Notification.job_id == job_id))).scalars().all()
        msgs = (await s.execute(select(Message).where(Message.job_id == job_id))).scalars().all()
    assert len(notifs) == 1
    assert len(msgs) == 1


@pytest.mark.asyncio
async def test_deleted_conversation_gets_notification_only(maker):
    if not os.getenv("TEST_DATABASE_URL"):
        pytest.skip("TEST_DATABASE_URL not set")
    from datetime import datetime, timezone
    from app.db.models import Job
    async with maker() as s:
        conv = Conversation(user_sub="sub-1", surface="panel", deleted_at=datetime.now(timezone.utc))
        s.add(conv)
        await s.flush()
        job = Job(type="create_ticket", status="running", conversation_id=conv.id, user_sub="sub-1", payload={})
        s.add(job)
        await s.commit()
        job_id = job.id
    async with maker() as s:
        job = (await s.execute(select(Job).where(Job.id == job_id))).scalar_one()
        await deliver_result(s, job, "ticket_created", "Ticket created", "KAN-1 created", "KAN-1")
        await s.commit()
    async with maker() as s:
        msgs = (await s.execute(select(Message).where(Message.job_id == job_id))).scalars().all()
        notifs = (await s.execute(select(Notification).where(Notification.job_id == job_id))).scalars().all()
    assert len(msgs) == 0
    assert len(notifs) == 1
