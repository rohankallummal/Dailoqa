"""Composition of a ticket document from the conversation transcript."""

from app.agent.ticket import missing_sections, ticket_model_for
from app.llm import get_chat_model


def _transcript_text(transcript: list[str]) -> str:
    """Render the conversation turns as a numbered transcript for the composer."""
    return "\n".join(f"{index}. {turn}" for index, turn in enumerate(transcript, start=1))


async def compose_ticket(kind: str, transcript: list[str], has_evidence: bool, model=None) -> dict:
    """Compose a ticket document of the given kind from everything the user has said.

    Sections the transcript does not support are left blank rather than invented;
    missing_sections turns those blanks into the next follow-up question.
    """
    model = model or get_chat_model("agent")
    structured = model.with_structured_output(ticket_model_for(kind))
    evidence_note = (
        "The user has attached screenshots or a recording."
        if has_evidence
        else "The user has attached no screenshots or recording."
    )
    prompt = (
        f"You are writing a {kind} ticket for a development team from a user's support chat.\n"
        f"{evidence_note}\n\n"
        f"Conversation so far:\n{_transcript_text(transcript)}\n\n"
        "Write each field in clear, factual prose based only on what the user actually said. "
        "Do not invent details. Leave a field empty if the conversation does not support it."
    )
    composed = await structured.ainvoke(prompt)
    return composed.model_dump()


async def next_follow_up(kind: str, ticket: dict, missing: list[str], model=None) -> str:
    """Author one concise follow-up question for the first missing section."""
    model = model or get_chat_model("agent")
    target = missing[0] if missing else "detail"
    prompt = (
        f"You are collecting a {kind} ticket. Drafted so far: {ticket}. "
        f"Still missing: {missing}. Ask one concise, friendly question that gets the user to "
        f"supply '{target}'. Ask only that question."
    )
    response = await model.ainvoke(prompt)
    return response.content


__all__ = ["compose_ticket", "missing_sections", "next_follow_up"]
