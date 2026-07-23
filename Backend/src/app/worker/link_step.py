"""Idempotent linking of a reporter to an existing Jira issue."""

from sqlalchemy import select

from app.db.models import Ticket, TicketReporter
from app.worker.queue import set_job_action


async def link_ticket(session, job, client, match_key: str) -> None:
    """Attach the reporter to an existing issue: comment + label + reporter row, once.

    The ticket_reporters (ticket_id, user_sub) unique row is the authoritative link
    marker and makes this safe to retry (a rare duplicate comment is tolerated).
    """
    ticket = (await session.execute(select(Ticket).where(Ticket.jira_key == match_key))).scalar_one_or_none()
    if ticket is None:
        ticket = Ticket(jira_key=match_key, type=job.payload["kind"], title=match_key)
        session.add(ticket)
        await session.flush()
    existing = (
        await session.execute(
            select(TicketReporter).where(
                TicketReporter.ticket_id == ticket.id, TicketReporter.user_sub == job.user_sub
            )
        )
    ).scalar_one_or_none()
    await set_job_action(session, job.id, "link", jira_key=match_key)
    if existing is not None:
        return
    await client.add_comment(match_key, f"Also reported by {job.user_sub}")
    await client.add_labels(match_key, ["also-affected"])
    session.add(TicketReporter(ticket_id=ticket.id, user_sub=job.user_sub))
    await session.flush()
