import os

import pytest

from app.agent.checkpointer import LANGGRAPH_SCHEMA, build_checkpointer


@pytest.mark.asyncio
async def test_checkpointer_setup_creates_tables_in_langgraph_schema():
    if not os.getenv("TEST_DATABASE_URL"):
        pytest.skip("TEST_DATABASE_URL not set")
    async with build_checkpointer() as saver:
        assert saver is not None
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(os.environ["TEST_DATABASE_URL"])
    async with engine.connect() as conn:
        tables = (
            await conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = :s"),
                {"s": LANGGRAPH_SCHEMA},
            )
        ).scalars().all()
    await engine.dispose()
    assert any("checkpoint" in t for t in tables)
