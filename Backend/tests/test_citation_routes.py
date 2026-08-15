"""Citations name a page the reader can open, and degrade sanely when they cannot.

Offline: the manifest is a file, so none of this needs a database or a model.
"""

import json

import pytest

from app.config import get_settings
from app.rag import routes
from app.rag.store import citation_label
from tests.conftest import corpus_page


@pytest.fixture(autouse=True)
def _clean_route_cache():
    """The manifest is cached process-wide; tests that repoint DOCS_PATH must not leak."""
    routes.reset_route_cache()
    yield
    routes.reset_route_cache()


@pytest.fixture
def manifest_at(tmp_path, monkeypatch):
    """Point DOCS_PATH at a throwaway corpus so the manifest beside it can be controlled."""

    def build(manifest: object | None) -> None:
        corpus = tmp_path / "formatted"
        corpus.mkdir(parents=True, exist_ok=True)
        if manifest is not None:
            written = manifest if isinstance(manifest, str) else json.dumps(manifest)
            (tmp_path / "manifest.json").write_text(written, encoding="utf-8")
        monkeypatch.setattr(get_settings(), "docs_path", str(corpus), raising=False)
        routes.reset_route_cache()

    return build


# --- the mapping itself -----------------------------------------------------------------

def test_a_citation_carries_the_documentation_route():
    label = citation_label(corpus_page("subagents"), "Subagents", "Using CompiledSubAgent")
    assert "(/docs/deepagents/subagents" in label
    assert "Subagents - Using CompiledSubAgent" in label


@pytest.mark.parametrize(
    "slug, topic, route",
    [
        # The five whose route cannot be derived from the filename -- the reason a manifest
        # exists at all. A pattern-matching implementation gets every one of these wrong.
        ("multimodal", "deep-agents", "/docs/deepagents/multimodality"),
        # the only page in a sub-folder, so its slug carries one too
        ("middleware/built-in", "langchain", "/docs/langchain/prebuilt-middleware"),
        ("use-subgraphs", "langgraph", "/docs/langgraph/subgraphs"),
        ("checkpointers", "langgraph", "/docs/langgraph/checkpoints"),
        ("overview", "langgraph", "/docs/langgraph"),
    ],
)
def test_routes_that_are_not_derivable_from_the_filename(slug, topic, route):
    assert citation_label(corpus_page(slug, topic), "T", None).endswith(f"({route})")


def test_the_three_overview_pages_cite_distinguishably():
    labels = {
        citation_label(corpus_page("overview", topic), "Overview", None)
        for topic in ("deep-agents", "langchain", "langgraph")
    }
    assert len(labels) == 3, f"overview citations must differ, got {labels}"


# --- the fallback, which is a permanent safety net rather than a stub --------------------

def test_an_unmapped_page_falls_back_to_the_filename_label(manifest_at):
    # The drift case: the corpus moved on and the manifest did not. An answer citing a
    # slightly stale-looking source beats no answer, so this must not raise or return empty.
    manifest_at({"pages": [{"vault_path": "other/page.md", "frontend_route": "/docs/other"}]})
    label = citation_label("deep-agents/skills.md", "Skills", "How skills work")
    assert label == "deep-agents/Skills - How skills work"
    assert "(" not in label


def test_a_missing_manifest_degrades_instead_of_failing(manifest_at):
    manifest_at(None)
    assert citation_label("deep-agents/skills.md", "Skills", None) == "deep-agents/Skills"


def test_a_corrupt_manifest_degrades_instead_of_failing(manifest_at):
    # Costing clickable citations is acceptable; costing the ability to answer is not.
    manifest_at("{ this is not json")
    assert citation_label("deep-agents/skills.md", "Skills", None) == "deep-agents/Skills"


def test_the_fallback_still_disambiguates_colliding_titles(manifest_at):
    # Without a route to tell them apart, the topic folder is the only thing left doing it.
    manifest_at({"pages": []})
    labels = {
        citation_label(f"{topic}/overview.md", "Overview", None)
        for topic in ("deep-agents", "langchain", "langgraph")
    }
    assert len(labels) == 3


# --- section anchors ---------------------------------------------------------------------

def test_the_intro_sentinel_matches_store():
    # routes.py duplicates INTRO_HEADING because store imports it, not the other way round.
    # This is what stops the two copies drifting silently.
    from app.rag.store import INTRO_HEADING

    assert routes._INTRO_HEADING == INTRO_HEADING


@pytest.mark.parametrize(
    "heading, anchor",
    [
        ("Using CompiledSubAgent", "using-compiledsubagent"),
        # Only the leaf is a heading on the page; the trail is the path to it.
        ("Context management > Summarization and context offloading", "summarization-and-context-offloading"),
        ("Add supporting resources > `references/`", "references"),
        ("Row key / index design", "row-key--index-design"),
        (None, None),
        ("(intro)", None),  # a page's lead-in is not a heading, so there is nothing to link to
    ],
)
def test_anchor_matches_the_docs_site_slugger(heading, anchor):
    assert routes.anchor_for(heading) == anchor


def test_a_citation_points_at_the_section_not_just_the_page():
    label = citation_label(corpus_page("subagents"), "Subagents", "Using CompiledSubAgent")
    assert label.endswith("(/docs/deepagents/subagents#using-compiledsubagent)")


def test_a_page_with_no_heading_cites_the_bare_route():
    assert citation_label(corpus_page("overview", "langgraph"), "Overview", None).endswith("(/docs/langgraph)")


def test_every_indexed_page_is_mapped():
    # If this fails, some page's citations have silently fallen back to filenames.
    from tests.conftest import corpus_sources

    unmapped = [path for path in corpus_sources() if routes.route_for(path) is None]
    assert not unmapped, f"pages with no documentation route: {unmapped}"
