"""Inbound Jira webhook that keeps local tickets in step with issue deletions."""

import hashlib
import hmac
import logging

from fastapi import APIRouter, Header, HTTPException, Request
from sqlalchemy import delete

from app.config import get_settings
from app.db.base import async_session
from app.db.models import Ticket

logger = logging.getLogger(__name__)

router = APIRouter()

ISSUE_DELETED_EVENT = "jira:issue_deleted"


def _signature_matches(body: bytes, header: str | None) -> bool:
    """Whether a delivery carries a valid HMAC-SHA256 signature over its raw body.

    Jira signs the body with the shared secret and sends the digest as
    ``sha256=<hex>``. An unset secret rejects every delivery rather than
    silently accepting unauthenticated callers.

    The comparison is done on bytes. ``compare_digest`` raises TypeError when handed a str
    that is not ASCII-only, which would turn a crafted header on this unauthenticated
    endpoint into a 500 with a traceback instead of the 401 it deserves.
    """
    secret = get_settings().jira_webhook_secret
    if not secret or not header:
        return False
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    provided = header.removeprefix("sha256=").strip()
    return hmac.compare_digest(expected.encode(), provided.encode())


@router.post("/jira/webhook")
async def jira_webhook(request: Request, x_hub_signature: str | None = Header(default=None)) -> dict:
    """Drop the local ticket when Jira reports its issue was deleted.

    Runs outside ``require_auth``: Jira sends no bearer token, so the shared-secret
    signature is the only trust boundary. Unrecognised events are acknowledged
    rather than rejected so Jira does not retry or deactivate the webhook.
    """
    body = await request.body()
    if not _signature_matches(body, x_hub_signature):
        raise HTTPException(status_code=401, detail="invalid signature")
    payload = await request.json()
    if payload.get("webhookEvent") != ISSUE_DELETED_EVENT:
        return {"handled": False}
    jira_key = (payload.get("issue") or {}).get("key")
    if not jira_key:
        return {"handled": False}
    async with async_session() as session:
        result = await session.execute(delete(Ticket).where(Ticket.jira_key == jira_key))
        await session.commit()
    logger.info("jira issue %s deleted; removed %s local ticket(s)", jira_key, result.rowcount)
    return {"handled": True, "jira_key": jira_key, "deleted": result.rowcount}
