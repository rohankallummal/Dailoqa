"""Idempotent Jira issue creation for a job."""

from sqlalchemy.dialects.postgresql import insert

from app.db.models import Ticket
from app.worker.queue import set_job_action


async def create_ticket(session, job, client) -> str:
    """Create a Jira issue for the job (or resume if already created); return the key.

    Persists job.jira_key in its own commit the instant create_issue returns, so a
    crash-then-retry resumes instead of double-filing.
    """
    if job.jira_key:
        return job.jira_key
    kind = job.payload["kind"]
    fields = job.payload.get("fields", {})
    summary = fields.get("summary", "Untitled")
    description = "\n".join(f"{k}: {v}" for k, v in fields.items())
    issue_type = client.issue_type_for(kind)
    result = await client.create_issue(issue_type, summary, description, labels=["agent-filed"])
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
    return key
