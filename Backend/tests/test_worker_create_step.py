import os

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models import Job, Ticket
from app.worker.create_step import create_ticket


class _FakeClient:
    def __init__(self):
        self.calls = 0

    def issue_type_for(self, kind):
        return "Bug"

    async def create_issue(self, issue_type, summary, description, labels=None):
        self.calls += 1
        return {"key": "KAN-7", "id": "700"}


@pytest_asyncio.fixture
async def maker(migrated_db):
    return async_sessionmaker(migrated_db, class_=AsyncSession, expire_on_commit=False)


async def _job(maker, **overrides):
    async with maker() as s:
        job = Job(type="create_ticket", status="running", conversation_id="c1", user_sub="sub-1",
                  payload={"kind": "bug", "fields": {"summary": "search broken", "steps_to_reproduce": "search"}}, **overrides)
        s.add(job)
        await s.commit()
        return job.id


@pytest.mark.asyncio
async def test_create_persists_key_and_ticket(maker):
    if not os.getenv("TEST_DATABASE_URL"):
        pytest.skip("TEST_DATABASE_URL not set")
    job_id = await _job(maker)
    client = _FakeClient()
    async with maker() as s:
        job = (await s.execute(select(Job).where(Job.id == job_id))).scalar_one()
        key = await create_ticket(s, job, client)
        await s.commit()
    assert key == "KAN-7"
    async with maker() as s:
        job = (await s.execute(select(Job).where(Job.id == job_id))).scalar_one()
        ticket = (await s.execute(select(Ticket).where(Ticket.jira_key == "KAN-7"))).scalar_one()
    assert job.jira_key == "KAN-7"
    assert job.action == "create"
    assert ticket.type == "bug"


@pytest.mark.asyncio
async def test_resume_with_key_does_not_recreate(maker):
    if not os.getenv("TEST_DATABASE_URL"):
        pytest.skip("TEST_DATABASE_URL not set")
    job_id = await _job(maker, jira_key="KAN-7", action="create")
    client = _FakeClient()
    async with maker() as s:
        job = (await s.execute(select(Job).where(Job.id == job_id))).scalar_one()
        key = await create_ticket(s, job, client)
    assert key == "KAN-7"
    assert client.calls == 0
