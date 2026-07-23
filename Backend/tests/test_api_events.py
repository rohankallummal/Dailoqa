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


def _token():
    import os

    secret = os.environ["SERVICE_JWT_SECRET"]
    return jwt.encode(
        {
            "sub": "sub-1",
            "userId": "u1",
            "aud": SERVICE_JWT_AUDIENCE,
            "iat": int(time.time()),
            "exp": int(time.time()) + 60,
        },
        secret,
        algorithm="HS256",
    )


def test_events_requires_auth():
    with TestClient(app) as client:
        assert client.get("/events").status_code == 401


@pytest.mark.asyncio
async def test_events_returns_the_sse_contract():
    from app.api.events import events
    from app.auth import AuthContext

    class _Request:
        async def is_disconnected(self):
            return True

    resp = await events(_Request(), AuthContext(user_sub="sub-events", user_id="u1"))
    assert resp.status_code == 200
    assert resp.media_type == "text/event-stream"
    assert resp.headers["content-type"].startswith("text/event-stream")
    assert resp.headers["cache-control"] == "no-cache, no-transform"
    assert resp.headers["x-accel-buffering"] == "no"
