"""The MDX normalizer, and the context prefix that ingestion and retrieval share.

These run entirely offline — no corpus, no database, no model — because a normalizer bug
does not announce itself. It corrupts the index quietly and only surfaces much later, as a
wrong answer, so it has to be provable before anything is ingested.
"""

import pytest

from app.config import get_settings
from app.rag.ingest import _flatten_mdx, _mask_code, _unmask_code
from app.rag.store import citation_label, context_prefix, strip_context_prefix

# Every character class the prose rules would otherwise mangle, inside one fence.
_HOSTILE_FENCE = """```cpp
#include <vector>
std::vector<int> v;
const agent = createAgent<MyState>();
// #fff  #!/bin/bash  %%not a comment%%  [[not a wikilink]]
<Tabs> is not a component in here
```"""


@pytest.fixture
def language(monkeypatch):
    """Pin docs_language; get_settings is cached and process-wide."""
    settings = get_settings()
    monkeypatch.setattr(settings, "docs_language", "python", raising=False)
    return settings


# --- 1. fence masking ------------------------------------------------------------------

def test_fenced_code_survives_byte_identical(language):
    # The bug this exists for: `<[^>]+>` turned `#include <vector>` into `#include` and
    # `std::vector<int>` into `std::vector`, silently, in the shipped normalizer.
    out = _flatten_mdx(f"Prose before.\n\n{_HOSTILE_FENCE}\n\nProse after.")
    assert _HOSTILE_FENCE in out


def test_inline_code_survives(language):
    out = _flatten_mdx("Use `Record<string, X>` and `<Tip>` carefully.")
    assert "`Record<string, X>`" in out
    assert "`<Tip>`" in out


def test_the_same_constructs_are_normalized_outside_fences(language):
    # Masking must not become a blanket exemption: outside a fence, a component is markup.
    out = _flatten_mdx(f"<Tip>Read this.</Tip>\n\n{_HOSTILE_FENCE}")
    assert "<Tip>" not in out.replace(_HOSTILE_FENCE, "")
    assert "Read this." in out
    assert _HOSTILE_FENCE in out


def test_masking_round_trips_exactly():
    original = f"a `x` b\n\n{_HOSTILE_FENCE}\n\nc"
    masked, saved = _mask_code(original)
    assert "```" not in masked and "`x`" not in masked
    assert _unmask_code(masked, saved) == original


# --- 2. language selection -------------------------------------------------------------

_PAIR = """:::python
PYTHON BODY
:::

:::js
JS BODY
:::"""


def test_only_the_configured_language_survives(language):
    out = _flatten_mdx(_PAIR)
    assert "PYTHON BODY" in out
    assert "JS BODY" not in out
    assert ":::" not in out


def test_flipping_the_setting_inverts_the_result(language, monkeypatch):
    monkeypatch.setattr(language, "docs_language", "js", raising=False)
    out = _flatten_mdx(_PAIR)
    assert "JS BODY" in out
    assert "PYTHON BODY" not in out


def test_language_selection_does_not_reach_outside_directive_blocks(language):
    # Scoped deliberately: 2 tsx fences in the real corpus sit outside any ::: block, so a
    # blanket "no TypeScript anywhere" rule would delete content this feature never owned.
    fence = "```tsx\nconst x = 1;\n```"
    out = _flatten_mdx(f"{_PAIR}\n\n{fence}")
    assert fence in out


# --- 3. Mintlify units -----------------------------------------------------------------

def test_components_and_imports_are_stripped(language):
    out = _flatten_mdx("import X from '/snippets/x.mdx';\n\n<CodeGroup>\n<Tip>Hi</Tip>\n</CodeGroup>")
    assert "import X" not in out
    assert "<CodeGroup>" not in out and "<Tip>" not in out
    assert "Hi" in out


def test_commonmark_autolinks_survive(language):
    # The narrowed JSX rule exists for this: `<[^>]+>` ate autolinks along with components.
    out = _flatten_mdx("Mail <user@example.com> or visit <https://example.com>.")
    assert "<user@example.com>" in out
    assert "<https://example.com>" in out


def test_link_targets_are_dropped_but_text_is_kept(language):
    # `/oss/langchain/agents` would otherwise enter the english tsvector as if it were prose.
    out = _flatten_mdx("See [the agents guide](/oss/langchain/agents).")
    assert "the agents guide" in out
    assert "/oss/langchain/agents" not in out


# --- 5. the shared context prefix ------------------------------------------------------

@pytest.mark.parametrize(
    "source_path, title, heading",
    [
        ("deep-agents/quickstart.md", "Quickstart", "Context management > Skills"),
        ("deep-agents/quickstart.md", "Quickstart", None),
        ("root-note.md", "Root", "Some heading"),
    ],
)
def test_prefix_round_trips(source_path, title, heading):
    # Writer and stripper must agree exactly; if they drift, the prefix leaks into every
    # passage a user reads and no test that mocks one side would notice.
    body = "The actual passage text."
    written = f"{context_prefix(source_path, title, heading)}\n\n{body}"
    assert strip_context_prefix(written, source_path, title, heading) == body


def test_the_topic_folder_disambiguates_colliding_titles():
    # Upstream ships a `Quickstart` for each topic, so the title alone identifies nothing.
    labels = {
        citation_label(f"{topic}/quickstart.md", "Quickstart", None)
        for topic in ("deep-agents", "langchain", "langgraph")
    }
    assert len(labels) == 3, f"citations must be distinguishable, got {labels}"


def test_prefix_and_label_agree_on_the_topic():
    prefix = context_prefix("langgraph/persistence.md", "Persistence", "Checkpointers")
    label = citation_label("langgraph/persistence.md", "Persistence", "Checkpointers")
    assert prefix.startswith("langgraph/Persistence")
    assert label.startswith("langgraph/Persistence")
