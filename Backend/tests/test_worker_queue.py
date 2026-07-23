import os

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models import Job
from app.worker import queue


@pytest_asyncio.fixture
async def maker(migrated_db):
    return async_sessionmaker(migrated_db, class_=AsyncSession, expire_on_commit=False)


async def _seed_job(maker) -> str:
    async with maker() as s:
        job = Job(type="create_ticket", status="queued", conversation_id="c1", user_sub="sub-1", payload={"kind": "bug"})
        s.add(job)
        await s.commit()
        return job.id


@pytest.mark.asyncio
async def test_claim_marks_running_and_locks(maker):
    if not os.getenv("TEST_DATABASE_URL"):
        pytest.skip("TEST_DATABASE_URL not set")
    job_id = await _seed_job(maker)
    async with maker() as s:
        claimed = await queue.claim_next_job(s, "worker-a")
        await s.commit()
    assert claimed.id == job_id
    async with maker() as s:
        row = (await s.execute(select(Job).where(Job.id == job_id))).scalar_one()
    assert row.status == "running"
    assert row.locked_by == "worker-a"


@pytest.mark.asyncio
async def test_fail_requeues_until_max_then_fails(maker):
    if not os.getenv("TEST_DATABASE_URL"):
        pytest.skip("TEST_DATABASE_URL not set")
    job_id = await _seed_job(maker)
    async with maker() as s:
        await queue.fail_job(s, job_id, "boom", max_attempts=2)
        await s.commit()
    async with maker() as s:
        row = (await s.execute(select(Job).where(Job.id == job_id))).scalar_one()
    assert row.status == "queued"
    assert row.attempts == 1
    async with maker() as s:
        await queue.fail_job(s, job_id, "boom again", max_attempts=2)
        await s.commit()
    async with maker() as s:
        row = (await s.execute(select(Job).where(Job.id == job_id))).scalar_one()
    assert row.status == "failed"
