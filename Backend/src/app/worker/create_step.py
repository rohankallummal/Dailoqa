"""Idempotent Jira issue creation for a job."""

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.db.models import Ticket, TicketReporter
from app.jira.adf import build_ticket_document
from app.worker.evidence_step import attach_evidence, evidence_of, original_names
from app.worker.queue import set_job_action


async def record_reporter(session, ticket_id: str, user_sub: str, user_name: str) -> None:
    """Record a reporter against a ticket exactly once.

    Every reporter is recorded, the one who filed the issue included, because the Similar
    Reports spreadsheet must list them all once a second user reports the same problem.
    """
    existing = (
        await session.execute(
            select(TicketReporter).where(
                TicketReporter.ticket_id == ticket_id, TicketReporter.user_sub == user_sub
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        return
    session.add(TicketReporter(ticket_id=ticket_id, user_sub=user_sub, user_name=user_name))
    await session.flush()


async def create_ticket(session, job, client) -> str:
    """Create a Jira issue for the job (or resume if already created); return the key.

    Persists job.jira_key in its own commit the instant create_issue returns, so a
    crash-then-retry resumes instead of double-filing. The Ticket row is committed
    before attachments are uploaded: an upload failure rolls back the session, and the
    resume path returns early on job.jira_key, so an uncommitted Ticket would be lost
    for good.

    The resume path re-runs the attachment upload rather than returning the key straight
    away, because that is the only thing left to do for an issue that was created but
    whose evidence never made it. attach_evidence skips whatever the issue already holds,
    so a resume after a fully successful upload costs one API call and changes nothing.
    """
    if job.jira_key:
        resumed = original_names([item["name"] for item in evidence_of(job)])
        await attach_evidence(job, client, job.jira_key, resumed)
        return job.jira_key
    kind = job.payload["kind"]
    ticket = job.payload.get("ticket", {})
    reporter = job.payload.get("reporter", {})
    evidence = evidence_of(job)
    title = ticket.get("title") or "Untitled"
    document = build_ticket_document(kind, ticket, job.payload.get("client_environment", {}), reporter)
    issue_type = client.issue_type_for(kind)
    result = await client.create_issue(issue_type, title, document, labels=["agent-filed"])
    key = result["key"]
    await set_job_action(session, job.id, "create", jira_key=key)
    await session.commit()
    await session.execute(
        insert(Ticket)
        .values(
            jira_key=key,
            type=kind,
            title=title,
            summary=ticket.get("summary") or ticket.get("feature"),
            conversation_id=job.conversation_id,
        )
        .on_conflict_do_nothing(index_elements=["jira_key"])
    )
    stored = (await session.execute(select(Ticket).where(Ticket.jira_key == key))).scalar_one()
    await record_reporter(session, stored.id, job.user_sub, reporter.get("name") or job.user_sub)
    job.jira_key = key
    job.action = "create"
    await session.commit()
    await attach_evidence(job, client, key, original_names([item["name"] for item in evidence]))
    return key
