import os
import time

import jwt
import pytest
from fastapi.testclient import TestClient

from app.auth import SERVICE_JWT_AUDIENCE
from app.config import get_settings
from app.main import app


@pytest.fixture(autouse=True)
def _env(base_env):
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _token() -> str:
    payload = {
        "sub": "google-sub-123",
        "userId": "user-uuid-1",
        "aud": SERVICE_JWT_AUDIENCE,
        "iat": int(time.time()),
        "exp": int(time.time()) + 60,
    }
    return jwt.encode(payload, os.environ["SERVICE_JWT_SECRET"], algorithm="HS256")


def test_health_is_public():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_me_requires_auth():
    client = TestClient(app)
    assert client.get("/me").status_code == 401


def test_me_returns_identity_with_token():
    client = TestClient(app)
    response = client.get("/me", headers={"Authorization": f"Bearer {_token()}"})
    assert response.status_code == 200
    assert response.json() == {"user_sub": "google-sub-123", "user_id": "user-uuid-1"}
