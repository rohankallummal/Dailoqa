"""Postgres checkpointer for the agent graph, pinned to the langgraph schema."""

from contextlib import asynccontextmanager

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.config import get_settings

LANGGRAPH_SCHEMA = "langgraph"


def _psycopg_dsn() -> str:
    """Return a raw psycopg DSN pinned to the langgraph schema via search_path.

    The checkpointer wants a libpq DSN with no SQLAlchemy dialect prefix; the
    ``options`` parameter sets ``search_path`` so its tables land in the isolated
    langgraph schema rather than public.
    """
    url = get_settings().database_url.replace("postgresql+psycopg://", "postgresql://")
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}options=-c%20search_path%3D{LANGGRAPH_SCHEMA}"


@asynccontextmanager
async def build_checkpointer():
    """Yield an AsyncPostgresSaver whose tables live in the langgraph schema.

    Ensures the schema exists, opens the saver over a search_path-pinned DSN, and
    runs .setup() so checkpoint/writes tables are created there on first use. The
    connection mirrors the saver's own requirements (autocommit, dict rows, no
    server-side prepared statements).
    """
    from psycopg import AsyncConnection
    from psycopg.rows import dict_row

    async with await AsyncConnection.connect(
        _psycopg_dsn(), autocommit=True, prepare_threshold=0, row_factory=dict_row
    ) as conn:
        await conn.execute(f"CREATE SCHEMA IF NOT EXISTS {LANGGRAPH_SCHEMA}")
        saver = AsyncPostgresSaver(conn)
        await saver.setup()
        yield saver
