"""FastAPI application entrypoint."""

from fastapi import Depends, FastAPI

from app.auth import AuthContext, require_auth

app = FastAPI(title="Dailoqa Agent Backend")


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}


@app.get("/me")
async def me(auth: AuthContext = Depends(require_auth)) -> dict[str, str]:
    """Return the identity derived from the caller's service JWT."""
    return {"user_sub": auth.user_sub, "user_id": auth.user_id}
