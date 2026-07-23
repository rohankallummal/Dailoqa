import pytest

from app.agent.dedupe import DedupeVerdict, build_jql, find_duplicate


def test_build_jql_targets_open_issues_of_type():
    jql = build_jql("bug", "KAN", "Bug")
    assert "project = KAN" in jql
    assert "Bug" in jql
    assert "Done" in jql


class _FakeClient:
    async def search_issues(self, jql, fields=None, max_results=20):
        return [{"key": "KAN-1", "fields": {"summary": "Search returns nothing"}}]

    issue_type_bug = "Bug"
    project_key = "KAN"

    def issue_type_for(self, kind):
        return "Bug"


class _FakeStructured:
    def __init__(self, verdict):
        self._v = verdict

    async def ainvoke(self, _msg):
        return self._v


class _FakeModel:
    def __init__(self, verdict):
        self._v = verdict

    def with_structured_output(self, _schema):
        return _FakeStructured(self._v)


@pytest.mark.asyncio
async def test_find_duplicate_returns_match_above_threshold():
    verdict = await find_duplicate(
        "bug",
        {"summary": "search empty until refresh"},
        client=_FakeClient(),
        model=_FakeModel(DedupeVerdict(match_key="KAN-1", confidence=0.9)),
    )
    assert verdict.match_key == "KAN-1"


@pytest.mark.asyncio
async def test_find_duplicate_drops_low_confidence():
    verdict = await find_duplicate(
        "bug",
        {"summary": "unrelated"},
        client=_FakeClient(),
        model=_FakeModel(DedupeVerdict(match_key="KAN-1", confidence=0.3)),
    )
    assert verdict.match_key is None
