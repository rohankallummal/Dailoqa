"""Per-turn values the agent's tools need but the model must never supply."""

from dataclasses import dataclass, field


@dataclass
class TurnContext:
    """Identity and environment for one conversation turn.

    Passed to the agent as ``context=`` and reached inside tools through
    ``ToolRuntime.context``. These values are trusted server state, so they are
    deliberately kept out of every tool's model-visible argument schema: a model
    that could set ``user_sub`` could file a ticket as somebody else.
    """

    user_sub: str
    conversation_id: str
    reporter_name: str
    client_environment: dict = field(default_factory=dict)
