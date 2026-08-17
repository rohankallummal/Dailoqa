"""Discovery and progressive disclosure of on-demand agent skills.

Only each skill's name and one-line description enter the system prompt. The full
body is fetched by the ``load_skill`` tool when the agent decides a skill applies,
so the per-turn prompt stays the same size no matter how many skills exist.
"""

from functools import lru_cache
from pathlib import Path

from app.knowledge.bundle import split_frontmatter

SKILLS_ROOT = Path(__file__).resolve().parents[3] / "skills"


@lru_cache
def _registry() -> dict[str, tuple[str, Path]]:
    """Map skill name to its description and file path, scanning the skills tree once."""
    found: dict[str, tuple[str, Path]] = {}
    for path in sorted(SKILLS_ROOT.glob("*/SKILL.md")):
        meta, _ = split_frontmatter(path.read_text(encoding="utf-8"))
        name = meta.get("name")
        description = meta.get("description")
        if not name or not description:
            continue
        found[str(name)] = (" ".join(str(description).split()), path)
    return found


def skill_descriptions() -> list[tuple[str, str]]:
    """Return (name, description) for every registered skill, name-sorted."""
    return [(name, description) for name, (description, _) in sorted(_registry().items())]


@lru_cache
def skill_body(name: str) -> str:
    """Return a skill's full instruction body; raise KeyError if it is not registered."""
    entry = _registry().get(name)
    if entry is None:
        raise KeyError(name)
    return split_frontmatter(entry[1].read_text(encoding="utf-8"))[1]
