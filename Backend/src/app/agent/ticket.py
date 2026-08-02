"""Typed ticket documents matching the sections in Ticket-Structure.md."""

from pydantic import BaseModel, Field

UNKNOWN_VALUE = "Unknown"


class ClientEnvironment(BaseModel):
    """The reporter's device, browser, and operating system."""

    device: str = UNKNOWN_VALUE
    browser: str = UNKNOWN_VALUE
    operating_system: str = UNKNOWN_VALUE


class Reporter(BaseModel):
    """The Google-authenticated user who filed or joined a report."""

    name: str
    oauth_id: str


class BugTicket(BaseModel):
    """A bug report composed by the agent from the conversation."""

    title: str = Field(description="A short, concise title for the bug.")
    summary: str = Field(description="A one-paragraph summary of the bug, written by you.")
    issue_description: str = Field(
        description="A clear description of the observed error or unexpected behavior, based on the user's messages."
    )
    steps_to_reproduce: list[str] = Field(
        default_factory=list,
        description="Ordered reproduction steps taken from the user's messages. Leave empty if the user has not described them.",
    )


class FeatureTicket(BaseModel):
    """A feature request composed by the agent from the conversation."""

    title: str = Field(description="A short, concise title for the feature request.")
    feature: str = Field(description="A clear description of what the user wants implemented.")
    problem_statement: str = Field(
        description="The problem or pain point this feature solves, and why it would be valuable. Leave empty if the user has not explained it."
    )


_MODELS: dict[str, type[BaseModel]] = {"bug": BugTicket, "feature": FeatureTicket}

_REQUIRED_SECTIONS: dict[str, list[str]] = {
    "bug": ["title", "summary", "issue_description"],
    "feature": ["title", "feature", "problem_statement"],
}


def ticket_model_for(kind: str) -> type[BaseModel]:
    """Return the ticket model for a classification kind."""
    model = _MODELS.get(kind)
    if model is None:
        raise ValueError(f"unknown ticket kind: {kind}")
    return model


def _is_blank(value) -> bool:
    """Report whether a composed section carries no usable content."""
    if isinstance(value, list):
        return not [item for item in value if str(item).strip()]
    return not str(value or "").strip()


def missing_sections(kind: str, ticket: dict, has_evidence: bool) -> list[str]:
    """Return the required section names the composer could not fill.

    Steps to reproduce are required only when no evidence was attached; supplied images
    or video stand in for the walkthrough.
    """
    required = list(_REQUIRED_SECTIONS.get(kind, []))
    if kind == "bug" and not has_evidence:
        required.append("steps_to_reproduce")
    return [name for name in required if _is_blank(ticket.get(name))]
