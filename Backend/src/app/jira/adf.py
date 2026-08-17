"""Conversion of plain text into Atlassian Document Format (ADF)."""


def build_document(text: str) -> dict:
    """Build a comment body as ADF, one paragraph per non-empty line.

    Jira Cloud's v3 API requires comments as ADF, not plain strings. Blank input yields a
    single empty paragraph so the field is valid.
    """
    lines = [line for line in text.split("\n") if line.strip()]
    if not lines:
        return {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": []}]}
    content = [
        {"type": "paragraph", "content": [{"type": "text", "text": line}]}
        for line in lines
    ]
    return {"type": "doc", "version": 1, "content": content}


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


def build_bug_document(ticket: dict, client_environment: dict, reporter: dict) -> dict:
    """Build a Bug Report description in the order Ticket-Structure.md specifies.

    Steps to Reproduce is written whenever there are steps. Only a user who cannot reproduce
    the problem has none, and their report is carried by Issue Description instead.

    Attachments are not described here. Every screenshot, recording, and the affected-users
    workbook is on the issue already, where Jira lists each one with its type and size, so
    naming them in the description only restated what a triager can see -- and it could go
    stale, since this document is written once and never rewritten.
    """
    content = _text_section("Summary", ticket.get("summary", ""))
    content.extend(_text_section("Issue Description", ticket.get("issue_description", "")))
    content.extend(_environment_section(client_environment or {}))
    steps = ticket.get("steps_to_reproduce") or []
    if steps:
        content.extend([_heading("Steps to Reproduce"), _ordered_list(steps)])
    content.extend(_reporter_section("Reported By", reporter or {}))
    return {"type": "doc", "version": 1, "content": content}


def build_feature_document(ticket: dict, reporter: dict) -> dict:
    """Build a Feature Request description in the order Ticket-Structure.md specifies."""
    content = _text_section("Feature", ticket.get("feature", ""))
    content.extend(_text_section("Problem Statement", ticket.get("problem_statement", "")))
    content.extend(_reporter_section("Requested by", reporter or {}))
    return {"type": "doc", "version": 1, "content": content}


def build_ticket_document(kind: str, ticket: dict, client_environment: dict, reporter: dict) -> dict:
    """Build the description document for a ticket of the given kind."""
    if kind == "bug":
        return build_bug_document(ticket, client_environment, reporter)
    if kind == "feature":
        return build_feature_document(ticket, reporter)
    raise ValueError(f"unknown ticket kind: {kind}")
