"""A `[Doc N]` with nothing to resolve it is not a citation.

Reported from a real conversation: an answer about creating agents in LangGraph carried "[Doc 1]"
and "[Doc 5]" and ended without a Sources legend. Every existing check passed it — a citation was
present, it was backed by passages the tools returned, and the attribution matched the sources —
because all three ask whether a tag *exists*, never whether it *resolves*.

For the reader that is worse than an uncited answer. There is no page to open, the numbers refer
to nothing on screen, and the answer looks sourced regardless.
"""

import pytest

from app.agent.middleware.grounding import _unresolved_citations

_LEGEND = "\nSources:\n[Doc 1] langgraph/LangGraph overview (/docs/langgraph)"


def test_tags_with_no_legend_at_all_are_unresolved():
    # The reported answer, reduced to its shape.
    answer = "LangGraph is an orchestration framework [Doc 1]. It mixes step types [Doc 5]."
    assert _unresolved_citations(answer) == {"1", "5"}


def test_a_tag_the_legend_covers_is_resolved():
    assert _unresolved_citations(f"Graphs are stateful [Doc 1].{_LEGEND}") == set()


def test_a_tag_missing_from_an_otherwise_present_legend_is_caught():
    # The partial case: a legend exists, so a "does it have Sources?" check would pass, but the
    # reader still cannot resolve [Doc 5].
    answer = f"Stateful [Doc 1]. Mixes steps [Doc 5].{_LEGEND}"
    assert _unresolved_citations(answer) == {"5"}


def test_an_answer_with_no_tags_is_never_flagged():
    # Declines and ticket replies cite nothing and owe nothing.
    assert _unresolved_citations("The documentation does not cover that.") == set()


def test_a_legend_entry_must_carry_a_route_to_count():
    # "[Doc 1] LangGraph overview" with no /docs path resolves to nothing the reader can open,
    # so it does not discharge the tag.
    assert _unresolved_citations("Stateful [Doc 1].\nSources:\n[Doc 1] LangGraph overview") == {"1"}


@pytest.mark.parametrize(
    "answer",
    [
        "Stateful [doc 1].\nSources:\n[doc 1] langgraph/Overview (/docs/langgraph)",
        "Stateful [Doc  1].\nSources:\n[Doc 1] langgraph/Overview (/docs/langgraph)",
        "Stateful [Doc 1].\nSources:\n[Doc 1] langgraph/Overview (/docs/langgraph#core-benefits)",
    ],
)
def test_spacing_case_and_anchors_do_not_break_resolution(answer):
    # The model varies all three, and a false bounce here costs a correct answer a retry.
    assert _unresolved_citations(answer) == set()
