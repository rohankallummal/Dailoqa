"""Idempotent linking of a reporter to an existing Jira issue."""

import logging

from sqlalchemy import select

from app.db.models import Ticket, TicketReporter
from app.jira.adf import (
    SIMILAR_REPORTS_HEADING,
    append_nodes,
    has_heading,
    similar_reports_section,
)
from app.jira.similar_reports import SIMILAR_REPORTS_FILENAME, build_workbook
from app.worker.create_step import record_reporter
from app.worker.evidence_step import attach_evidence
from app.worker.queue import set_job_action

logger = logging.getLogger(__name__)


def _is_repeat_report(existing, job_created_at) -> bool:
    """Whether a reporter row predates its job, meaning an earlier report wrote it.

    A row written after the job was created belongs to this job's own earlier attempt, so a
    resumed first-time link is not mistaken for the same user reporting twice.
    """
    return existing is not None and existing.added_at < job_created_at


async def _reporter_rows(session, ticket_id: str) -> list[dict]:
    """Return every recorded reporter for a ticket, oldest first."""
    rows = (
        (
            await session.execute(
                select(TicketReporter)
                .where(TicketReporter.ticket_id == ticket_id)
                .order_by(TicketReporter.added_at)
            )
        )
        .scalars()
        .all()
    )
    return [
        {"name": row.user_name or row.user_sub, "oauth_id": row.user_sub, "reported_at": row.added_at}
        for row in rows
    ]


async def _replace_spreadsheet(client, issue_key: str, rows: list[dict]) -> None:
    """Upload a freshly generated workbook, removing the one it supersedes."""
    for attachment in await client.list_attachments(issue_key):
        if attachment["filename"] == SIMILAR_REPORTS_FILENAME:
            await client.delete_attachment(attachment["id"])
    await client.add_attachment_bytes(issue_key, SIMILAR_REPORTS_FILENAME, build_workbook(rows))


async def _ensure_similar_reports_section(client, issue_key: str) -> None:
    """Add the Similar Reports heading to the description, once.

    Presence is read from the live issue rather than tracked locally, so a retry that
    already added the section does not write a second copy.
    """
    document = await client.get_description(issue_key)
    if has_heading(document, SIMILAR_REPORTS_HEADING):
        return
    await client.update_description(
        issue_key, append_nodes(document, similar_reports_section(SIMILAR_REPORTS_FILENAME))
    )


async def update_similar_reports(session, client, ticket_id: str, issue_key: str) -> None:
    """Refresh the Similar Reports spreadsheet and section once a second user reports.

    Failures are logged and swallowed. The reporter link and the evidence upload are the
    load-bearing work, and the whole workbook is regenerated from the reporter rows on the
    next link, so a failed attempt heals itself rather than costing the job an attempt.
    """
    rows = await _reporter_rows(session, ticket_id)
    if len(rows) < 2:
        return
    try:
        await _replace_spreadsheet(client, issue_key, rows)
        await _ensure_similar_reports_section(client, issue_key)
    except Exception as error:  # noqa: BLE001
        logger.warning("similar reports update failed for %s: %s", issue_key, error)


async def link_ticket(session, job, client, match_key: str) -> bool:
    """Attach the reporter to an existing issue: comment + label + reporter row, once.

    Returns whether this link should be reported as fresh. False means the same user had
    already reported the issue before this job existed, which the caller turns into the
    already-reported outcome rather than a link.

    The ticket_reporters (ticket_id, user_sub) unique row is the authoritative link
    marker and makes this safe to retry (a rare duplicate comment is tolerated).

    Evidence is uploaded to the matched issue on every attempt, before the reporter row is
    consulted. The reporter row cannot gate it: an upload that failed after that row was
    written would never be retried, and the caller deletes the files once the job
    commits, so the screenshots proving a duplicate report would be lost for good.

    The Similar Reports refresh runs on every attempt for the same reason: it is driven by
    the reporter rows, so a retry after the row was written still produces the spreadsheet.
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
    repeat = _is_repeat_report(existing, job.created_at)
    await set_job_action(session, job.id, "link", jira_key=match_key)
    await attach_evidence(job, client, match_key)
    if existing is None:
        reporter = job.payload.get("reporter", {})
        reporter_name = reporter.get("name") or job.user_sub
        await client.add_comment(match_key, f"Also reported by {reporter_name}")
        await client.add_labels(match_key, ["also-affected"])
        await record_reporter(session, ticket.id, job.user_sub, reporter_name)
    await update_similar_reports(session, client, ticket.id, match_key)
    return not repeat
