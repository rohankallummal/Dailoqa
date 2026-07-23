from app.db.base import APP_SCHEMA, Base
from app.db import models  # noqa: F401


def test_metadata_has_naming_convention():
    nc = Base.metadata.naming_convention
    assert nc.get("uq") is not None
    assert nc.get("ix") is not None


def test_job_id_uniques_named_to_match_migration():
    messages = Base.metadata.tables[f"{APP_SCHEMA}.messages"]
    notifications = Base.metadata.tables[f"{APP_SCHEMA}.notifications"]
    uq_names = {c.name for t in (messages, notifications) for c in t.constraints
               if c.__class__.__name__ == "UniqueConstraint"}
    assert "uq_message_job" in uq_names
    assert "uq_notification_job" in uq_names


def test_env_include_object_filters_non_app_schema():
    from app.migrations.env import _include_object

    assert _include_object(object=None, name="x", type_="table", reflected=True, compare_to=None, schema="public") is False
    assert _include_object(object=None, name="x", type_="table", reflected=False, compare_to=None, schema="app") is True
    assert _include_object(object=None, name="x", type_="table", reflected=True, compare_to=None, schema="langgraph") is False
