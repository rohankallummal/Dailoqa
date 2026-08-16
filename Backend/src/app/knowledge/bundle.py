"""Loading of the OKF documentation bundle into retrievable sections.

The bundle under ``Backend/knowledge-store`` holds one Markdown concept per documentation
page. Whole pages are far too large to hand a model -- the middleware page alone is 94KB --
so a page is split at its H2 and H3 headings into sections. A section is the unit the agent
retrieves and the unit it cites: its heading slug is the same anchor the published page
uses, so every answer can link straight to the passage it came from.
"""

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

KNOWLEDGE_ROOT = Path(__file__).resolve().parents[3] / "knowledge-store"

_DELIMITER = "---"
_FENCE = "```"
_INLINE_LINK = re.compile(r"\[([^\]]*)\]\([^)\s]+\)")
_PUNCTUATION = re.compile(r"[^\w\s-]", re.UNICODE)
_CODE_LINK = re.compile(r"\((\.\./code/[^)\s]+)\)")


@dataclass(frozen=True)
class Section:
    """One retrievable passage of a documentation page."""

    path: str
    product: str
    page_title: str
    title: str
    anchor: str
    resource: str
    text: str
    code_examples: tuple[str, ...]

    @property
    def citation(self) -> str:
        """The published URL of this exact passage, used as the answer's evidence link."""
        return f"{self.resource}#{self.anchor}" if self.anchor else self.resource

    @property
    def label(self) -> str:
        """A human-readable name for this passage, page first."""
        return f"{self.page_title} — {self.title}" if self.anchor else self.page_title

    @property
    def markdown_citation(self) -> str:
        """The citation as a finished Markdown link, ready to copy into an answer.

        Handing the model a complete link rather than a bare path removes the step where
        it assembles one, which is where it kept inventing a public docs domain that does
        not exist.
        """
        return f"[{self.label}]({self.citation})"


@dataclass(frozen=True)
class Page:
    """One documentation concept: its frontmatter, its outline, and its sections."""

    path: str
    product: str
    title: str
    description: str
    resource: str
    sections: tuple[Section, ...]


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Split a concept file into its parsed frontmatter mapping and its body."""
    if not text.startswith(_DELIMITER):
        return {}, text
    parts = text.split(_DELIMITER, 2)
    if len(parts) < 3:
        return {}, text
    meta = yaml.safe_load(parts[1]) or {}
    return (meta if isinstance(meta, dict) else {}), parts[2].lstrip("\n")


def prose_lines(body: str) -> list[tuple[bool, str]]:
    """Mark every line of a body with whether it sits inside a fenced code block.

    Headings are only recognised outside code, so a ``#`` comment in a Python example is
    never mistaken for a section boundary.
    """
    marked: list[tuple[bool, str]] = []
    inside = False
    for line in body.split("\n"):
        if line.lstrip().startswith(_FENCE):
            marked.append((True, line))
            inside = not inside
            continue
        marked.append((inside, line))
    return marked


def _heading(line: str) -> tuple[int, str] | None:
    """Return the level and text of an H2 or H3, or None for anything else."""
    stripped = line.strip()
    if not stripped.startswith("##"):
        return None
    hashes = len(stripped) - len(stripped.lstrip("#"))
    if hashes not in (2, 3):
        return None
    return hashes, stripped[hashes:].strip()


def slugify(text: str) -> str:
    """Slug a heading the way the docs site does, so anchors resolve on the live page."""
    value = _INLINE_LINK.sub(r"\1", text).strip().lower()
    return re.sub(r"\s+", "-", _PUNCTUATION.sub("", value))


def _anchors(body: str) -> list[tuple[int, int, str, str]]:
    """Locate every H2 and H3 as ``(line index, level, title, anchor)``, deduping slugs."""
    found: list[tuple[int, int, str, str]] = []
    seen: dict[str, int] = {}
    for index, (is_code, line) in enumerate(prose_lines(body)):
        if is_code:
            continue
        heading = _heading(line)
        if heading is None:
            continue
        level, title = heading
        slug = slugify(title)
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        found.append((index, level, title, slug if count == 0 else f"{slug}-{count}"))
    return found


def _sections(body: str, meta: dict, path: str) -> tuple[Section, ...]:
    """Split a page body into its lead passage and one passage per H2 or H3."""
    lines = [line for _, line in prose_lines(body)]
    headings = _anchors(body)
    boundaries = [index for index, _, _, _ in headings]
    title = str(meta.get("title") or path)
    common = {
        "path": path,
        "product": str(meta.get("product") or ""),
        "page_title": title,
        "resource": str(meta.get("resource") or ""),
    }

    found: list[Section] = []
    lead = "\n".join(lines[: boundaries[0]] if boundaries else lines).strip()
    if lead:
        found.append(Section(title=title, anchor="", text=lead, code_examples=_code_links(lead), **common))
    for position, (start, _, heading, anchor) in enumerate(headings):
        end = boundaries[position + 1] if position + 1 < len(boundaries) else len(lines)
        text = "\n".join(lines[start:end]).strip()
        found.append(
            Section(title=heading, anchor=anchor, text=text, code_examples=_code_links(text), **common)
        )
    return tuple(found)


def _code_links(text: str) -> tuple[str, ...]:
    """Return the code examples this passage itself embeds, in order and without repeats.

    The page's frontmatter lists every example on the page, which for a long page is
    dozens of paths that have nothing to do with the passage being read. Reading them off
    the passage keeps the link between documentation and code exact.
    """
    return tuple(dict.fromkeys(_CODE_LINK.findall(text)))


def _load(path: Path) -> Page:
    """Parse one concept file into a page with its sections."""
    relative = path.relative_to(KNOWLEDGE_ROOT).as_posix()
    meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
    return Page(
        path=relative,
        product=str(meta.get("product") or ""),
        title=str(meta.get("title") or relative),
        description=str(meta.get("description") or ""),
        resource=str(meta.get("resource") or ""),
        sections=_sections(body, meta, relative),
    )


@lru_cache
def pages() -> tuple[Page, ...]:
    """Every documentation page in the bundle, loaded once and cached for the process."""
    found = [
        _load(path)
        for path in sorted(KNOWLEDGE_ROOT.glob("*/*.md"))
        if path.name != "index.md" and path.parent.name != "code"
    ]
    return tuple(found)


@lru_cache
def sections() -> tuple[Section, ...]:
    """Every retrievable passage across every page."""
    return tuple(section for page in pages() for section in page.sections)


@lru_cache
def _by_path() -> dict[str, Page]:
    """Index the pages by their bundle-relative path."""
    return {page.path: page for page in pages()}


def page(path: str) -> Page:
    """Return one page by its bundle path, raising KeyError when it is not in the bundle."""
    return _by_path()[path.strip().lstrip("/")]


def outline() -> str:
    """Render the whole bundle as a product-grouped list of pages and their sections.

    This is what tells the agent whether a question is covered at all, without spending a
    retrieval on it.
    """
    lines: list[str] = []
    for product in sorted({page.product for page in pages()}):
        lines.append(f"\n## {product}")
        for item in pages():
            if item.product != product:
                continue
            lines.append(f"\n### {item.title} ({item.path})")
            if item.description:
                lines.append(item.description)
            titles = [section.title for section in item.sections if section.anchor]
            if titles:
                lines.append("Sections: " + ", ".join(titles))
    return "\n".join(lines).strip()
