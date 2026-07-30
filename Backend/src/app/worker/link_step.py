"""Idempotent linking of a reporter to an existing Jira issue."""

from sqlalchemy import select

from app.db.models import Ticket, TicketReporter
from app.worker.evidence_step import attach_evidence
from app.worker.queue import set_job_action


async def link_ticket(session, job, client, match_key: str) -> None:
    """Attach the reporter to an existing issue: comment + label + reporter row, once.

    The ticket_reporters (ticket_id, user_sub) unique row is the authoritative link
    marker and makes this safe to retry (a rare duplicate comment is tolerated).

    Evidence is uploaded to the matched issue on every attempt, before the reporter row is
    consulted. The reporter row cannot gate it: an upload that failed after that row was
    written would never be retried, and the caller deletes the files once the job
    commits, so the screenshots proving a duplicate report would be lost for good.
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
    await attach_evidence(job, client, match_key)
    if existing is not None:
        return
    await client.add_comment(match_key, f"Also reported by {job.user_sub}")
    await client.add_labels(match_key, ["also-affected"])
    session.add(TicketReporter(ticket_id=ticket.id, user_sub=job.user_sub))
    await session.flush()
