import asyncio
import os

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://user:password@localhost:5432/dailoqa_test")
os.environ.setdefault("SERVICE_JWT_SECRET", "unit-test-service-jwt-secret-0123456789ab")
os.environ.setdefault("LLM_PROVIDER", "openai")
os.environ.setdefault("LLM_MODEL", "gpt-4o-mini")
os.environ.setdefault("JIRA_SITE_URL", "https://example.atlassian.net")

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


@pytest.fixture
def base_env(monkeypatch):
    """Set the minimum required env vars for constructing Settings."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost:5432/db")
    monkeypatch.setenv("SERVICE_JWT_SECRET", "unit-test-service-jwt-secret-0123456789ab")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("JIRA_SITE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_PROJECT_KEY", "KAN")


@pytest_asyncio.fixture
async def migrated_db():
    """Reset and migrate the test database, yielding an async engine bound to it."""
    if not TEST_DATABASE_URL:
        pytest.skip("TEST_DATABASE_URL not set")
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA IF EXISTS app CASCADE"))
        await conn.execute(text("DROP SCHEMA IF EXISTS langgraph CASCADE"))
    await engine.dispose()

    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    await asyncio.to_thread(command.upgrade, config, "head")

    engine = create_async_engine(TEST_DATABASE_URL)
    yield engine
    await engine.dispose()
