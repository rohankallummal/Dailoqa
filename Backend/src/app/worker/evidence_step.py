"""Idempotent upload of a job's evidence files to a Jira issue."""

from app.evidence.storage import evidence_dir, safe_filename

EVIDENCE_FIELD = "evidence"


def evidence_of(job) -> list[dict]:
    """Return the job's evidence manifest, or an empty list when it carries none."""
    return (job.payload.get("fields") or {}).get(EVIDENCE_FIELD) or []


async def attach_evidence(job, client, jira_key: str) -> None:
    """Upload the job's evidence to jira_key, skipping anything already attached.

    Names are reduced to a safe basename before being joined onto the evidence directory,
    so a manifest crafted with path separators cannot reach another conversation's files,
    and repeated names are collapsed so one file is never uploaded twice.

    The create path, the create resume path, and the link path all call this, and any of
    them may call it again on a retry. Checking what the issue already holds is what makes
    that safe, and is also what lets an upload that failed after the issue was created be
    retried rather than silently skipped.
    """
    evidence = evidence_of(job)
    if not evidence:
        return
    directory = evidence_dir(job.user_sub, job.conversation_id)
    already_attached = await client.list_attachment_filenames(jira_key)
    names = list(dict.fromkeys(safe_filename(item["name"]) for item in evidence))
    pending = [directory / name for name in names if name not in already_attached]
    existing = [path for path in pending if path.is_file()]
    if existing:
        await client.add_attachments(jira_key, existing)
