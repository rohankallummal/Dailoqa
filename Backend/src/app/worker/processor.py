"""Resume-aware orchestration of a single ticket-creation job."""

from app.agent.dedupe import find_duplicate
from app.worker.create_step import create_ticket
from app.worker.link_step import link_ticket
from app.worker.notify import deliver_result
from app.worker.queue import complete_job


async def process_job(session, job, client, model=None) -> None:
    """Run one job to completion: dedupe (unless resuming) -> create/link -> notify."""
    if job.jira_key and job.action == "create":
        key = job.jira_key
        action = "create"
    elif job.jira_key and job.action == "link":
        await link_ticket(session, job, client, job.jira_key)
        key, action = job.jira_key, "link"
    else:
        verdict = await find_duplicate(job.payload["kind"], job.payload.get("fields", {}), client=client, model=model)
        if verdict.match_key:
            await link_ticket(session, job, client, verdict.match_key)
            key, action = verdict.match_key, "link"
        else:
            key = await create_ticket(session, job, client)
            action = "create"
    if action == "create":
        await deliver_result(session, job, "ticket_created", "Ticket created", f"Created {key}.", key)
    else:
        await deliver_result(session, job, "ticket_linked", "Linked to existing", f"Linked your report to {key}.", key)
    await complete_job(session, job.id)
