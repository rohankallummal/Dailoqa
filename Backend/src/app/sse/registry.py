"""In-process registry of active SSE subscribers, keyed by user_sub."""

import asyncio


class Subscriber:
    """A single SSE connection's event queue."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[dict] = asyncio.Queue()

    async def get(self) -> dict:
        """Await the next event for this subscriber."""
        return await self._queue.get()

    def put_nowait(self, event: dict) -> None:
        """Enqueue an event without blocking."""
        self._queue.put_nowait(event)

    def empty(self) -> bool:
        """Whether the queue currently has no pending events."""
        return self._queue.empty()


class SseRegistry:
    """Fan-out registry mapping user_sub to the set of that user's subscribers."""

    def __init__(self) -> None:
        self._subscribers: dict[str, set[Subscriber]] = {}

    def subscribe(self, user_sub: str) -> Subscriber:
        """Register and return a new subscriber for a user."""
        subscriber = Subscriber()
        self._subscribers.setdefault(user_sub, set()).add(subscriber)
        return subscriber

    def unsubscribe(self, user_sub: str, subscriber: Subscriber) -> None:
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
