"""Middleware that reports tool activity to the chat surface as it happens."""

from collections.abc import Awaitable, Callable

from langchain.agents.middleware import AgentMiddleware

_LABELS = {
    "search_existing_issues": "Checking for similar reports",
    "create_ticket": "Submitting your report",
    "link_to_existing": "Adding you to the existing report",
    "load_skill": "Getting up to speed",
    "request_evidence": "Waiting for your attachments",
}


class StreamPublisherMiddleware(AgentMiddleware):
    """Publishes a human-readable status line around every tool call.

    Without this the chat shows an undifferentiated spinner while the agent searches
    Jira, which is the slowest step in most conversations.
    """

    def __init__(self, publish: Callable[[dict], Awaitable[None]]) -> None:
        super().__init__()
        self._publish = publish

    async def awrap_tool_call(self, request, handler):
        """Announce the tool, run it, then clear the status."""
        label = _LABELS.get(request.tool_call["name"])
        if label:
            await self._publish({"stage": "tool_status", "tool": request.tool_call["name"], "text": label})
        try:
            return await handler(request)
        finally:
            if label:
                await self._publish({"stage": "tool_status", "tool": None, "text": ""})
