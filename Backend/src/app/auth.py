"""Verification of the short-lived service JWT minted by the frontend."""

import logging

import jwt
from fastapi import Header, HTTPException
from pydantic import BaseModel

from app.config import get_settings

logger = logging.getLogger(__name__)

SERVICE_JWT_AUDIENCE = "backend"

CLOCK_SKEW_LEEWAY_SECONDS = 60


class AuthContext(BaseModel):
    """Identity derived from a verified service JWT."""

    user_sub: str
    user_name: str


def verify_service_token(token: str) -> AuthContext:
    """Verify an HS256 service token and return its identity.

    Raises a jwt.InvalidTokenError subclass when the token is invalid,
    expired, or carries the wrong audience.

    The name claim is optional and falls back to the subject, so a token minted before
    the reporter's display name was carried still verifies.

    Leeway absorbs clock drift between the frontend that mints the token and this
    process. Tokens live two minutes, and without leeway a container running even a few
    seconds ahead of its host rejects tokens that were valid when issued, which is what
    the intermittent 401 bursts turned out to be.
    """
    payload = jwt.decode(
        token,
        get_settings().service_jwt_secret,
        algorithms=["HS256"],
        audience=SERVICE_JWT_AUDIENCE,
        leeway=CLOCK_SKEW_LEEWAY_SECONDS,
        options={"require": ["sub", "userId", "exp"]},
    )
    return AuthContext(
        user_sub=payload["sub"],
        user_name=payload.get("name") or payload["sub"],
    )


async def require_auth(authorization: str | None = Header(default=None)) -> AuthContext:
    """FastAPI dependency that resolves the caller's AuthContext or 401s."""
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("auth 401: missing bearer token (header_present=%s)", authorization is not None)
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        return verify_service_token(token)
    except jwt.InvalidTokenError as error:
        logger.warning("auth 401: %s (%s)", type(error).__name__, error)
        raise HTTPException(status_code=401, detail="invalid token") from error
