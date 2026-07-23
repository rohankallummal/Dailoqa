import os

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models import Job, Ticket, TicketReporter
from app.worker.link_step import link_ticket


class _FakeClient:
    def __init__(self):
        self.comments = 0
        self.labels = 0

    async def add_comment(self, key, text):
        self.comments += 1

    async def add_labels(self, key, labels):
        self.labels += 1


@pytest_asyncio.fixture
async def maker(migrated_db):
    return async_sessionmaker(migrated_db, class_=AsyncSession, expire_on_commit=False)


@pytest.mark.asyncio
async def test_link_adds_reporter_once(maker):
    if not os.getenv("TEST_DATABASE_URL"):
        pytest.skip("TEST_DATABASE_URL not set")
    async with maker() as s:
        s.add(Ticket(jira_key="KAN-1", type="bug", title="dup"))
        job = Job(type="create_ticket", status="running", conversation_id="c1", user_sub="sub-9", payload={"kind": "bug"})
        s.add(job)
        await s.commit()
        job_id = job.id
    client = _FakeClient()
    for _ in range(2):
        async with maker() as s:
            job = (await s.execute(select(Job).where(Job.id == job_id))).scalar_one()
            await link_ticket(s, job, client, "KAN-1")
            await s.commit()
    async with maker() as s:
        ticket = (await s.execute(select(Ticket).where(Ticket.jira_key == "KAN-1"))).scalar_one()
        reporters = (await s.execute(select(TicketReporter).where(TicketReporter.ticket_id == ticket.id))).scalars().all()
    assert len(reporters) == 1
    assert client.comments == 1
