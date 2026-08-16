# Mandatory Reproduction Steps for Bug Reports

Date: 2026-08-16
Status: approved for planning

## Problem

The bug-report agent can file a Jira ticket with neither reproduction steps nor
evidence. When it does, it fabricates the steps: given only "the dashboard chart goes
blank when I switch to the yearly view", it filed `["Open the dashboard", "Select the
yearly view from the chart options", "Observe that the chart goes blank"]`. Step 2
asserts a "chart options" menu the reporter never mentioned. A triager follows it,
cannot find it, and bounces the ticket.

Two rules in `SKILL.md` cause this. Step 2 item 4 makes steps *required* when there is
no evidence; the Edge cases section says *never invent* them. When the user supplies
neither, the model satisfies the requirement by inventing.

The agent cannot see images or video. Steps are therefore the only input it can reason
about — the only thing that lets it judge whether a report matches an existing issue or
warrants a new one. Evidence is for the human triager; steps are for the agent.

## Decisions

Settled with the project owner before writing this spec:

1. Steps to reproduce are mandatory for bug tickets, on both the create and the link
   path. Evidence is optional on both.
2. The agent asks for steps **first**, evidence second. This reverses today's order.
3. Without steps: explain, ask exactly once more, then terminate the run with the
   fixed sentence `Sorry, we can’t proceed with raising this issue.` — reproduced
   verbatim from the request, curly apostrophe included. Assertions on it normalise
   apostrophes so a straight-quote rendering does not fail the test.
4. The link path keeps its `Also reported by {name}` comment and its `also-affected`
   label. "Only two new sections" governs the description body.
5. Evidence uploaded on the link path is renamed `{oauth_name}-{oauth_id}-{n}`, matching
   the Affected Users spreadsheet columns so a triager can map a file to a row.
6. **More Evidence** holds only the files of reporters who linked after the issue was
   created. The original filer's evidence stays in the existing Evidence section under
   its original filenames, and is never renamed.
7. Feature requests are untouched. They have no reproduction steps.

## Behaviour

### Creating a bug ticket

- `steps_to_reproduce` must be non-empty. Evidence may be absent.
- Never invent a step. If the user did not describe it, it does not go in the list.

### Linking to an existing ticket

- The linking reporter must also supply steps. They are used for the agent's matching
  judgement and as proof the reporter genuinely hit the bug; they are **not** written
  into the issue.
- Exactly two sections are added to the issue description:
  - **More Evidence** — images and video from every reporter who linked afterwards.
  - **Affected Users** — the spreadsheet of everyone affected.

### Conversation flow

1. Ask what goes wrong and what was expected.
2. Ask for steps to reproduce.
3. Ask for evidence, via `request_evidence`. Optional; the user may decline.
4. Duplicate check, then create or link.

If steps are missing at step 2, explain that the issue cannot be raised without them
and ask once more. If they are still missing, reply with exactly:

> Sorry, we can’t proceed with raising this issue.

The run ends. The conversation stays open; the user may return with steps and start
again.

## Ticket structure

### Bug description, create path

| Section | Today | After |
| --- | --- | --- |
| Summary | always | unchanged |
| Evidence | when files attached | unchanged |
| Issue Description | always | unchanged |
| Client Environment | always | unchanged |
| Steps to Reproduce | only when there is **no** evidence | **always** |
| Reported By | always | unchanged |

Section order is unchanged. `adf.py:185` currently gates Steps to Reproduce on
`if not evidence and steps`; that condition is removed.

### Bug description, link path

`Similar Reports` is replaced by:

- **More Evidence** — a bulleted list, one line per file, formatted as the existing
  Evidence section does: `{filename} ({category}, {size})`.
- **Affected Users** — a paragraph pointing at the attached spreadsheet.

## Implementation

### Gate — `app/agent/tools/jira.py`

Both write tools refuse rather than enqueue when `kind == "bug"` and there are no
steps. No `Job` row is created, so the worker never runs.

- `create_ticket` already receives `steps_to_reproduce`. Keep it optional in the schema:
  making it a required argument invites the model to invent a value to satisfy the
  schema, which is the defect this spec exists to remove.
- `link_to_existing` gains a `steps_to_reproduce` argument. It currently hardcodes
  `"steps_to_reproduce": []` (`jira.py:196`). The value gates the call and feeds the
  worker's duplicate matching; it is not written to Jira.

The refusal string tells the model to ask the user for steps, and says the report was
not filed.

### Sections — `app/jira/adf.py`

- Replace `SIMILAR_REPORTS_HEADING` / `similar_reports_section` with
  `MORE_EVIDENCE_HEADING` + `more_evidence_section(files)` and
  `AFFECTED_USERS_HEADING` + `affected_users_section(filename)`.
- Add `replace_section(document, heading, nodes)`. More Evidence changes every time
  somebody links, so it must be regenerated, not appended once. The helper finds the
  heading and replaces through to the next heading of the same level, appending when
  the heading is absent. `append_nodes` and `has_heading` remain for the append-once
  callers.

### Link path — `app/worker/link_step.py`

- `_replace_spreadsheet` becomes the Affected Users refresh.
- New `_refresh_more_evidence`: read `list_attachments(issue_key)`, keep the files
  whose names carry the `{oauth_name}-{oauth_id}-` prefix of any **linked** reporter,
  and rebuild the section from them.
  Reading the live issue rather than tracking filenames in the database keeps this
  self-healing on retry and needs no schema change.
- Both refreshes stay inside the existing swallow-and-log block. The reporter row and
  the evidence upload remain the load-bearing work.

### Evidence naming — `app/worker/evidence_step.py`

- On the link path only, upload as `{safe(oauth_name)}-{safe(oauth_id)}-{n}{ext}`.
  `n` counts that reporter's own files, from 1, in stable source-filename order, so two
  reporters on one issue each start at 1 and their prefixes keep them apart. The
  extension is preserved from the source file.
- Idempotency moves to the renamed values: compare the target names against
  `list_attachment_filenames`. The names are deterministic per reporter, so a retry
  computes the same set and skips what is already there.
- The create path keeps original filenames.

### Spreadsheet — `app/jira/similar_reports.py`

- `SIMILAR_REPORTS_FILENAME` becomes `affected-users.xlsx`; the sheet title becomes
  `Affected Users`. Columns are unchanged.
- **Migration:** `_replace_spreadsheet` deletes by filename. Issues already carrying
  `similar-reports.xlsx` would keep it alongside the new file, and their description
  would keep a stale `Similar Reports` heading. The refresh must therefore delete both
  the old and the new filename, and remove a `Similar Reports` section if present.
  This runs on the next link to a given issue and needs no backfill.

### Skill — `skills/bug-report-creation/SKILL.md`

- Step 2: the question list becomes, in order —
  1. What goes wrong, and what did you expect instead?
  2. **Steps to reproduce** — required, always asked, never inferred.
  3. **Screenshots or a screen recording** — optional; call `request_evidence`.
  4. Browser — captured automatically; ask only to confirm a browser-specific bug.
  5. *(Optional)* Does it happen every time or only sometimes?
- Evidence Branch: keep the imperative `request_evidence` wording added on 2026-08-16;
  drop the "steps become required when there is no evidence" conditional, since steps
  are now always required.
- Step 4: add the stop branch with the exact termination sentence.
- Delete the contradicting edge case: *"Not enough detail and the user goes quiet:
  create the ticket with what you have, mark the missing parts as 'Not provided'"*.

### Client — `app/jira/client.py`

`list_attachments` returns only `{id, filename}`. Add `size` from the same payload so
More Evidence can match the existing Evidence section's formatting. Category is derived
from the filename with the existing `categorize()`.

## Testing

Hard guarantees, asserted on state rather than wording:

- Bug with no steps → zero `Job` rows, on both the create and the link path.
- Bug with steps and no evidence → files normally.
- Bug with steps and evidence → files normally, evidence attached.
- Feature request → unaffected by the gate.

Behavioural, run as repeated trials across differing report phrasings, because a fix
verified on one phrasing has already been shown this session to fail on another:

- Steps are asked for before evidence.
- A user who never gives steps is asked exactly once more, then receives the exact
  termination sentence.
- No fabricated steps reach `create_ticket` when the user described none.

Link path:

- Later reporters' files are uploaded as `{name}-{id}-{n}`; the original filer's are
  untouched.
- More Evidence lists every later reporter's files and is regenerated, not duplicated,
  across successive links.
- A retried link produces no duplicate attachments and no second section.
- An issue holding `similar-reports.xlsx` ends up with only `affected-users.xlsx` and
  no `Similar Reports` heading.

## Out of scope

Known defects, found while designing this, deliberately not fixed here:

- The `note` argument on `link_to_existing` is written by the model and then discarded —
  `link_ticket` never reads `job.payload["ticket"]`. It reaches Jira nowhere.
- A linking reporter's browser and operating system are captured but never recorded on
  the issue. The Affected Users spreadsheet holds name, id, and date only.
- `Ticket-Structure.md`, cited by `adf.py:173` and `adf.py:192` as the authority for
  section order, does not exist in the repository.

## Risks

The two-strike ask-and-terminate flow is enforced by prose in `SKILL.md`, because
judging whether a reply constitutes usable steps is a judgement the model has to make.
`azure-gpt-4o-mini` has twice this session failed to honour prose instructions that were
not backed by code. The gate itself is structural and cannot be talked around, so the
worst case is a badly paced conversation, not a bad ticket.

If trials show the model asking indefinitely or terminating on the first refusal, the
escalation is to count prior refusals from `runtime.state["messages"]` inside the write
tools, the same technique that fixed the `request_evidence` repeat loop, and drive the
termination from that count instead of from the model's judgement.
