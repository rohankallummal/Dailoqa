"""Verification of the short-lived service JWT minted by the frontend."""

import logging
import time

import jwt
from fastapi import Header, HTTPException
from pydantic import BaseModel

from app.config import get_settings

logger = logging.getLogger(__name__)

SERVICE_JWT_AUDIENCE = "backend"


class AuthContext(BaseModel):
    """Identity derived from a verified service JWT."""

    user_sub: str
    user_id: str


def verify_service_token(token: str) -> AuthContext:
    """Verify an HS256 service token and return its identity.

    Raises a jwt.InvalidTokenError subclass when the token is invalid,
    expired, or carries the wrong audience.
    """
    payload = jwt.decode(
        token,
        get_settings().service_jwt_secret,
        algorithms=["HS256"],
        audience=SERVICE_JWT_AUDIENCE,
        options={"require": ["sub", "userId", "exp"]},
    )
    return AuthContext(user_sub=payload["sub"], user_id=payload["userId"])


def _reject_reason(token: str) -> str:
    """Describe a rejected token's timing and audience claims, without verifying it.

    TEMPORARY DIAGNOSTIC for intermittent 401 bursts. The signature is deliberately not
    checked here -- the caller has already established the token is invalid, and the goal
    is to learn why. The token itself is never logged, only its claims.
    """
    try:
        claims = jwt.decode(token, options={"verify_signature": False, "verify_aud": False})
    except jwt.InvalidTokenError:
        return "claims unreadable"
    now = int(time.time())
    exp = claims.get("exp")
    overdue = f"{now - exp}s" if isinstance(exp, int) else "n/a"
    return f"now={now} iat={claims.get('iat')} exp={exp} expired_by={overdue} aud={claims.get('aud')}"


async def require_auth(authorization: str | None = Header(default=None)) -> AuthContext:
    """FastAPI dependency that resolves the caller's AuthContext or 401s."""
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("auth 401: missing bearer token (header_present=%s)", authorization is not None)
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        return verify_service_token(token)
    except jwt.InvalidTokenError as error:
        logger.warning("auth 401: %s (%s); %s", type(error).__name__, error, _reject_reason(token))
        raise HTTPException(status_code=401, detail="invalid token") from error
