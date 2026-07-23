"""Conversion of plain text into Atlassian Document Format (ADF)."""


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
