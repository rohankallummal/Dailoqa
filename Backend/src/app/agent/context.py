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
    surface: str
    reporter_name: str
    client_environment: dict = field(default_factory=dict)
    grounding_corrections: int = 0
    """How many times this turn has been sent back for citing without consulting the docs.

    Bounded so a model that keeps citing unsourced cannot loop; see the grounding
    middleware. Per-turn like ``citations``, and never shown to the model.
    """

    citations: dict[str, int] = field(default_factory=dict)
    """Chunk id -> its ``[Doc N]`` number for this turn.

    The documentation tools may run several times in one turn, so the numbering they
    hand the model has to stay stable across those calls or the Sources legend stops
    matching the prose. This context object is the one thing every tool call in a turn
    shares, which makes it the natural place to keep the mapping. It is per-turn state,
    not identity, and is deliberately never exposed to the model.
    """
