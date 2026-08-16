"""Covers selection of later reporters' attachments for the More Evidence section."""

from app.worker.link_step import linked_evidence


def _attachment(filename, size=1024):
    return {"id": "1", "filename": filename, "size": size}


def test_selects_only_prefixed_attachments():
    attachments = [
        _attachment("original-screenshot.png"),
        _attachment("Alan_Turing-1002-1.png"),
        _attachment("affected-users.xlsx"),
    ]

    assert linked_evidence(attachments, ["Alan_Turing-1002"]) == [
        {"name": "Alan_Turing-1002-1.png", "category": "image", "size": 1024}
    ]


def test_returns_empty_without_linked_reporters():
    assert linked_evidence([_attachment("a.png")], []) == []


def test_orders_by_filename():
    attachments = [_attachment("A-1-2.png"), _attachment("A-1-1.png")]

    assert [item["name"] for item in linked_evidence(attachments, ["A-1"])] == [
        "A-1-1.png",
        "A-1-2.png",
    ]


def test_tolerates_a_missing_size():
    attachments = [{"id": "1", "filename": "A-1-1.png"}]

    assert linked_evidence(attachments, ["A-1"])[0]["size"] == 0
