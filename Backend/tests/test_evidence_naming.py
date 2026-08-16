"""Covers how a reporter's evidence is renamed before it reaches a shared issue."""

from app.worker.evidence_step import original_names, reporter_prefix, upload_names


def test_reporter_prefix_is_filesystem_safe():
    assert reporter_prefix("Ada Lovelace", "1001") == "Ada_Lovelace-1001"
    assert reporter_prefix("a/b", "../x") == "b-x"


def test_upload_names_number_from_one_in_filename_order():
    assert upload_names("Ada-1001", ["b.png", "a.mp4"]) == {
        "a.mp4": "Ada-1001-1.mp4",
        "b.png": "Ada-1001-2.png",
    }


def test_upload_names_are_stable_across_calls():
    names = ["z.png", "a.png"]

    assert upload_names("A-1", names) == upload_names("A-1", list(reversed(names)))


def test_upload_names_collapse_duplicates():
    assert upload_names("A-1", ["a.png", "a.png"]) == {"a.png": "A-1-1.png"}


def test_original_names_are_identity():
    assert original_names(["a.png"]) == {"a.png": "a.png"}
