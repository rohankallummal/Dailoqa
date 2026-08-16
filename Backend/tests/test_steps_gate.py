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


def test_refusal_says_nothing_was_filed_and_redirects_to_the_capture_tool():
    assert "not filed" in STEPS_REQUIRED.lower()
    assert "request_steps" in STEPS_REQUIRED


def test_refusal_does_not_invite_the_model_to_write_steps():
    assert "do not write the steps yourself" in STEPS_REQUIRED.lower()
