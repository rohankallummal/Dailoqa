"""Idempotent Jira issue creation for a job."""

from sqlalchemy.dialects.postgresql import insert

from app.db.models import Ticket
from app.worker.evidence_step import EVIDENCE_FIELD, attach_evidence, evidence_of
from app.worker.queue import set_job_action


def _describe(fields: dict) -> str:
    """Render the ticket description, excluding the evidence manifest.

    The manifest becomes its own ADF section, so leaving it in would print a raw list
    into the description body.
    """
    return "\n".join(f"{key}: {value}" for key, value in fields.items() if key != EVIDENCE_FIELD)


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
        await attach_evidence(job, client, job.jira_key)
        return job.jira_key
    kind = job.payload["kind"]
    fields = job.payload.get("fields", {})
    summary = fields.get("summary", "Untitled")
    description = _describe(fields)
    issue_type = client.issue_type_for(kind)
    result = await client.create_issue(
        issue_type, summary, description, labels=["agent-filed"], evidence=evidence_of(job)
    )
    key = result["key"]
    await set_job_action(session, job.id, "create", jira_key=key)
    await session.commit()
    await session.execute(
        insert(Ticket)
        .values(jira_key=key, type=kind, title=summary, summary=description, conversation_id=job.conversation_id)
        .on_conflict_do_nothing(index_elements=["jira_key"])
    )
    job.jira_key = key
    job.action = "create"
    await session.commit()
    await attach_evidence(job, client, key)
    return key
