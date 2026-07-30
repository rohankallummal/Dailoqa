"""Postgres LISTEN/NOTIFY wake hints that trigger reads from the durable feed."""

import asyncio
import logging

from app.db.notifications import list_undelivered
from app.sse.registry import registry

logger = logging.getLogger(__name__)

_SWEEP_INTERVAL_SECONDS = 30.0


async def push_undelivered_to_user(session_maker, user_sub: str) -> None:
    """Read the user's undelivered notifications and publish each to the SSE registry.

    Selecting on delivery rather than read state keeps the periodic sweep cheap: once a
    client acknowledges a toast the row drops out of this query, so a user sitting on a
    long backlog of unread notifications is not re-sent all of them every sweep.
    """
    async with session_maker() as session:
        for notification in await list_undelivered(session, user_sub):
            await registry.publish(
                user_sub,
                {
                    "type": "notification",
                    "id": notification.id,
                    "title": notification.title,
                    "body": notification.body,
                    "jira_key": notification.jira_key,
                    "notification_type": notification.type,
                    "conversation_id": notification.conversation_id,
                },
            )


async def run_listener(session_maker, stop_event: asyncio.Event | None = None) -> None:
    """LISTEN on the notifications channel; on each NOTIFY read+publish undelivered.

    A missed NOTIFY is covered by the on-connect read (the SSE endpoint) and this
    loop's periodic safety sweep of currently subscribed users, so delivery never
    depends on catching every signal. The connection is opened lazily and failures
    are swallowed so the app boots even when no database is reachable.
    """
    from psycopg import AsyncConnection

    from app.agent.checkpointer import _raw_dsn

    stop_event = stop_event or asyncio.Event()
    try:
        async with await AsyncConnection.connect(_raw_dsn(), autocommit=True) as conn:
            await conn.execute("LISTEN notifications")
            while not stop_event.is_set():
                received = False
                async for notify in conn.notifies(timeout=_SWEEP_INTERVAL_SECONDS, stop_after=1):
                    received = True
                    await push_undelivered_to_user(session_maker, notify.payload)
                if not received:
                    for user_sub in registry.active_user_subs():
                        await push_undelivered_to_user(session_maker, user_sub)
    except asyncio.CancelledError:
        raise
    except Exception as error:
        logger.warning("notifications backplane stopped: %s", error)
