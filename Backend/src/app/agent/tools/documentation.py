"""Tools that retrieve from the documentation knowledge store.

These are the agent's only window onto the documentation. Everything they return carries
the published URL of the passage it came from, so an answer can cite the exact section it
was built from and a reader can check it.
"""

from langchain.tools import tool

from app.knowledge import Hit, Page, Section, outline, page, search

_PREVIEW_CHARACTERS = 600
_SECTION_CHARACTERS = 12000
_MAX_RESULTS = 8

_RULES = """
---
Rules for answering from this content:
1. Every fact in your answer must come from text above. You have no other knowledge of
   LangGraph, LangChain, or DeepAgents. Do not add, generalise, or fill gaps from memory.
2. If the content above does not answer the question, say the documentation does not cover
   it and stop. Do not offer a partial answer from your own knowledge, and do not hedge
   with "typically" or "generally".
3. If the question asked several things and the content covers only some of them, answer
   those and say plainly which part the documentation does not cover. Dropping the part
   you cannot answer reads as though it was never asked, which misleads the user.
4. To cite a section, copy its `cite as` line into your answer exactly as written. It is
   already a finished Markdown link. Do not rebuild it from the parts, do not add a
   domain, and do not write a URL of your own. Any citation containing "http" is invented.
"""


def _with_rules(body: str) -> str:
    """Attach the answering rules to a tool result.

    The rules live here rather than only in the DocQA skill because the model reaches these
    tools whether or not it loaded that skill, and a tool result is the last thing it reads
    before it answers. Grounding that depends on the model having chosen to read a skill
    first is grounding that fails silently.
    """
    return f"{body}\n{_RULES}"


def _preview(text: str) -> str:
    """Shorten a section to a preview that shows what it covers without spending context."""
    if len(text) <= _PREVIEW_CHARACTERS:
        return text
    return text[:_PREVIEW_CHARACTERS].rstrip() + " […]"


def _render_hit(position: int, hit: Hit) -> str:
    """Render one search result with everything needed to cite it or read it in full."""
    section = hit.section
    lines = [
        f"### Result {position}: {section.label}",
        f"- page: {section.path}",
        f"- section: {section.anchor or '(introduction)'}",
        f"- cite as: {section.markdown_citation}",
        f"- relevance: {hit.score:.1f}",
        f"- query terms found: {', '.join(hit.matched) or 'none'}",
    ]
    if hit.missing:
        lines.append(f"- query terms absent: {', '.join(hit.missing)}")
    if section.code_examples:
        lines.append(f"- code examples in this section: {', '.join(section.code_examples)}")
    lines.extend(["", _preview(section.text)])
    return "\n".join(lines)


@tool
async def search_documentation(query: str, product: str | None = None) -> str:
    """Search the documentation knowledge store for passages relevant to a question.

    This is the only source you may answer documentation questions from. Search before
    answering anything about LangGraph, LangChain, or DeepAgents, and never answer such a
    question from memory.

    Each result is one section of one documentation page and carries the ``link`` you must
    cite, plus which of the question's terms that section actually contains. A result whose
    only matched term is incidental to the question means the store does not cover it. An
    empty result means the same thing. Results are previews: call ``read_documentation``
    for the full text of any section you intend to answer from.

    Cite a ``link`` exactly as returned. Links are site-relative paths starting with
    ``/docs/``; prepending a domain produces a URL that does not exist.

    Args:
        query: The user's question, or the distinctive terms from it. Include the technical
            nouns they used, such as "checkpointer", "interrupt", or "create_agent".
        product: Optional filter, one of "langgraph", "langchain", or "deepagents". Leave
            it unset unless the user named the product, so a cross-cutting question can
            find the page that actually answers it.
    """
    hits = search(query, limit=_MAX_RESULTS, product=product)
    if not hits:
        return (
            f"No documentation section matches '{query}'. The knowledge store does not "
            "cover this question. Tell the user the available documentation does not "
            "answer it, and do not answer it from your own knowledge."
        )
    rendered = [_render_hit(position, hit) for position, hit in enumerate(hits, start=1)]
    return _with_rules(f"{len(hits)} matching sections.\n\n" + "\n\n".join(rendered))


@tool
async def read_documentation(path: str, section: str | None = None) -> str:
    """Read the full text of a documentation page or one of its sections.

    Call this on the results of ``search_documentation`` before you answer, so the answer
    is built from the whole passage rather than a preview. Reading a page without a section
    returns its outline, which is the cheap way to find the right section on a long page.

    Args:
        path: The page path from a search result, such as "langgraph/stores.md".
        section: The section anchor from a search result, such as "semantic-search". Omit
            it to get the page's outline instead of its text.
    """
    try:
        found = page(path)
    except KeyError:
        return f"No page '{path}' in the knowledge store. Use a path from a search result.\n\n{outline()}"
    if section is None:
        return _render_outline(found)
    wanted = section.strip().lstrip("#")
    for item in found.sections:
        if item.anchor == wanted:
            return _render_section(item)
    anchors = ", ".join(item.anchor for item in found.sections if item.anchor)
    return f"No section '{section}' on {path}. Sections on this page: {anchors}."


def _render_outline(found: Page) -> str:
    """Render a page's frontmatter and section list without its body."""
    lines = [
        f"# {found.title} ({found.path})",
        f"- link: {found.resource}",
        f"- product: {found.product}",
    ]
    if found.description:
        lines.append(f"- description: {found.description}")
    lines.extend(["", "## Sections", ""])
    for item in found.sections:
        anchor = item.anchor or "(introduction)"
        lines.append(f"- {item.title} — anchor `{anchor}` — {item.citation} ({len(item.text)} characters)")
    return "\n".join(lines)


def _render_section(item: Section) -> str:
    """Render one section in full, with the citation link the answer must carry."""
    text = item.text
    if len(text) > _SECTION_CHARACTERS:
        text = text[:_SECTION_CHARACTERS].rstrip() + "\n\n[…section truncated…]"
    lines = [
        f"# {item.label}",
        f"- page: {item.path}",
        f"- cite as: {item.markdown_citation}",
    ]
    if item.code_examples:
        lines.append(f"- code examples in this section: {', '.join(item.code_examples)}")
    lines.extend(["", text])
    return _with_rules("\n".join(lines))
