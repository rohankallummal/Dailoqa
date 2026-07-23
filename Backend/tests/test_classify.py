import pytest

from app.agent.classify import Classification, classify_message


class _FakeStructured:
    def __init__(self, result):
        self._result = result

    async def ainvoke(self, _text):
        return self._result


class _FakeModel:
    def __init__(self, result):
        self._result = result

    def with_structured_output(self, _schema):
        return _FakeStructured(self._result)


@pytest.mark.asyncio
async def test_classifies_bug():
    model = _FakeModel(Classification(kind="bug", reason="defect"))
    result = await classify_message("Search returns nothing until refresh", model=model)
    assert result.kind == "bug"


@pytest.mark.asyncio
async def test_classifies_feature():
    model = _FakeModel(Classification(kind="feature", reason="enhancement"))
    result = await classify_message("Please add dark mode", model=model)
    assert result.kind == "feature"
