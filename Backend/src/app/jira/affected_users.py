"""Generation of the Affected Users spreadsheet attached to a shared issue."""

from datetime import datetime
from io import BytesIO

from openpyxl import Workbook

AFFECTED_USERS_FILENAME = "affected-users.xlsx"

_COLUMNS = ["Name", "ID", "Date Reported"]
_COLUMN_WIDTHS = [32, 32, 16]


def _format_date(value) -> str:
    """Render a reported-at value as an ISO date, passing through anything unusable."""
    if isinstance(value, datetime):
        return value.date().isoformat()
    return str(value or "")


def build_workbook(rows: list[dict]) -> bytes:
    """Build the affected-users workbook as xlsx bytes.

    One row per reporter, in the order given. The sheet is the record of everyone affected
    by the issue, so the development team can judge its impact.
    """
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Affected Users"
    sheet.append(_COLUMNS)
    for index, width in enumerate(_COLUMN_WIDTHS, start=1):
        sheet.column_dimensions[sheet.cell(row=1, column=index).column_letter].width = width
    for row in rows:
        sheet.append(
            [row.get("name") or "", row.get("oauth_id") or "", _format_date(row.get("reported_at"))]
        )
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
