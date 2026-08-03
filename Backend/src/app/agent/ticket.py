"""Typed ticket documents shared by the agent's tools and the worker payload."""

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
