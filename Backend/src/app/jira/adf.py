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


MORE_EVIDENCE_HEADING = "More Evidence"
AFFECTED_USERS_HEADING = "Affected Users"
LEGACY_SIMILAR_REPORTS_HEADING = "Similar Reports"


def _heading(text: str) -> dict:
    """Build a level-3 section heading node."""
    return {"type": "heading", "attrs": {"level": 3}, "content": [{"type": "text", "text": text}]}


def _paragraph(text: str) -> dict:
    """Build a paragraph node, empty when the text is blank."""
    if not str(text).strip():
        return {"type": "paragraph", "content": []}
    return {"type": "paragraph", "content": [{"type": "text", "text": str(text)}]}


def _bullet_list(lines: list[str]) -> dict:
    """Build a bulleted list node from non-empty lines."""
    items = [
        {"type": "listItem", "content": [_paragraph(line)]} for line in lines if str(line).strip()
    ]
    return {"type": "bulletList", "content": items}


def _ordered_list(lines: list[str]) -> dict:
    """Build a numbered list node from non-empty lines."""
    items = [
        {"type": "listItem", "content": [_paragraph(line)]} for line in lines if str(line).strip()
    ]
    return {"type": "orderedList", "attrs": {"order": 1}, "content": items}


def _text_section(title: str, body: str) -> list[dict]:
    """Build a heading plus one prose paragraph."""
    return [_heading(title), _paragraph(body)]


def _environment_section(environment: dict) -> list[dict]:
    """Build the Client Environment heading and its labelled bullet list."""
    return [
        _heading("Client Environment"),
        _bullet_list(
            [
                f"Device: {environment.get('device') or 'Unknown'}",
                f"Browser: {environment.get('browser') or 'Unknown'}",
                f"Operating System: {environment.get('operating_system') or 'Unknown'}",
            ]
        ),
    ]


def _reporter_section(title: str, reporter: dict) -> list[dict]:
    """Build a Reported By / Requested by heading and its identity bullets."""
    return [
        _heading(title),
        _bullet_list(
            [
                f"Google OAuth Name: {reporter.get('name') or 'Unknown'}",
                f"Google OAuth ID: {reporter.get('oauth_id') or 'Unknown'}",
            ]
        ),
    ]


def more_evidence_section(files: list[dict]) -> list[dict]:
    """Build the More Evidence heading and the file list contributed by later reporters.

    Returns an empty list when there are no files, so a caller can replace the section
    unconditionally and have it disappear when the last attachment is removed.
    """
    if not files:
        return []
    lines = [
        f"{item['name']} ({item['category']}, {format_size(int(item['size']))})" for item in files
    ]
    return [_heading(MORE_EVIDENCE_HEADING), _bullet_list(lines)]


def affected_users_section(filename: str) -> list[dict]:
    """Build the Affected Users heading pointing at the attached spreadsheet."""
    return [
        _heading(AFFECTED_USERS_HEADING),
        _paragraph(
            f"More than one user has reported this issue. The attached {filename} lists every "
            "affected user and the date they reported it, and is updated automatically as "
            "further reports arrive."
        ),
    ]


def _is_heading_at(node: dict, level: int | None) -> bool:
    """Report whether a node is a heading at the given level."""
    return node.get("type") == "heading" and node.get("attrs", {}).get("level") == level


def _heading_index(content: list[dict], text: str) -> int | None:
    """Return the position of the heading carrying the given text, or None."""
    for index, node in enumerate(content):
        if node.get("type") != "heading":
            continue
        if any(child.get("text") == text for child in node.get("content") or []):
            return index
    return None


def replace_section(document: dict, heading: str, nodes: list[dict]) -> dict:
    """Return the document with one section's nodes swapped for new ones.

    A section runs from its heading to the next heading of the same level. The link path
    regenerates More Evidence on every report, so appending would stack a fresh copy under
    each link; replacing keeps exactly one. An absent heading appends, which is how the
    first link adds the section, and empty nodes remove it.
    """
    content = document.get("content") or []
    start = _heading_index(content, heading)
    if start is None:
        return {**document, "content": [*content, *nodes]}
    level = content[start].get("attrs", {}).get("level")
    end = start + 1
    while end < len(content) and not _is_heading_at(content[end], level):
        end += 1
    return {**document, "content": [*content[:start], *nodes, *content[end:]]}


def has_heading(document: dict, text: str) -> bool:
    """Report whether a document already carries a heading with the given text."""
    for node in document.get("content") or []:
        if node.get("type") != "heading":
            continue
        for child in node.get("content") or []:
            if child.get("text") == text:
                return True
    return False


def append_nodes(document: dict, nodes: list[dict]) -> dict:
    """Return the document with nodes appended to its content."""
    return {**document, "content": [*(document.get("content") or []), *nodes]}


def build_bug_document(
    ticket: dict, client_environment: dict, reporter: dict, evidence: list[dict] | None = None
) -> dict:
    """Build a Bug Report description in the order Ticket-Structure.md specifies.

    Steps to Reproduce appears only when no evidence was attached; supplied images or video
    stand in for the walkthrough. Similar Reports is not written here -- it is appended to
    the live issue by the link path once a second user reports the same problem.
    """
    evidence = evidence or []
    content = _text_section("Summary", ticket.get("summary", ""))
    content.extend(evidence_section(evidence))
    content.extend(_text_section("Issue Description", ticket.get("issue_description", "")))
    content.extend(_environment_section(client_environment or {}))
    steps = ticket.get("steps_to_reproduce") or []
    if not evidence and steps:
        content.extend([_heading("Steps to Reproduce"), _ordered_list(steps)])
    content.extend(_reporter_section("Reported By", reporter or {}))
    return {"type": "doc", "version": 1, "content": content}


def build_feature_document(ticket: dict, reporter: dict) -> dict:
    """Build a Feature Request description in the order Ticket-Structure.md specifies."""
    content = _text_section("Feature", ticket.get("feature", ""))
    content.extend(_text_section("Problem Statement", ticket.get("problem_statement", "")))
    content.extend(_reporter_section("Requested by", reporter or {}))
    return {"type": "doc", "version": 1, "content": content}


def build_ticket_document(
    kind: str,
    ticket: dict,
    client_environment: dict,
    reporter: dict,
    evidence: list[dict] | None = None,
) -> dict:
    """Build the description document for a ticket of the given kind."""
    if kind == "bug":
        return build_bug_document(ticket, client_environment, reporter, evidence)
    if kind == "feature":
        return build_feature_document(ticket, reporter)
    raise ValueError(f"unknown ticket kind: {kind}")
