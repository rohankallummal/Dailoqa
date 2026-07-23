"""Async Alembic environment pinned to the app schema."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import get_settings
from app.db.base import APP_SCHEMA, Base
from app.db import models  # noqa: F401

target_metadata = Base.metadata


def _include_object(object, name, type_, reflected, compare_to, schema=None) -> bool:
    """Restrict autogenerate to the app schema so public (Drizzle) and langgraph are ignored.

    Alembic invokes this with five positional arguments and no schema; the schema
    is then derived from the reflected/target object. The keyword is accepted so
    callers (and tests) may pass the schema explicitly.
    """
    effective_schema = schema if schema is not None else getattr(object, "schema", None)
    if effective_schema is not None and effective_schema != APP_SCHEMA:
        return False
    return True


def _url() -> str:
    return context.config.get_main_option("sqlalchemy.url") or get_settings().database_url


def _run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema=APP_SCHEMA,
        include_schemas=True,
        include_object=_include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


async def _run_async() -> None:
    engine = create_async_engine(_url())
    async with engine.begin() as connection:
        await connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {APP_SCHEMA}"))
    async with engine.connect() as connection:
        await connection.run_sync(_run_migrations)
    await engine.dispose()


def run() -> None:
    """Run migrations online or offline; invoked when Alembic loads this environment."""
    config = context.config
    if config.config_file_name is not None:
        fileConfig(config.config_file_name)
    if context.is_offline_mode():
        context.configure(
            url=_url(),
            target_metadata=target_metadata,
            version_table_schema=APP_SCHEMA,
            include_object=_include_object,
        )
        with context.begin_transaction():
            context.run_migrations()
    else:
        asyncio.run(_run_async())


def _under_alembic() -> bool:
    """True only when Alembic has installed its context proxy (env loaded by a command)."""
    try:
        context.config
    except AttributeError:
        return False
    return True


if _under_alembic():
    run()
