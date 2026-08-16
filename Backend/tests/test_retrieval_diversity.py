"""Reserved slots, so one page cannot take every slot in the result set.

Chunks are ranked individually, so a page whose every chunk matches a query sweeps the whole
top-k and the second subject of a two-subject question is never retrieved at all. Measured
against the live index before this existed:

    "can a subagent use a sandbox?"        ranks 1-8 all sandboxes.md, subagents.md at 11
    "how do checkpointers and stores..."   stores.md at rank 6, one past the cutoff
    "...Skill inside a LangGraph checkpointer"   skills.md at rank 10

The middle one is the reason this is not filed as a hallucination guard: it is an ordinary
documented question, and the agent was answering it having never seen the Stores page.

These drive the selection directly with synthetic chunks. Whether *retrieval* ranks a given page
at 6 or 11 is a property of the index and belongs to the live tests; what belongs here is that
given such a ranking, the selection reaches past the monopoly.
"""

import pytest

from app.rag.store import RetrievedChunk, _with_reserved_slots


def _chunks(*source_paths: str) -> list[RetrievedChunk]:
    """Candidates in rank order, one per source path given."""
    return [
        RetrievedChunk(
            id=f"c{i}", source_path=path, title="T", heading=f"h{i}", content="body", score=1 / (i + 1)
        )
        for i, path in enumerate(source_paths)
    ]


def _paths(chunks) -> list[str]:
    return [c.source_path for c in chunks]


def test_a_monopolising_page_does_not_take_every_slot():
    # "can a subagent use a sandbox?" -- eight sandboxes chunks, subagents far below.
    candidates = _chunks(*(["deep-agents/sandboxes.md"] * 8), "deep-agents/subagents.md")
    chosen = _with_reserved_slots(candidates, k=5, reserved=2)

    assert "deep-agents/subagents.md" in _paths(chosen)
    assert len(chosen) == 5


def test_the_page_slot_recovers_a_second_page_in_the_same_topic():
    # "how do checkpointers and stores differ?" -- both LangGraph, so only the page slot helps.
    candidates = _chunks(
        "langgraph/persistence.md",
        "langgraph/checkpointers.md",
        "langgraph/persistence.md",
        "langgraph/checkpointers.md",
        "langgraph/checkpointers.md",
        "langgraph/stores.md",  # rank 6, one past the live cutoff
    )
    chosen = _with_reserved_slots(candidates, k=5, reserved=2)

    assert "langgraph/stores.md" in _paths(chosen)


def test_the_topic_slot_reaches_a_page_the_page_slot_cannot():
    """The cross-topic half, and why one reserved slot is not enough.

    "Use a Skill inside a LangGraph checkpointer" has four LangGraph terms against one Deep
    Agents term, so the whole top of the list is LangGraph. A page slot is spent on yet another
    LangGraph page -- there are plenty -- and only a topic slot reaches deep-agents/skills.md.
    """
    candidates = _chunks(
        "langgraph/use-subgraphs.md",
        "langgraph/persistence.md",
        "langgraph/persistence.md",
        "langgraph/stores.md",
        "langgraph/checkpointers.md",
        "langgraph/checkpointers.md",
        "langgraph/use-subgraphs.md",
        "langgraph/checkpointers.md",
        "langgraph/persistence.md",
        "deep-agents/skills.md",  # rank 10
    )
    chosen = _with_reserved_slots(candidates, k=5, reserved=2)
    assert "deep-agents/skills.md" in _paths(chosen)

    # One slot is genuinely insufficient here, which is what justifies reserving two.
    one_slot = _with_reserved_slots(candidates, k=5, reserved=1)
    assert "deep-agents/skills.md" not in _paths(one_slot)


def test_the_top_ranked_chunks_are_never_displaced():
    # Reserved slots come off the bottom. The best matches are why the answer is right at all.
    candidates = _chunks(
        "a/one.md", "a/one.md", "a/one.md", "a/one.md", "a/one.md", "b/two.md", "c/three.md"
    )
    chosen = _with_reserved_slots(candidates, k=5, reserved=2)

    assert [c.id for c in chosen[:3]] == ["c0", "c1", "c2"]


def test_a_single_subject_result_is_returned_whole_when_nothing_else_qualifies():
    # No other page or topic cleared the gate, so both slots fall back to rank order and the
    # result is exactly what it would have been. Diversity is never manufactured.
    candidates = _chunks(*(["deep-agents/skills.md"] * 7))
    chosen = _with_reserved_slots(candidates, k=5, reserved=2)

    assert [c.id for c in chosen] == ["c0", "c1", "c2", "c3", "c4"]


@pytest.mark.parametrize("reserved", [0, 1, 2, 5])
def test_the_result_is_always_k_chunks_with_no_repeats(reserved):
    candidates = _chunks(
        "a/one.md", "a/one.md", "b/two.md", "a/one.md", "c/three.md", "b/two.md", "d/four.md"
    )
    chosen = _with_reserved_slots(candidates, k=5, reserved=reserved)

    assert len(chosen) == 5
    assert len({c.id for c in chosen}) == 5, "a chunk was selected twice"


def test_disabling_the_slots_restores_pure_rank_order():
    candidates = _chunks(*(["a/one.md"] * 6), "b/two.md")
    assert _with_reserved_slots(candidates, k=5, reserved=0) == candidates[:5]


def test_fewer_candidates_than_k_are_returned_untouched():
    candidates = _chunks("a/one.md", "b/two.md")
    assert _with_reserved_slots(candidates, k=5, reserved=2) == candidates
