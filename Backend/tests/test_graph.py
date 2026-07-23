import os

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.agent.graph import build_graph, enqueue_job
from app.agent.state import AgentState
from app.db.models import Job


def test_build_graph_has_expected_nodes():
    graph = build_graph()
    node_names = set(graph.nodes)
    for expected in ["classify", "gather", "preview_dedupe", "confirm", "enqueue"]:
        assert expected in node_names


@pytest_asyncio.fixture
async def session(migrated_db):
    maker = async_sessionmaker(migrated_db, class_=AsyncSession, expire_on_commit=False)
    async with maker() as s:
        yield s


@pytest.mark.asyncio
async def test_enqueue_job_writes_queued_row(session):
    if not os.getenv("TEST_DATABASE_URL"):
        pytest.skip("TEST_DATABASE_URL not set")
    state: AgentState = {
        "user_sub": "sub-1",
        "conversation_id": "conv-1",
        "kind": "bug",
        "fields": {"summary": "search broken"},
        "dedupe_key": None,
        "confirmed": True,
    }
    job_id = await enqueue_job(session, state)
    await session.commit()
    job = (await session.execute(select(Job).where(Job.id == job_id))).scalar_one()
    assert job.status == "queued"
    assert job.type == "create_ticket"
    assert job.payload["kind"] == "bug"
