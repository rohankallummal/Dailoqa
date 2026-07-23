import os

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.agent.dedupe import DedupeVerdict
from app.db.models import Conversation, Job, Notification
from app.worker.processor import process_job


class _FakeClient:
    project_key = "KAN"

    def issue_type_for(self, kind):
        return "Bug"

    async def search_issues(self, jql, fields=None, max_results=20):
        return []

    async def create_issue(self, issue_type, summary, description, labels=None):
        return {"key": "KAN-11", "id": "1100"}


class _FakeStructured:
    def __init__(self, v):
        self._v = v

    async def ainvoke(self, _m):
        return self._v


class _FakeModel:
    def __init__(self, v):
        self._v = v

    def with_structured_output(self, _s):
        return _FakeStructured(self._v)


@pytest_asyncio.fixture
async def maker(migrated_db):
    return async_sessionmaker(migrated_db, class_=AsyncSession, expire_on_commit=False)


@pytest.mark.asyncio
async def test_process_create_path(maker):
    if not os.getenv("TEST_DATABASE_URL"):
        pytest.skip("TEST_DATABASE_URL not set")
    async with maker() as s:
        conv = Conversation(user_sub="sub-1", surface="panel")
        s.add(conv)
        await s.flush()
        job = Job(type="create_ticket", status="running", conversation_id=conv.id, user_sub="sub-1",
                  payload={"kind": "bug", "fields": {"summary": "x"}, "dedupe_key": None})
        s.add(job)
        await s.commit()
        job_id = job.id
    async with maker() as s:
        job = (await s.execute(select(Job).where(Job.id == job_id))).scalar_one()
        await process_job(s, job, _FakeClient(), model=_FakeModel(DedupeVerdict(match_key=None, confidence=0.0)))
        await s.commit()
    async with maker() as s:
        job = (await s.execute(select(Job).where(Job.id == job_id))).scalar_one()
        notif = (await s.execute(select(Notification).where(Notification.job_id == job_id))).scalar_one()
    assert job.status == "succeeded"
    assert job.jira_key == "KAN-11"
    assert notif.type == "ticket_created"


@pytest.mark.asyncio
async def test_run_one_marks_failed_after_error(maker):
    if not os.getenv("TEST_DATABASE_URL"):
        pytest.skip("TEST_DATABASE_URL not set")
    from app.worker.runner import run_one
    from app.db.models import Job

    class _BoomClient:
        project_key = "KAN"

        def issue_type_for(self, kind):
            return "Bug"

        async def search_issues(self, jql, fields=None, max_results=20):
            return []

        async def create_issue(self, *a, **k):
            raise RuntimeError("jira down")

    async with maker() as s:
        job = Job(type="create_ticket", status="queued", conversation_id="c1", user_sub="sub-1",
                  payload={"kind": "bug", "fields": {"summary": "x"}, "dedupe_key": None})
        s.add(job)
        await s.commit()
        job_id = job.id
    handled = await run_one(maker, _BoomClient(), "worker-x",
                            model=_FakeModel(DedupeVerdict(match_key=None, confidence=0.0)))
    assert handled is True
    async with maker() as s:
        job = (await s.execute(select(Job).where(Job.id == job_id))).scalar_one()
    assert job.status == "queued"  # requeued (attempt 1 of 5)
    assert job.attempts == 1
    assert "jira down" in job.last_error
