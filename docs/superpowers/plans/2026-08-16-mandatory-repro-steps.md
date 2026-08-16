# Mandatory Reproduction Steps Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make reproduction steps mandatory for every bug the agent files or links, enforced in code rather than prose, and restructure the link path's Jira output into a More Evidence and an Affected Users section.

**Architecture:** A pure predicate in the agent's write tools refuses any bug without steps before a `Job` row is enqueued, so no wording the model produces can file a stepless ticket. The link path gains a regenerable description section built from the issue's live attachments, which are renamed per reporter so they map onto the Affected Users spreadsheet.

**Tech Stack:** Python 3.12, FastAPI, LangChain/LangGraph, SQLAlchemy async, openpyxl, Jira Cloud v3 REST (ADF), pytest. Everything runs in Docker.

**Spec:** `docs/superpowers/specs/2026-08-16-mandatory-repro-steps-design.md`

## Global Constraints

- **No Python on the host.** Every command runs through Docker. Tests:
  `docker compose run --rm api pytest tests -q -m "not live"` from `Backend/`.
  While iterating, mount the sources instead of rebuilding between edits:
  `docker compose run --rm -v "$PWD/tests:/code/tests" -v "$PWD/src/app:/code/src/app" -v "$PWD/skills:/code/skills" api pytest tests -q -m "not live"`
- **Coding rules:** `Backend/CLAUDE.md`. `snake_case` modules and functions,
  `UPPER_SNAKE_CASE` constants, leading underscore for internal helpers. **No inline or
  block comments.** Docstrings required on public modules, classes, and functions.
- **Tool docstrings and Pydantic `description=` are functional** — they are sent to the
  model at runtime. Never strip them as comments.
- Three levels of indentation is the ceiling; use guard clauses and early returns.
- **Termination sentence, verbatim, curly apostrophe:**
  `Sorry, we can’t proceed with raising this issue.`
- **Attachment naming, link path only:** `{safe(oauth_name)}-{safe(oauth_id)}-{n}{ext}`,
  `n` from 1 per reporter, stable source-filename order.
- **Section headings, exact:** `More Evidence`, `Affected Users`.
- **Spreadsheet filename:** `affected-users.xlsx`. Legacy name to migrate away from:
  `similar-reports.xlsx`. Legacy heading: `Similar Reports`.
- Do not commit to a remote. Local commits only, per `Frontend/CLAUDE.md`.

---

### Task 1: Test infrastructure

There are no tests in `Backend/` and pytest is not a dependency. Everything after this
task depends on being able to run one.

**Files:**
- Modify: `Backend/pyproject.toml`
- Modify: `Backend/Dockerfile:12`
- Create: `Backend/tests/conftest.py`
- Test: `Backend/tests/test_infrastructure.py`

**Interfaces:**
- Consumes: nothing.
- Produces: a working `docker compose run --rm api pytest tests -q -m "not live"`, and a
  `live` marker for tests that call the real gateway.

- [ ] **Step 1: Add the dev dependency group and pytest config to `pyproject.toml`**

Append after the `dependencies` list:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.3",
    "pytest-asyncio>=0.24",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
markers = [
    "live: exercises the real LLM gateway; requires the VPN to be connected",
]
```

- [ ] **Step 2: Install the dev extra in the image**

In `Backend/Dockerfile`, change the install line from:

```dockerfile
RUN pip install --no-cache-dir -e .
```

to:

```dockerfile
RUN pip install --no-cache-dir -e ".[dev]"
```

The image does not copy `tests/`, so add it alongside the other COPY lines or the
documented command fails with `file or directory not found: tests`:

```dockerfile
COPY tests ./tests
```

- [ ] **Step 3: Create `Backend/tests/conftest.py`**

```python
"""Shared fixtures for the backend test suite."""

import pytest


@pytest.fixture
def reporter_rows():
    """Two reporter rows, oldest first: the original filer then one linker."""
    from datetime import datetime

    return [
        {"name": "Ada Lovelace", "oauth_id": "1001", "reported_at": datetime(2026, 8, 1)},
        {"name": "Alan Turing", "oauth_id": "1002", "reported_at": datetime(2026, 8, 2)},
    ]
```

- [ ] **Step 4: Write the failing smoke test**

Create `Backend/tests/test_infrastructure.py`:

```python
"""Confirms the suite can import the application package."""


def test_app_package_imports():
    from app.jira import adf

    assert adf.format_size(2560) == "3 KB"
```

- [ ] **Step 5: Rebuild and run**

```bash
cd Backend
docker compose build api
docker compose run --rm api pytest tests -q -m "not live"
```

Expected: 1 passed.

- [ ] **Step 6: Commit**

```bash
git add Backend/pyproject.toml Backend/Dockerfile Backend/tests/
git commit -m "test: add pytest infrastructure for the backend"
```

---

### Task 2: ADF section builders and replaceable sections

**Files:**
- Modify: `Backend/src/app/jira/adf.py:79` (replace `SIMILAR_REPORTS_HEADING` and `similar_reports_section`)
- Test: `Backend/tests/test_adf_sections.py`

**Interfaces:**
- Consumes: `_heading`, `_paragraph`, `_bullet_list`, `format_size` from `adf.py`.
- Produces:
  - `MORE_EVIDENCE_HEADING: str = "More Evidence"`
  - `AFFECTED_USERS_HEADING: str = "Affected Users"`
  - `LEGACY_SIMILAR_REPORTS_HEADING: str = "Similar Reports"`
  - `more_evidence_section(files: list[dict]) -> list[dict]` — each file is
    `{"name": str, "category": str, "size": int}`; returns `[]` when empty
  - `affected_users_section(filename: str) -> list[dict]`
  - `replace_section(document: dict, heading: str, nodes: list[dict]) -> dict`

- [ ] **Step 1: Write the failing tests**

Create `Backend/tests/test_adf_sections.py`:

```python
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
    nodes = more_evidence_section(
        [{"name": "ada-1001-1.png", "category": "image", "size": 2560}]
    )
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
    result = replace_section(document, MORE_EVIDENCE_HEADING, more_evidence_section(
        [{"name": "x.png", "category": "image", "size": 10}]
    ))
    assert _headings(result) == ["Summary", MORE_EVIDENCE_HEADING]


def test_replace_section_swaps_body_without_duplicating_heading():
    first = more_evidence_section([{"name": "a.png", "category": "image", "size": 10}])
    document = replace_section(_document(_heading_node("Summary")), MORE_EVIDENCE_HEADING, first)
    second = more_evidence_section([{"name": "b.png", "category": "image", "size": 10}])
    result = replace_section(document, MORE_EVIDENCE_HEADING, second)

    assert _headings(result).count(MORE_EVIDENCE_HEADING) == 1
    rendered = str(result)
    assert "b.png" in rendered
    assert "a.png" not in rendered


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
```

- [ ] **Step 2: Run to verify they fail**

```bash
docker compose run --rm api pytest tests/test_adf_sections.py -q
```

Expected: FAIL — `ImportError: cannot import name 'MORE_EVIDENCE_HEADING'`.

- [ ] **Step 3: Implement**

In `Backend/src/app/jira/adf.py`, replace the `SIMILAR_REPORTS_HEADING = "Similar Reports"`
line at 79 with:

```python
MORE_EVIDENCE_HEADING = "More Evidence"
AFFECTED_USERS_HEADING = "Affected Users"
LEGACY_SIMILAR_REPORTS_HEADING = "Similar Reports"
```

Delete `similar_reports_section` (lines 142-151) and add, after `_environment_section`:

```python
def more_evidence_section(files: list[dict]) -> list[dict]:
    """Build the More Evidence heading and the file list contributed by later reporters.

    Returns an empty list when there are no files, so a caller can replace the section
    unconditionally and have it disappear when the last attachment is removed.
    """
    if not files:
        return []
    lines = [
        f"{item['name']} ({item['category']}, {format_size(int(item['size']))})"
        for item in files
    ]
    return [_heading(MORE_EVIDENCE_HEADING), _bullet_list(lines)]


def affected_users_section(filename: str) -> list[dict]:
    """Build the Affected Users heading pointing at the attached spreadsheet."""
    return [
        _heading(AFFECTED_USERS_HEADING),
        _paragraph(
            f"More than one user has reported this issue. The attached {filename} lists "
            "every affected user and the date they reported it, and is updated "
            "automatically as further reports arrive."
        ),
    ]
```

Add near `has_heading`:

```python
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
    regenerates More Evidence on every report, so appending would stack a fresh copy
    under each link; replacing keeps exactly one. An absent heading appends, which is how
    the first link adds the section, and empty nodes remove it.
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
```

- [ ] **Step 4: Run to verify they pass**

```bash
docker compose run --rm api pytest tests/test_adf_sections.py -q
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add Backend/src/app/jira/adf.py Backend/tests/test_adf_sections.py
git commit -m "feat: add More Evidence and Affected Users sections with replacement"
```

---

### Task 3: Rename the spreadsheet to Affected Users

**Files:**
- Modify: `Backend/src/app/jira/similar_reports.py` → rename file to `Backend/src/app/jira/affected_users.py`
- Test: `Backend/tests/test_affected_users.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - `app.jira.affected_users.AFFECTED_USERS_FILENAME: str = "affected-users.xlsx"`
  - `app.jira.affected_users.LEGACY_FILENAME: str = "similar-reports.xlsx"`
  - `app.jira.affected_users.build_workbook(rows: list[dict]) -> bytes` — unchanged
    signature; rows carry `name`, `oauth_id`, `reported_at`

- [ ] **Step 1: Write the failing test**

Create `Backend/tests/test_affected_users.py`:

```python
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
```

- [ ] **Step 2: Run to verify it fails**

```bash
docker compose run --rm api pytest tests/test_affected_users.py -q
```

Expected: FAIL — `ModuleNotFoundError: No module named 'app.jira.affected_users'`.

- [ ] **Step 3: Rename the module and its constants**

```bash
git mv Backend/src/app/jira/similar_reports.py Backend/src/app/jira/affected_users.py
```

In the renamed file, change the module docstring to
`"""Generation of the Affected Users spreadsheet attached to a shared issue."""`,
replace the filename constant block with:

```python
AFFECTED_USERS_FILENAME = "affected-users.xlsx"
LEGACY_FILENAME = "similar-reports.xlsx"
```

and change the sheet title line to:

```python
    sheet.title = "Affected Users"
```

- [ ] **Step 4: Run to verify it passes**

```bash
docker compose run --rm api pytest tests/test_affected_users.py -q
```

Expected: 2 passed. `tests/test_infrastructure.py` still passes;
`app/worker/link_step.py` is now importing a module that no longer exists and is fixed in
Task 5 — do not fix it here.

- [ ] **Step 5: Commit**

```bash
git add Backend/src/app/jira/ Backend/tests/test_affected_users.py
git commit -m "refactor: rename the similar-reports workbook to affected-users"
```

---

### Task 4: Per-reporter evidence naming

**Files:**
- Modify: `Backend/src/app/worker/evidence_step.py`
- Modify: `Backend/src/app/jira/client.py:113` (`add_attachments`)
- Modify: `Backend/src/app/worker/create_step.py:46,77` (call sites)
- Test: `Backend/tests/test_evidence_naming.py`

**Interfaces:**
- Consumes: `safe_filename` from `app.evidence.storage`.
- Produces:
  - `reporter_prefix(user_name: str, user_sub: str) -> str`
  - `upload_names(prefix: str, names: list[str]) -> dict[str, str]` — source filename to
    upload name
  - `original_names(names: list[str]) -> dict[str, str]` — identity map for the create path
  - `attach_evidence(job, client, jira_key: str, names: dict[str, str]) -> None` — the
    fourth argument is now **required**
  - `JiraClient.add_named_attachments(issue_key: str, items: list[tuple[str, Path]]) -> list[str]`

- [ ] **Step 1: Write the failing tests**

Create `Backend/tests/test_evidence_naming.py`:

```python
"""Covers how a reporter's evidence is renamed before it reaches a shared issue."""

from app.worker.evidence_step import original_names, reporter_prefix, upload_names


def test_reporter_prefix_is_filesystem_safe():
    assert reporter_prefix("Ada Lovelace", "1001") == "Ada Lovelace-1001"
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
```

- [ ] **Step 2: Run to verify they fail**

```bash
docker compose run --rm api pytest tests/test_evidence_naming.py -q
```

Expected: FAIL — `ImportError: cannot import name 'reporter_prefix'`.

- [ ] **Step 3: Implement the naming helpers**

Replace `Backend/src/app/worker/evidence_step.py` with:

```python
"""Idempotent upload of a job's evidence files to a Jira issue."""

from pathlib import Path

from app.evidence.storage import evidence_dir, safe_filename

EVIDENCE_FIELD = "evidence"


def evidence_of(job) -> list[dict]:
    """Return the job's evidence manifest, or an empty list when it carries none."""
    return job.payload.get(EVIDENCE_FIELD) or []


def reporter_prefix(user_name: str, user_sub: str) -> str:
    """Build the filename prefix tying a reporter's evidence to their spreadsheet row.

    The Affected Users sheet lists the same name and id, so a triager reading a filename
    can find who supplied it without opening the spreadsheet.
    """
    return f"{safe_filename(user_name)}-{safe_filename(user_sub)}"


def upload_names(prefix: str, names: list[str]) -> dict[str, str]:
    """Map each source filename to its {prefix}-{n} upload name, numbered from 1.

    Sorting makes the mapping deterministic, which is what lets a retry compute the same
    names and skip whatever the issue already holds instead of uploading a second copy.
    """
    ordered = sorted(dict.fromkeys(safe_filename(name) for name in names))
    return {
        name: f"{prefix}-{index}{Path(name).suffix}"
        for index, name in enumerate(ordered, start=1)
    }


def original_names(names: list[str]) -> dict[str, str]:
    """Map each source filename to itself, for the path that keeps original names."""
    return {safe_filename(name): safe_filename(name) for name in names}


async def attach_evidence(job, client, jira_key: str, names: dict[str, str]) -> None:
    """Upload the job's evidence under the given upload names, skipping what is attached.

    Names are reduced to a safe basename before being joined onto the evidence directory,
    so a manifest crafted with path separators cannot reach another conversation's files.

    The create path, the create resume path, and the link path all call this, and any of
    them may call it again on a retry. Checking what the issue already holds is what makes
    that safe, and is also what lets an upload that failed after the issue was created be
    retried rather than silently skipped.
    """
    if not names:
        return
    directory = evidence_dir(job.user_sub, job.conversation_id)
    already_attached = await client.list_attachment_filenames(jira_key)
    pending = [
        (upload, directory / source)
        for source, upload in sorted(names.items())
        if upload not in already_attached
    ]
    existing = [(upload, path) for upload, path in pending if path.is_file()]
    if existing:
        await client.add_named_attachments(jira_key, existing)
```

- [ ] **Step 4: Add the client method**

In `Backend/src/app/jira/client.py`, replace `add_attachments` (line 113) with:

```python
    async def add_named_attachments(self, issue_key: str, items: list[tuple[str, Path]]) -> list[str]:
        """Upload files under explicit names and return the filenames Jira accepted.

        The name is passed separately from the path because the link path renames a
        reporter's evidence to match their Affected Users row.

        Jira rejects multipart uploads without the X-Atlassian-Token: no-check header.
        """
        if not items:
            return []
        files = [("file", (name, path.read_bytes())) for name, path in items]
        response = await self._request(
            "POST",
            f"/issue/{issue_key}/attachments",
            timeout=_UPLOAD_TIMEOUT,
            files=files,
            headers={"X-Atlassian-Token": "no-check"},
        )
        return [item["filename"] for item in response.json()]
```

Keep the rest of the original method body identical to what it was — copy the
`_request` call and return statement from the existing implementation if they differ
from the above.

`evidence_step.py:34` is the only caller of the old `add_attachments`, and Step 3 already
replaced it, so no other call site needs changing. Update the one stale reference in
`add_attachment_bytes`'s docstring (`client.py:134`) from "add_attachments" to
"add_named_attachments", and change "Similar Reports workbook" to "Affected Users
workbook" while you are in it.

- [ ] **Step 5: Update the create-path call sites**

In `Backend/src/app/worker/create_step.py`, change the import at line 8 to:

```python
from app.worker.evidence_step import attach_evidence, evidence_of, original_names
```

At line 46 (the resume branch):

```python
        await attach_evidence(job, client, job.jira_key, original_names([item["name"] for item in evidence_of(job)]))
```

Note the resume branch runs before `evidence` is assigned, so it calls `evidence_of(job)`
itself. At line 77:

```python
    await attach_evidence(job, client, key, original_names([item["name"] for item in evidence]))
```

- [ ] **Step 6: Run to verify they pass**

```bash
docker compose run --rm api pytest tests/test_evidence_naming.py -q
```

Expected: 5 passed.

- [ ] **Step 7: Commit**

```bash
git add Backend/src/app/worker/ Backend/src/app/jira/client.py Backend/tests/test_evidence_naming.py
git commit -m "feat: rename link-path evidence per reporter"
```

---

### Task 5: Link path refreshes both sections and migrates the legacy ones

**Files:**
- Modify: `Backend/src/app/worker/link_step.py`
- Modify: `Backend/src/app/jira/client.py:144` (`list_attachments` carries size)
- Test: `Backend/tests/test_link_sections.py`

**Interfaces:**
- Consumes: `replace_section`, `more_evidence_section`, `affected_users_section`,
  `MORE_EVIDENCE_HEADING`, `AFFECTED_USERS_HEADING`, `LEGACY_SIMILAR_REPORTS_HEADING`
  (Task 2); `AFFECTED_USERS_FILENAME`, `LEGACY_FILENAME`, `build_workbook` (Task 3);
  `reporter_prefix`, `upload_names`, `attach_evidence` (Task 4).
- Produces:
  - `linked_evidence(attachments: list[dict], prefixes: list[str]) -> list[dict]` — the
    attachments belonging to later reporters, as `{"name", "category", "size"}`
  - `JiraClient.list_attachments` entries gain `"size": int`

- [ ] **Step 1: Write the failing test**

Create `Backend/tests/test_link_sections.py`:

```python
"""Covers selection of later reporters' attachments for the More Evidence section."""

from app.worker.link_step import linked_evidence


def _attachment(filename, size=1024):
    return {"id": "1", "filename": filename, "size": size}


def test_selects_only_prefixed_attachments():
    attachments = [
        _attachment("original-screenshot.png"),
        _attachment("Alan Turing-1002-1.png"),
        _attachment("affected-users.xlsx"),
    ]
    assert linked_evidence(attachments, ["Alan Turing-1002"]) == [
        {"name": "Alan Turing-1002-1.png", "category": "image", "size": 1024}
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
```

- [ ] **Step 2: Run to verify it fails**

```bash
docker compose run --rm api pytest tests/test_link_sections.py -q
```

Expected: FAIL — `ImportError: cannot import name 'linked_evidence'`.

- [ ] **Step 3: Make `list_attachments` carry size**

In `Backend/src/app/jira/client.py`, change the return at line 148 to:

```python
        return [
            {"id": item["id"], "filename": item["filename"], "size": item.get("size") or 0}
            for item in attachments
        ]
```

and update its docstring to
`"""Return the issue's attachments as {"id", "filename", "size"} entries."""`.

- [ ] **Step 4: Rewrite the link step's refresh functions**

In `Backend/src/app/worker/link_step.py`, replace the imports at lines 8-16 with:

```python
from app.evidence.storage import categorize
from app.jira.adf import (
    AFFECTED_USERS_HEADING,
    LEGACY_SIMILAR_REPORTS_HEADING,
    MORE_EVIDENCE_HEADING,
    affected_users_section,
    more_evidence_section,
    replace_section,
)
from app.jira.affected_users import AFFECTED_USERS_FILENAME, LEGACY_FILENAME, build_workbook
from app.worker.create_step import record_reporter
from app.worker.evidence_step import attach_evidence, evidence_of, reporter_prefix, upload_names
from app.worker.queue import set_job_action
```

Replace `_replace_spreadsheet` and `_ensure_similar_reports_section` with:

```python
def linked_evidence(attachments: list[dict], prefixes: list[str]) -> list[dict]:
    """Return the attachments contributed by reporters who linked after the issue existed.

    The naming convention is the only marker, which is what lets this be rebuilt from the
    live issue rather than tracked in the database: a retry recomputes the same list.
    """
    if not prefixes:
        return []
    selected = [
        item
        for item in attachments
        if any(item["filename"].startswith(f"{prefix}-") for prefix in prefixes)
    ]
    return [
        {
            "name": item["filename"],
            "category": categorize(item["filename"]),
            "size": item.get("size") or 0,
        }
        for item in sorted(selected, key=lambda item: item["filename"])
    ]


async def _replace_spreadsheet(client, issue_key: str, rows: list[dict]) -> None:
    """Upload a freshly generated workbook, removing whatever it supersedes.

    Both the current and the legacy filename are removed, so an issue last touched before
    the rename ends up holding one spreadsheet rather than two.
    """
    superseded = {AFFECTED_USERS_FILENAME, LEGACY_FILENAME}
    for attachment in await client.list_attachments(issue_key):
        if attachment["filename"] in superseded:
            await client.delete_attachment(attachment["id"])
    await client.add_attachment_bytes(issue_key, AFFECTED_USERS_FILENAME, build_workbook(rows))


async def _refresh_sections(client, issue_key: str, prefixes: list[str]) -> None:
    """Rewrite More Evidence and Affected Users, dropping the legacy section.

    Both are replaced rather than appended because their contents change with every new
    report, and the legacy Similar Reports heading is removed so a migrated issue does not
    carry two descriptions of the same thing.
    """
    files = linked_evidence(await client.list_attachments(issue_key), prefixes)
    document = await client.get_description(issue_key)
    document = replace_section(document, LEGACY_SIMILAR_REPORTS_HEADING, [])
    document = replace_section(document, MORE_EVIDENCE_HEADING, more_evidence_section(files))
    document = replace_section(
        document, AFFECTED_USERS_HEADING, affected_users_section(AFFECTED_USERS_FILENAME)
    )
    await client.update_description(issue_key, document)
```

Replace `update_similar_reports` with:

```python
async def update_shared_sections(session, client, ticket_id: str, issue_key: str) -> None:
    """Refresh the spreadsheet and both sections once a second user reports.

    Failures are logged and swallowed. The reporter link and the evidence upload are the
    load-bearing work, and everything here is regenerated from the reporter rows and the
    issue's own attachments on the next link, so a failed attempt heals itself rather than
    costing the job an attempt.

    The first row is the reporter who filed the issue, so their evidence keeps its original
    filenames and is excluded from More Evidence.
    """
    rows = await _reporter_rows(session, ticket_id)
    if len(rows) < 2:
        return
    prefixes = [reporter_prefix(row["name"], row["oauth_id"]) for row in rows[1:]]
    try:
        await _replace_spreadsheet(client, issue_key, rows)
        await _refresh_sections(client, issue_key, prefixes)
    except Exception as error:  # noqa: BLE001
        logger.warning("shared sections update failed for %s: %s", issue_key, error)
```

In `link_ticket`, change the evidence upload at line 121 to rename this reporter's files:

```python
    reporter = job.payload.get("reporter", {})
    reporter_name = reporter.get("name") or job.user_sub
    prefix = reporter_prefix(reporter_name, job.user_sub)
    names = upload_names(prefix, [item["name"] for item in evidence_of(job)])
    await attach_evidence(job, client, match_key, names)
```

Then remove the now-duplicated `reporter`/`reporter_name` lines from inside the
`if existing is None:` block, and change the final call from
`await update_similar_reports(...)` to `await update_shared_sections(...)`.

- [ ] **Step 5: Run to verify it passes**

```bash
docker compose run --rm api pytest tests -q -m "not live"
```

Expected: all tests pass, including the earlier files.

- [ ] **Step 6: Commit**

```bash
git add Backend/src/app/worker/link_step.py Backend/src/app/jira/client.py Backend/tests/test_link_sections.py
git commit -m "feat: rebuild More Evidence and Affected Users on every link"
```

---

### Task 6: The structural gate in the agent's write tools

**Files:**
- Modify: `Backend/src/app/agent/tools/jira.py`
- Test: `Backend/tests/test_steps_gate.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - `missing_steps(kind: str, steps: list[str] | None) -> bool`
  - `STEPS_REQUIRED: str` — the refusal returned to the model
  - `link_to_existing` gains `steps_to_reproduce: list[str] | None = None`

- [ ] **Step 1: Write the failing test**

Create `Backend/tests/test_steps_gate.py`:

```python
"""Covers the predicate that refuses a bug with no reproduction steps."""

import pytest

from app.agent.tools.jira import STEPS_REQUIRED, missing_steps


@pytest.mark.parametrize("steps", [None, [], [""], ["   "]])
def test_bug_without_usable_steps_is_refused(steps):
    assert missing_steps("bug", steps) is True


def test_bug_with_steps_is_allowed():
    assert missing_steps("bug", ["Open the dashboard"]) is False


@pytest.mark.parametrize("steps", [None, [], ["Open the dashboard"]])
def test_feature_is_never_gated(steps):
    assert missing_steps("feature", steps) is False


def test_refusal_carries_the_termination_sentence():
    assert "Sorry, we can’t proceed with raising this issue." in STEPS_REQUIRED
    assert "not filed" in STEPS_REQUIRED.lower()
```

- [ ] **Step 2: Run to verify it fails**

```bash
docker compose run --rm api pytest tests/test_steps_gate.py -q
```

Expected: FAIL — `ImportError: cannot import name 'STEPS_REQUIRED'`.

- [ ] **Step 3: Implement the gate**

In `Backend/src/app/agent/tools/jira.py`, add after `_MAX_CANDIDATES`:

```python
STEPS_REQUIRED = (
    "Not filed. A bug needs steps to reproduce before it can reach the team, and none "
    "were given. The agent cannot see screenshots or video, so the steps are the only "
    "thing it can reason about. Ask the user for them. If they will not give them, reply "
    "with exactly: Sorry, we can’t proceed with raising this issue."
)


def missing_steps(kind: str, steps: list[str] | None) -> bool:
    """Report whether a bug is missing the reproduction steps it cannot be filed without.

    Blank entries do not count, so a list of empty strings is treated as no steps at all.
    Feature requests have no reproduction steps and are never gated.
    """
    return kind == "bug" and not [step for step in (steps or []) if str(step).strip()]
```

In `create_ticket`, immediately after the docstring:

```python
    if missing_steps(kind, steps_to_reproduce):
        return STEPS_REQUIRED
```

Change `link_to_existing`'s signature to add the argument before `runtime`:

```python
@tool
async def link_to_existing(
    issue_key: str,
    note: str,
    kind: Literal["bug", "feature"],
    runtime: ToolRuntime,
    steps_to_reproduce: list[str] | None = None,
) -> str:
```

Add to its `Args:` docstring block:

```
        steps_to_reproduce: The ordered steps this reporter described. Required for a
            bug: it is how the report is judged to be the same problem. Not written into
            the existing issue.
```

Add the same guard after its docstring, and thread the steps into the ticket dict:

```python
    if missing_steps(kind, steps_to_reproduce):
        return STEPS_REQUIRED
    ticket = {
        "title": issue_key,
        "summary": note,
        "issue_description": note,
        "steps_to_reproduce": steps_to_reproduce or [],
    }
```

- [ ] **Step 4: Run to verify it passes**

```bash
docker compose run --rm api pytest tests/test_steps_gate.py -q
```

Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git add Backend/src/app/agent/tools/jira.py Backend/tests/test_steps_gate.py
git commit -m "feat: refuse to file a bug without reproduction steps"
```

---

### Task 7: The skill's conversation flow

**Files:**
- Modify: `Backend/skills/bug-report-creation/SKILL.md`

**Interfaces:**
- Consumes: `STEPS_REQUIRED` wording from Task 6 — the skill and the refusal must agree
  on the termination sentence.
- Produces: no code interface. Task 8 asserts this task's behaviour.

- [ ] **Step 1: Rewrite Step 2's question list**

Replace the numbered list under `## Step 2` so it reads, in this order:

```markdown
1. **What goes wrong, and what did you expect instead?** (the error behaviour)
2. **Steps to reproduce** — required for every bug. Ask for them before anything else
   below. Never write a step the user did not describe: a guessed step sends a triager
   looking for a button that may not exist.
3. **Screenshots or a screen recording** — optional, and asked only after you have the
   steps. Do not ask for these in a message. Call `request_evidence`. [Evidence branch —
   see below]
4. **Browser** — captured automatically from the user's session. Do not ask by default;
   ask only to confirm when the bug looks browser-specific.
5. *(Optional, ask only if it helps triage)* **Does it happen every time or only
   sometimes?**
```

- [ ] **Step 2: Rewrite the Evidence Branch**

Replace the two bullets under `### Evidence Branch` with:

```markdown
- Evidence is optional. A user who has none still gets a ticket, as long as they gave
  the steps.
- You cannot see what they attach. The steps are what you reason about; the evidence is
  for the human triager.
```

Keep the existing paragraph about `request_evidence` being the only way to open the
picker.

- [ ] **Step 3: Add the stop branch to Step 4**

Add as the first bullet under `## Step 4 — Decide: associate, create, or stop`:

```markdown
- **No steps to reproduce:** do not create and do not associate. Explain that the report
  cannot reach the team without them and ask once more. If they still do not give them,
  reply with exactly this and nothing more:

  > Sorry, we can’t proceed with raising this issue.
```

- [ ] **Step 4: Delete the contradicting edge case**

Remove this bullet from `## Edge cases` entirely:

```markdown
- **Not enough detail and the user goes quiet:** create the ticket with what you have, mark the missing parts as "Not provided," and note it's ready for triage rather than blocking indefinitely.
```

- [ ] **Step 5: Update Step 4b's steps guidance**

Under `## Step 4b`, replace the `steps_to_reproduce` bullet with:

```markdown
- **steps_to_reproduce** — the ordered steps the user described. Always required; you
  will not be able to file without them.
```

- [ ] **Step 6: Verify the file still parses as a skill**

```bash
docker compose run --rm api python -c "from app.agent.skills import skill_body; print(skill_body('bug-report-creation')[:80])"
```

Expected: prints `# Bug Report Creation`.

- [ ] **Step 7: Commit**

```bash
git add Backend/skills/bug-report-creation/SKILL.md
git commit -m "docs: require reproduction steps and ask for them before evidence"
```

---

### Task 8: Behavioural verification against the live model

These tests call the real gateway, so they carry the `live` marker and are excluded from
the default run. **The VPN must be connected.**

**Files:**
- Create: `Backend/tests/live/test_bug_flow.py`

**Interfaces:**
- Consumes: everything above.
- Produces: the regression suite for the model-facing behaviour.

- [ ] **Step 1: Write the tests**

Create `Backend/tests/live/test_bug_flow.py`:

```python
"""End-to-end agent behaviour against the real gateway.

Marked live because each test drives the model. Run with:
docker compose run --rm api pytest tests/live -q -m live
"""

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from app.agent.context import TurnContext
from app.agent.factory import build_agent

pytestmark = pytest.mark.live

TERMINATION = "sorry, we can’t proceed with raising this issue."


async def _publish(event):
    return None


def _normalise(text):
    return text.replace("'", "’").strip().lower()


class Session:
    """One scripted conversation against the agent graph."""

    def __init__(self, name):
        self.agent = build_agent(InMemorySaver(), _publish)
        self.config = {"configurable": {"thread_id": name}}
        self.context = TurnContext(
            user_sub=f"u-{name}",
            conversation_id=name,
            surface="panel",
            reporter_name="Tester",
            client_environment={"browser": "Chrome 129"},
        )
        self.tools = []
        self.prose = ""
        self.drafts = []

    async def say(self, payload):
        self.tools, self.prose = [], ""
        async for chunk in self.agent.astream(
            payload, self.config, context=self.context, stream_mode="updates"
        ):
            for update in chunk.values():
                if not isinstance(update, dict):
                    continue
                for message in update.get("messages", []):
                    for call in getattr(message, "tool_calls", None) or []:
                        self.tools.append(call["name"])
                        if call["name"] in ("create_ticket", "link_to_existing"):
                            self.drafts.append(call["args"])
                    if type(message).__name__ == "AIMessage":
                        content = message.content
                        if isinstance(content, list):
                            content = "".join(
                                block.get("text", "")
                                for block in content
                                if isinstance(block, dict)
                            )
                        self.prose += content or ""
        state = await self.agent.aget_state(self.config)
        return state.interrupts[0].value if state.interrupts else None

    async def user(self, text):
        return await self.say({"messages": [{"role": "user", "content": text}]})


REPORT = "the dashboard chart goes blank when I switch to the yearly view"


@pytest.mark.parametrize("trial", range(3))
async def test_steps_are_asked_for_before_evidence(trial):
    session = Session(f"order-{trial}")
    await session.user(REPORT)

    assert "request_evidence" not in session.tools
    assert "step" in session.prose.lower()


@pytest.mark.parametrize("trial", range(3))
async def test_refusing_steps_terminates_without_filing(trial):
    session = Session(f"stop-{trial}")
    await session.user(REPORT)
    await session.user("I'd rather not write out the steps")
    await session.user("no, I'm not going to provide them")

    assert session.drafts == []
    assert TERMINATION in _normalise(session.prose)


@pytest.mark.parametrize("trial", range(3))
async def test_steps_without_evidence_still_file(trial):
    session = Session(f"file-{trial}")
    await session.user(REPORT)
    await session.user("Open the dashboard, click the yearly toggle, the chart blanks")
    value = await session.user("I don't have a screenshot")

    if isinstance(value, dict) and "evidence_request" in value:
        value = await session.say(Command(resume=[]))

    assert session.drafts, "expected a ticket to be drafted from steps alone"
    assert session.drafts[-1].get("steps_to_reproduce")


@pytest.mark.parametrize("trial", range(3))
async def test_no_step_is_invented(trial):
    session = Session(f"invent-{trial}")
    await session.user(REPORT)
    await session.user("I'm not going to describe the steps")
    await session.user("still no")

    for draft in session.drafts:
        assert not draft.get("steps_to_reproduce")
```

- [ ] **Step 2: Run them**

```bash
cd Backend
docker compose run --rm api pytest tests/live -q -m live
```

Expected: 12 passed. If `test_refusing_steps_terminates_without_filing` fails because the
model keeps asking rather than terminating, apply the escalation recorded in the spec:
count prior `STEPS_REQUIRED` refusals from `runtime.state["messages"]` inside the write
tools and drive the termination from that count. Do not weaken the assertion.

- [ ] **Step 3: Run the whole suite one last time**

```bash
docker compose run --rm api pytest tests -q -m "not live"
docker compose run --rm api pytest tests/live -q -m live
```

- [ ] **Step 4: Commit**

```bash
git add Backend/tests/live/
git commit -m "test: verify the mandatory-steps flow against the live model"
```

---

## Self-Review

**Spec coverage.** Every spec section maps to a task: gate → Task 6; ADF sections and
`replace_section` → Task 2; spreadsheet rename and migration → Tasks 3 and 5; evidence
naming → Task 4; link refresh and `list_attachments` size → Task 5; skill flow → Task 7;
testing → Tasks 1 and 8. The three out-of-scope defects stay out of scope.

**Known ordering hazard.** Task 3 renames `similar_reports.py`, which `link_step.py`
imports. The suite is red between Task 3 and Task 5. This is called out in Task 3 Step 4
so an executor does not "fix" it early and collide with Task 5.

**Type consistency.** `attach_evidence` takes a required fourth `names` argument from
Task 4 onward; both create-path call sites are updated in Task 4 Step 5 and the link-path
call site in Task 5 Step 4. `list_attachments` entries gain `size` in Task 5 Step 3,
which `linked_evidence` reads with `.get("size") or 0` so a stubbed attachment without
one still works.
