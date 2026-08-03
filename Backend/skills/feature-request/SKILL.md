---
name: feature-request
description: >-
  Turn a user's idea or complaint about a missing capability into a well-formed Jira
  feature request. Use whenever a user asks for something the product does not do
  yet, says "it would be great if", wishes a workflow were easier, or proposes an
  improvement — even if they never say the words "feature" or "request".
---

# Feature Request Creation

Turn a user's idea into a request the product team can evaluate. The valuable part
is the *problem*, not the proposed solution — capture both, but never file a request
whose problem statement is empty.

## Step 1 — Read what they already said

Extract the desired capability and any pain point they described. Do not re-ask for
either if it is already there.

## Step 2 — Fill only the real gaps

You need two things to file:

1. **What they want** — the capability, in their terms.
2. **Why** — the problem it solves, or what it currently costs them.

If they described a solution but not a problem, ask what they are trying to
accomplish. That single question is usually the whole difference between a request
that gets built and one that gets closed as unclear.

## Step 3 — Check it is not already requested

Call `search_existing_issues` with `kind="feature"` and the distinctive words from
their idea. If a candidate plausibly describes the same capability, show it and ask
in one line whether that is what they mean. On a confirmed match, call
`link_to_existing` instead of creating a duplicate.

## Step 4 — File it

Call `create_ticket` with `kind="feature"`:

- **title** — the capability, short enough to scan on a board.
- **summary** — one or two plain sentences on what is being asked for.
- **description** — the capability, then the problem it solves and why it matters.
  Attribute the reasoning to the user; do not invent business justification.

## Step 5 — Confirm back

Give the key and link in one line. Do not recap the request.

## Edge cases

- **Two unrelated ideas in one message:** file them separately.
- **It already exists in the product:** say so and point them at it. Do not file.
- **They are actually reporting something broken:** that is a bug — load the
  `bug-report-creation` skill instead.
