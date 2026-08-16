"""Covers the regenerable link-path sections and section replacement."""

from app.jira.adf import (
    AFFECTED_USERS_HEADING,
    MORE_EVIDENCE_HEADING,
    affected_users_section,
    more_evidence_section,
    replace_section,
)


def _document(*nodes):
    return {"type": "doc", "version": 1, "content": list(nodes)}


def _heading_node(text):
    return {"type": "heading", "attrs": {"level": 3}, "content": [{"type": "text", "text": text}]}


def _paragraph_node(text):
    return {"type": "paragraph", "content": [{"type": "text", "text": text}]}


def _headings(document):
    return [
        child["text"]
        for node in document["content"]
        if node["type"] == "heading"
        for child in node["content"]
    ]


def test_more_evidence_section_lists_each_file():
    nodes = more_evidence_section([{"name": "ada-1001-1.png", "category": "image", "size": 2560}])

    assert nodes[0] == _heading_node(MORE_EVIDENCE_HEADING)
    text = nodes[1]["content"][0]["content"][0]["content"][0]["text"]
    assert text == "ada-1001-1.png (image, 3 KB)"


def test_more_evidence_section_is_empty_without_files():
    assert more_evidence_section([]) == []


def test_affected_users_section_names_the_spreadsheet():
    nodes = affected_users_section("affected-users.xlsx")

    assert nodes[0] == _heading_node(AFFECTED_USERS_HEADING)
    assert "affected-users.xlsx" in nodes[1]["content"][0]["text"]


def test_replace_section_appends_when_heading_absent():
    document = _document(_heading_node("Summary"), _paragraph_node("a"))
    nodes = more_evidence_section([{"name": "x.png", "category": "image", "size": 10}])

    result = replace_section(document, MORE_EVIDENCE_HEADING, nodes)

    assert _headings(result) == ["Summary", MORE_EVIDENCE_HEADING]


def test_replace_section_swaps_body_without_duplicating_heading():
    first = more_evidence_section([{"name": "a.png", "category": "image", "size": 10}])
    document = replace_section(_document(_heading_node("Summary")), MORE_EVIDENCE_HEADING, first)
    second = more_evidence_section([{"name": "b.png", "category": "image", "size": 10}])

    result = replace_section(document, MORE_EVIDENCE_HEADING, second)

    assert _headings(result).count(MORE_EVIDENCE_HEADING) == 1
    assert "b.png" in str(result)
    assert "a.png" not in str(result)


def test_replace_section_preserves_sections_after_it():
    document = _document(
        _heading_node(MORE_EVIDENCE_HEADING),
        _paragraph_node("old"),
        _heading_node("Reported By"),
        _paragraph_node("Ada"),
    )

    result = replace_section(document, MORE_EVIDENCE_HEADING, [])

    assert _headings(result) == ["Reported By"]
    assert "Ada" in str(result)
    assert "old" not in str(result)
