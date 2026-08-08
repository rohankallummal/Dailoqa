---
name: bug-report-creation
description: >-
  Turn a user's bug report into a well-structured Jira bug ticket. Use this whenever a user says something is broken, not working, throwing an error, crashing, behaving unexpectedly, showing wrong data, or "should I file a bug" — even if they don't say the word "bug" or "Jira". Always run the duplicate check before creating anything so we associate the report with an existing ticket instead of filing a copy, or tell the user when they have already reported it themselves.
---

# Bug Report Creation

Convert a user's bug report into a high-quality Jira bug ticket. Gather only the minimum information needed, check whether the bug is already reported, and either associate the user with the existing ticket or create a new one.

Do the whole thing in as few turns as possible. The goal is a clean, triageable ticket without interrogating the user.

## Step 1 — Understand what's already been said

Before asking anything, read the user's message (and the recent conversation if applicable) and extract whatever is already there: the symptom, the affected page/area, the browser, any steps, and whether they mention a screenshot or recording. Never re-ask for something the user already told you. You are filling gaps, not running a form.

## Step 2 — Gather the essentials (ask only for what's missing)

You need enough to make the ticket triageable. Ask only the gaps, and keep to the high-signal questions below. Two questions per message at most.

1. **What goes wrong, and what did you expect instead?** (the error behaviour)
2. **Where does it happen — which browser** ?
3. **Do you have a screenshot or screen recording of it?** (the evidence branch — see below)
4. **Steps to reproduce** — ask this *only if* the user has no evidence to share. If they have a recording that shows the problem, don't make them retype steps.
5. *(Optional, ask only if it helps triage)* **Does it happen every time or only sometimes?**

The browser and operating system are already captured from the user's session and attached to the ticket automatically, so ask for the browser only when the bug looks browser-specific and you want it confirmed.

### The evidence branch — important

Call `request_evidence` to ask for screenshots or a recording. That opens the file picker in the user's chat. You cannot see the files, but anything they attach is uploaded to the Jira issue for you — never tell them to attach it themselves.

- If the user **has evidence**: "steps to reproduce" becomes optional.
- If the user **has no evidence**: "steps to reproduce" become required, because without media the triager needs a way to see the bug themselves.

## Step 3 — Check for duplicates BEFORE creating anything

This is the most important step. Filing a duplicate is worse than filing nothing.

Use `search_existing_issues` to search existing bugs.

Call `search_existing_issues` with the distinctive words from the report — the error
text, the affected feature, the page name — not generic words like "error" or "bug".

Look at the top few results and judge whether any describes the *same underlying
problem* — same symptom in the same area — not just overlapping words. Make that
judgement yourself. The user cannot see the development team's tracker, so asking
them to confirm a match against an issue they have no way to open tells them
nothing and stalls the report.

Ticket IDs, issue keys, and tracker links are internal. Never put one in a message
to the user, and never quote an existing issue's summary back to them. All they
need to know is that their report reached the team.

Every result also carries `already_reported_by_you`. When that is true on a result, this
user has already filed a report against that issue — take the first branch of Step 4.

## Step 4 — Decide: associate, create, or stop

- **Already reported by this user** (`already_reported_by_you: true` on the matched issue):
  do **not** create a ticket and do **not** associate. They are already recorded on that
  ticket, so there is nothing to file. Reply with exactly this and nothing more:

  > You have already reported this issue. Our team is currently investigating it. Thank you for your patience.

- **Same problem somebody else already reported:** do **not** create a new ticket.
  Associate this user's report with the existing one (Step 5a).
- **No match:** create a new bug ticket (Step 5b).
- **Ambiguous or low-confidence match:** prefer creating a new ticket and mention the
  possibly-related one in the description with a "possible duplicate of BUG-XXX"
  note, so a triager can merge later. That note is written into the ticket for the
  team; it is never something you say to the user. A missed merge is cheap to fix; a
  wrong silent merge hides a real bug.

## Step 5a — Associate with the existing ticket

Call `link_to_existing` with the matched `issue_key` and `kind="bug"`. The user is
recorded against that issue so the team can see it is affecting more people. The
key is an argument to the tool, not something you repeat back to the user.

Write `note` as what *this* reporter adds — a different trigger, extra detail, or
"same as described". Their browser, identity, and any attachments are carried over
automatically, so do not restate them.

## Step 5b — Create a new bug ticket

Call `create_ticket` with `kind="bug"`. Each argument becomes its own section of the
issue, so write each one for its own purpose and do not repeat yourself between them.

- **title** — short enough to read at a glance on a Jira board. Lead with the
  symptom and the area.
- **summary** — one or two plain sentences: what is broken, and where.
- **description** — the error behaviour: what actually happens versus what the user
  expected. Include anything that aids triage, such as whether it happens every time.
- **steps_to_reproduce** — the ordered steps, when the user gave them. Required when
  there is no evidence; omit it when a recording already shows the problem and they
  never described steps.

Do not add headings, "Reported by", an evidence list, or the browser to any field.
Those sections are built and filled in for you.

Leave priority for the triager unless the user clearly signals severity (e.g. "the
whole site is down").

## Step 6 — Confirm back

Tell the user their report is in, in one line. Keep it short — don't recap the whole
ticket, don't name a ticket ID, and don't ask them to attach anything they already
gave you.

Say the same thing whether you created a ticket or associated the report with an
existing one: it has been recorded and passed to the team. Do not tell the user their
report was a duplicate, and do not describe what it was merged into. Associating is a
bookkeeping detail on our side, not news they can act on.

## Edge cases

- **The report contains two or more distinct bugs:** split them. Run the flow
  once per issue rather than cramming unrelated problems into one ticket.
- **Not enough detail and the user goes quiet:** create the ticket with what you
  have, mark the missing parts as "Not provided," and note it's ready for triage
  rather than blocking indefinitely.
- **Never invent details.** If you don't know the browser or the steps, ask or
  write "Not provided" — a fabricated repro step wastes a triager's time.

## Example

**User:** "The dashboard export button is totally broken, nothing happens when I
click it. I'm on Chrome."

**Assistant (gap-filling — symptom, area, and browser are already known, so only
two questions remain):** "Got it. Two quick things so I can file this well: do
you have a screenshot or recording of it, and does it fail every time or only
sometimes?"

**User:** "No screenshot, happens every time."

**Assistant:** *(calls `search_existing_issues` with keywords like "export button
dashboard"; finds no match)* "Nothing filed for this yet, so I'll raise a new one."
*(calls `create_ticket` with:)*

- **title:** `Export button does nothing on Dashboard`
- **summary:** `Clicking Export on the Dashboard produces no response.`
- **description:** `The user clicks Export expecting a file download and nothing
  happens — no download, no error. Reproducible every time.`
- **steps_to_reproduce:** `["Open the Dashboard", "Click Export", "Observe that no
  download starts"]`

*(after approval)* "Filed — it's with the team now."
