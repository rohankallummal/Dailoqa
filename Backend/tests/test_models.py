from app.db.base import APP_SCHEMA, Base
from app.db import models  # noqa: F401


def test_all_tables_registered_in_app_schema():
    tables = Base.metadata.tables
    expected = {
        f"{APP_SCHEMA}.conversations",
        f"{APP_SCHEMA}.messages",
        f"{APP_SCHEMA}.tickets",
        f"{APP_SCHEMA}.ticket_reporters",
        f"{APP_SCHEMA}.jobs",
        f"{APP_SCHEMA}.notifications",
    }
    assert expected.issubset(set(tables.keys()))


def test_idempotency_unique_constraints_present():
    messages = Base.metadata.tables[f"{APP_SCHEMA}.messages"]
    notifications = Base.metadata.tables[f"{APP_SCHEMA}.notifications"]
    reporters = Base.metadata.tables[f"{APP_SCHEMA}.ticket_reporters"]

    assert messages.c.job_id.unique is True
    assert notifications.c.job_id.unique is True
    reporter_uniques = [c for c in reporters.constraints if c.__class__.__name__ == "UniqueConstraint"]
    assert any({"ticket_id", "user_sub"} == {col.name for col in c.columns} for c in reporter_uniques)


def test_conversation_isolation_columns_present():
    conversations = Base.metadata.tables[f"{APP_SCHEMA}.conversations"]
    assert "user_sub" in conversations.c
    assert "surface" in conversations.c
    assert "deleted_at" in conversations.c
    assert "status" in conversations.c
