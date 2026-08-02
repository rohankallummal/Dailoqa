"""Typed state and structured schemas for the ticket agent graph."""

from typing import Literal, TypedDict

from pydantic import BaseModel, Field


class Classification(BaseModel):
    """The category of a user's message."""

    kind: Literal["bug", "feature", "other"] = Field(description="bug for a defect, feature for a request, other otherwise.")
    reason: str = Field(description="Short justification for the classification.")


class AgentState(TypedDict, total=False):
    """Working state threaded through the agent graph."""

    messages: list
    surface: str
    user_sub: str
    conversation_id: str
    kind: str
    ticket: dict
    client_environment: dict
    reporter: dict
    evidence: list
    confirmed: bool
    job_id: str | None
    reply: str
