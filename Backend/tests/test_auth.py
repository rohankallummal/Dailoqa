import time

import jwt
import pytest
from fastapi import HTTPException

from app.auth import AuthContext, SERVICE_JWT_AUDIENCE, require_auth, verify_service_token

SECRET = "test-secret"


def _token(claims: dict, secret: str = SECRET) -> str:
    payload = {
        "sub": "google-sub-123",
        "userId": "user-uuid-1",
        "aud": SERVICE_JWT_AUDIENCE,
        "iat": int(time.time()),
        "exp": int(time.time()) + 60,
    }
    payload.update(claims)
    return jwt.encode(payload, secret, algorithm="HS256")


@pytest.fixture(autouse=True)
def _auth_env(base_env):
    from app.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_verify_valid_token_returns_context():
    ctx = verify_service_token(_token({}))
    assert ctx == AuthContext(user_sub="google-sub-123", user_id="user-uuid-1")


def test_verify_wrong_audience_rejected():
    with pytest.raises(jwt.InvalidAudienceError):
        verify_service_token(_token({"aud": "frontend"}))


def test_verify_expired_rejected():
    with pytest.raises(jwt.ExpiredSignatureError):
        verify_service_token(_token({"exp": int(time.time()) - 5}))


def test_verify_bad_signature_rejected():
    with pytest.raises(jwt.InvalidSignatureError):
        verify_service_token(_token({}, secret="wrong-secret"))


@pytest.mark.asyncio
async def test_require_auth_missing_header_401():
    with pytest.raises(HTTPException) as exc:
        await require_auth(authorization=None)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_require_auth_valid_bearer_returns_context():
    ctx = await require_auth(authorization=f"Bearer {_token({})}")
    assert ctx.user_sub == "google-sub-123"
