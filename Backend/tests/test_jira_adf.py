from app.jira.adf import _to_adf


def test_single_line_becomes_one_paragraph():
    doc = _to_adf("Search returns no results.")
    assert doc == {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": "Search returns no results."}],
            }
        ],
    }


def test_multiple_lines_become_multiple_paragraphs():
    doc = _to_adf("line one\nline two")
    assert len(doc["content"]) == 2
    assert doc["content"][1]["content"][0]["text"] == "line two"


def test_blank_input_yields_one_empty_paragraph():
    doc = _to_adf("")
    assert doc["content"] == [{"type": "paragraph", "content": []}]
