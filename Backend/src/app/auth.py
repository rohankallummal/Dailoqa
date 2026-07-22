"""Verification of the short-lived service JWT minted by the frontend."""

import jwt
from fastapi import Header, HTTPException
from pydantic import BaseModel

from app.config import get_settings

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
        options={"require": ["sub", "userId"]},
    )
    return AuthContext(user_sub=payload["sub"], user_id=payload["userId"])


async def require_auth(authorization: str | None = Header(default=None)) -> AuthContext:
    """FastAPI dependency that resolves the caller's AuthContext or 401s."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        return verify_service_token(token)
    except jwt.InvalidTokenError as error:
        raise HTTPException(status_code=401, detail="invalid token") from error
