"""Tests verifying Alembic migrations produce the expected schema layout."""

import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_schemas_and_tables_created(migrated_db):
    """Migrating to head creates the app and langgraph schemas and all six app tables."""
    async with migrated_db.connect() as conn:
        schemas = (
            await conn.execute(
                text("SELECT schema_name FROM information_schema.schemata")
            )
        ).scalars().all()
        assert "app" in schemas
        assert "langgraph" in schemas

        tables = (
            await conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'app'")
            )
        ).scalars().all()
        for expected in ["conversations", "messages", "tickets", "ticket_reporters", "jobs", "notifications"]:
            assert expected in tables


@pytest.mark.asyncio
async def test_alembic_version_table_in_app_schema(migrated_db):
    """The Alembic version table lives in the app schema, not public."""
    async with migrated_db.connect() as conn:
        tables = (
            await conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'app'")
            )
        ).scalars().all()
        assert "alembic_version" in tables
