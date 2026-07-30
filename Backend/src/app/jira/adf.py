"""Conversion of plain text into Atlassian Document Format (ADF)."""

import math


def _to_adf(text: str) -> dict:
    """Build an ADF document with one paragraph per non-empty line.

    Jira Cloud's v3 API requires descriptions and comments as ADF, not plain
    strings. Blank input yields a single empty paragraph so the field is valid.
    """
    lines = [line for line in text.split("\n") if line.strip()]
    if not lines:
        return {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": []}]}
    content = [
        {"type": "paragraph", "content": [{"type": "text", "text": line}]}
        for line in lines
    ]
    return {"type": "doc", "version": 1, "content": content}


def _round_half_up(value: float, digits: int) -> float:
    """Round halves away from zero, the way JavaScript's toFixed does.

    Python's format spec rounds halves to even instead, so 2560 bytes would be written
    into the ticket as 2 KB while the picker the reporter uploaded it from showed 3 KB.
    """
    factor = 10**digits
    return math.floor(value * factor + 0.5) / factor


def format_size(num_bytes: int) -> str:
    """Render a byte count the way the Evidence list shows it."""
    if num_bytes < 1024:
        return f"{num_bytes} B"
    if num_bytes < 1024 * 1024:
        return f"{_round_half_up(num_bytes / 1024, 0):.0f} KB"
    return f"{_round_half_up(num_bytes / 1024 / 1024, 1):.1f} MB"


def evidence_section(files: list[dict]) -> list[dict]:
    """Build the Evidence heading and its bulleted file list as ADF nodes.

    Returns an empty list when there are no files, so callers can extend
    unconditionally.
    """
    if not files:
        return []
    items = [
        {
            "type": "listItem",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{item['name']} ({item['category']}, {format_size(int(item['size']))})",
                        }
                    ],
                }
            ],
        }
        for item in files
    ]
    return [
        {"type": "heading", "attrs": {"level": 3}, "content": [{"type": "text", "text": "Evidence"}]},
        {"type": "bulletList", "content": items},
    ]


def build_document(text: str, files: list[dict] | None = None) -> dict:
    """Build a ticket description: the field lines, then an Evidence section if any."""
    document = _to_adf(text)
    document["content"].extend(evidence_section(files or []))
    return document
