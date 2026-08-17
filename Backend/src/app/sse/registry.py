"""In-process registry of active SSE subscribers, keyed by user_sub."""

import asyncio


class SseRegistry:
    """Fan-out registry mapping user_sub to the set of that user's event queues."""

    def __init__(self) -> None:
        self._subscribers: dict[str, set[asyncio.Queue]] = {}

    def subscribe(self, user_sub: str) -> asyncio.Queue:
        """Register and return a new event queue for a user."""
        subscriber: asyncio.Queue[dict] = asyncio.Queue()
        self._subscribers.setdefault(user_sub, set()).add(subscriber)
        return subscriber

    def unsubscribe(self, user_sub: str, subscriber: asyncio.Queue) -> None:
        """Remove a subscriber; drop the user entry when empty."""
        subs = self._subscribers.get(user_sub)
        if subs:
            subs.discard(subscriber)
            if not subs:
                self._subscribers.pop(user_sub, None)

    def active_user_subs(self) -> list[str]:
        """Return the user_subs that currently have at least one subscriber."""
        return list(self._subscribers.keys())

    async def publish(self, user_sub: str, event: dict) -> None:
        """Deliver an event to every current subscriber of a user."""
        for subscriber in list(self._subscribers.get(user_sub, ())):
            subscriber.put_nowait(event)


registry = SseRegistry()
