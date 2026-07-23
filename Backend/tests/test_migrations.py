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


@pytest.mark.asyncio
async def test_messages_metadata_column_and_unique_constraints(migrated_db):
    """The messages table exposes a literal metadata column and all four uq_* constraints exist."""
    async with migrated_db.connect() as conn:
        columns = (
            await conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = 'app' AND table_name = 'messages'"
                )
            )
        ).scalars().all()
        assert "metadata" in columns

        constraints = (
            await conn.execute(
                text(
                    "SELECT constraint_name FROM information_schema.table_constraints "
                    "WHERE table_schema = 'app' AND constraint_type = 'UNIQUE'"
                )
            )
        ).scalars().all()
        for expected in ["uq_message_job", "uq_notification_job", "uq_ticket_jira_key", "uq_ticket_reporter"]:
            assert expected in constraints


@pytest.mark.asyncio
async def test_metadata_and_payload_columns_are_jsonb(migrated_db):
    """messages.metadata and jobs.payload must be jsonb, not json, for worker inspection."""
    async with migrated_db.connect() as conn:
        rows = (
            await conn.execute(
                text(
                    "SELECT table_name, column_name, data_type FROM information_schema.columns "
                    "WHERE table_schema = 'app' "
                    "AND ((table_name = 'messages' AND column_name = 'metadata') "
                    "OR (table_name = 'jobs' AND column_name = 'payload'))"
                )
            )
        ).all()
        data_types = {(row.table_name, row.column_name): row.data_type for row in rows}
        assert data_types[("messages", "metadata")] == "jsonb"
        assert data_types[("jobs", "payload")] == "jsonb"
