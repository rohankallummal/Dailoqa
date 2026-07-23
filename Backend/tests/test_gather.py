import pytest

from app.agent.gather import REQUIRED_FIELDS, missing_fields, next_follow_up


def test_missing_fields_for_bug():
    missing = missing_fields("bug", {"summary": "x", "steps_to_reproduce": "", "expected": "y"})
    assert "steps_to_reproduce" in missing
    assert "actual" in missing
    assert "summary" not in missing


def test_required_fields_shape():
    assert set(REQUIRED_FIELDS) == {"bug", "feature"}
    assert "business_justification" in REQUIRED_FIELDS["feature"]


class _FakeModel:
    async def ainvoke(self, _messages):
        class _M:
            content = "Can you share the exact steps to reproduce?"
        return _M()


@pytest.mark.asyncio
async def test_next_follow_up_returns_question():
    q = await next_follow_up("bug", {"summary": "s"}, model=_FakeModel())
    assert "?" in q
