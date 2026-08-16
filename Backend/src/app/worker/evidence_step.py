"""Idempotent upload of a job's evidence files to a Jira issue."""

from pathlib import Path

from app.evidence.storage import evidence_dir, safe_filename

EVIDENCE_FIELD = "evidence"


def evidence_of(job) -> list[dict]:
    """Return the job's evidence manifest, or an empty list when it carries none."""
    return job.payload.get(EVIDENCE_FIELD) or []


def reporter_prefix(user_name: str, user_sub: str) -> str:
    """Build the filename prefix tying a reporter's evidence to their spreadsheet row.

    The Affected Users sheet lists the same name and id, so a triager reading a filename
    can tell who supplied it without opening the spreadsheet.
    """
    return f"{safe_filename(user_name)}-{safe_filename(user_sub)}"


def upload_names(prefix: str, names: list[str]) -> dict[str, str]:
    """Map each source filename to its {prefix}-{n} upload name, numbered from 1.

    Sorting makes the mapping deterministic, which is what lets a retry compute the same
    names and skip whatever the issue already holds instead of uploading a second copy.
    """
    ordered = sorted(dict.fromkeys(safe_filename(name) for name in names))
    return {
        name: f"{prefix}-{index}{Path(name).suffix}"
        for index, name in enumerate(ordered, start=1)
    }


def original_names(names: list[str]) -> dict[str, str]:
    """Map each source filename to itself, for the path that keeps original names."""
    return {safe_filename(name): safe_filename(name) for name in names}


async def attach_evidence(job, client, jira_key: str, names: dict[str, str]) -> None:
    """Upload the job's evidence under the given upload names, skipping what is attached.

    Names are reduced to a safe basename before being joined onto the evidence directory,
    so a manifest crafted with path separators cannot reach another conversation's files,
    and repeated names are collapsed so one file is never uploaded twice.

    The create path, the create resume path, and the link path all call this, and any of
    them may call it again on a retry. Checking what the issue already holds is what makes
    that safe, and is also what lets an upload that failed after the issue was created be
    retried rather than silently skipped.
    """
    if not names:
        return
    directory = evidence_dir(job.user_sub, job.conversation_id)
    already_attached = await client.list_attachment_filenames(jira_key)
    pending = [
        (upload, directory / source)
        for source, upload in sorted(names.items())
        if upload not in already_attached
    ]
    existing = [(upload, path) for upload, path in pending if path.is_file()]
    if existing:
        await client.add_named_attachments(jira_key, existing)
