"""Covers the affected-users workbook and its filename constants."""

from io import BytesIO

from openpyxl import load_workbook

from app.jira.affected_users import AFFECTED_USERS_FILENAME, LEGACY_FILENAME, build_workbook


def test_filenames():
    assert AFFECTED_USERS_FILENAME == "affected-users.xlsx"
    assert LEGACY_FILENAME == "similar-reports.xlsx"


def test_workbook_lists_every_reporter(reporter_rows):
    sheet = load_workbook(BytesIO(build_workbook(reporter_rows))).active

    assert sheet.title == "Affected Users"
    assert [cell.value for cell in sheet[1]] == [
        "Google OAuth Name",
        "Google OAuth ID",
        "Date Reported",
    ]
    assert [cell.value for cell in sheet[2]] == ["Ada Lovelace", "1001", "2026-08-01"]
    assert [cell.value for cell in sheet[3]] == ["Alan Turing", "1002", "2026-08-02"]
