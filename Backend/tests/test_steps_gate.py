"""Covers the predicate that refuses a bug with no reproduction steps."""

import pytest

from app.agent.tools.jira import STEPS_REQUIRED, missing_steps


@pytest.mark.parametrize("steps", [None, [], [""], ["   "]])
def test_bug_without_usable_steps_is_refused(steps):
    assert missing_steps("bug", steps) is True


def test_bug_with_steps_is_allowed():
    assert missing_steps("bug", ["Open the dashboard"]) is False


@pytest.mark.parametrize("steps", [None, [], ["Open the dashboard"]])
def test_feature_is_never_gated(steps):
    assert missing_steps("feature", steps) is False


def test_refusal_carries_the_termination_sentence():
    assert "Sorry, we can’t proceed with raising this issue." in STEPS_REQUIRED
    assert "not filed" in STEPS_REQUIRED.lower()
