"""The record of what the agent established about a bug before it may be filed.

A report is only triageable once someone knows what the user was trying to do, what they
expected, what happened instead, how often it happens, and whether it can be reproduced.
Those five facts are recorded through one tool, and the write tools refuse a filing until
they exist. Gating on this rather than on reproduction steps alone is what separates
investigating a bug from collecting a form: steps describe a route to the symptom, while
these describe the problem.

The tool cannot check whether a recorded fact is true, but it can check that the agent asked
before declaring a fact unknowable. A record carrying gaps is refused the first time with
those gaps named; it is accepted only once the agent has put them to the user and the user
has replied. That removes the two cheapest ways past the gate -- inferring all five from the
symptom, and writing every one of them off as unestablished without a word to the user --
while still letting a genuine "I don't know" through on the second pass.
"""

import json
from typing import Literal

from langchain.tools import ToolRuntime, tool
from langchain_core.messages import HumanMessage

FINDINGS_MARKER = "FINDINGS RECORDED"

UNESTABLISHED = "NOT ESTABLISHED"

AREAS = (
    ("user_goal", "what the user was trying to do"),
    ("expected", "what they expected to happen"),
    ("actual", "what happened instead"),
    ("frequency", "whether it happens every time or only sometimes"),
)

_REPRODUCIBLE_GAP = "whether the problem can be reproduced"

_GAP_PHRASES = frozenset({"unknown", "not provided", "not specified", "not sure", "unclear", "n/a"})

FINDINGS_FIRST = (
    "Refused. You have not established what this bug actually is yet, so there is nothing "
    "for this to supplement. Call record_findings first."
)

FINDINGS_REQUIRED = (
    "Not filed. Nothing is recorded about what this bug actually is. Call record_findings "
    "with what the user was doing, what they expected, what happened instead, how often it "
    "happens, and whether they can reproduce it."
)

_BLANK = (
    "Nothing recorded. Left empty: {fields}. Each one needs either what the user told you, "
    f"or exactly {UNESTABLISHED} when you asked and they could not say. Never leave one "
    "blank, and never fill one in by guessing from the symptom."
)

GAPS_REFUSED_MARKER = "GAPS NOT YET PUT TO THE USER"

_GAPS_REFUSED = (
    GAPS_REFUSED_MARKER + "\nNothing recorded. You marked these as unestablished without "
    "asking the user about them: {gaps}. Ask now, in your next message, in your own words "
    "and as flowing prose rather than a list. Then call this again with whatever they say. "
    "If they tell you they do not know, record it as unestablished then and it will be "
    "accepted. Do not infer any of it from the symptom, and do not call this again before "
    "they have replied."
)


def is_unestablished(value) -> bool:
    """Whether a recorded fact says the agent could not establish it.

    Matches the sentinel and the handful of phrasings a model reaches for instead of it,
    so a gap is treated as a gap rather than written into the ticket as a finding.
    """
    normalized = " ".join(str(value or "").split()).strip(".").lower()
    return not normalized or normalized in _GAP_PHRASES or normalized.startswith("not established")


def _last_refusal(messages) -> int | None:
    """Return the index of the most recent gaps refusal, or None if there has not been one."""
    for index in range(len(messages) - 1, -1, -1):
        message = messages[index]
        if getattr(message, "name", None) == "record_findings" and str(message.content).startswith(
            GAPS_REFUSED_MARKER
        ):
            return index
    return None


def gaps_unasked(messages) -> bool:
    """Whether the agent still owes the user a question about the gaps it wants to record.

    True until a refusal has been issued and the user has replied to it. Requiring the reply
    is what stops the refusal being satisfied by calling straight back with the same gaps.

    Only a typed reply counts. ``request_steps`` and ``request_evidence`` both resume through
    ``interrupt``, so what the user gives them lands as a tool result rather than a human
    turn -- which is right, because neither one asks about the problem itself.
    """
    refused_at = _last_refusal(messages)
    if refused_at is None:
        return True
    return not any(isinstance(message, HumanMessage) for message in messages[refused_at + 1 :])


def _gaps(findings: dict) -> list[str]:
    """Name every area the findings leave unestablished, in the order they are asked about."""
    missing = [label for field, label in AREAS if is_unestablished(findings.get(field))]
    if findings.get("reproducible") == "unknown":
        missing.append(_REPRODUCIBLE_GAP)
    return missing


@tool
async def record_findings(
    user_goal: str,
    expected: str,
    actual: str,
    frequency: str,
    reproducible: Literal["yes", "no", "unknown"],
    runtime: ToolRuntime,
) -> str:
    """Record what you have established about a bug. Required before you can file one.

    Call this once you have built a picture of the problem, not before. Take every field
    from what the user actually told you, in your own third-person prose.

    Where they have not told you, pass exactly NOT ESTABLISHED. Do not fill a field in
    because a plausible answer is easy to write: a user who has described what went wrong
    once has told you nothing about how often it happens, so "It has happened every time"
    is an invention, not a finding, and it sends the team chasing something nobody
    reported. A visible gap costs you nothing and costs them far less.

    Re-call it to replace an earlier record once you learn more; the newest one is used.

    These are joined into the ticket in the order below, so each must be a complete
    sentence that names what it is on its own. A bare phrase like "a PDF with 12 rows"
    leaves a triager unable to tell an expectation from a result. Follow the shapes shown.

    Args:
        user_goal: What the user was trying to accomplish -- the task, not the click.
            E.g. "The user was exporting a Q3 client report to send to their manager."
        expected: What they expected to happen.
            E.g. "They expected a PDF containing all 12 rows shown on screen."
        actual: What happened instead, including any error message in their words.
            E.g. "Instead a 0 KB PDF downloaded that will not open, with no error shown."
        frequency: Whether it happens every time or only sometimes, and since when.
            E.g. "It has happened every time since Friday." NOT ESTABLISHED unless the user
            actually told you -- this is not deducible from the symptom.
        reproducible: "yes" if the user has told you they can make it happen on demand, "no"
            if they have told you they cannot, "unknown" if you asked and they do not know.
            Use "unknown" rather than assuming "yes" because the bug sounds repeatable. A bug
            marked "no" is filed without reproduction steps, so never use it as a shortcut
            past collecting them.
    """
    findings = {
        "user_goal": user_goal,
        "expected": expected,
        "actual": actual,
        "frequency": frequency,
        "reproducible": reproducible,
    }
    blank = [field for field, _ in AREAS if not str(findings.get(field) or "").strip()]
    if blank:
        return _BLANK.format(fields=", ".join(blank))
    gaps = _gaps(findings)
    if gaps and gaps_unasked((runtime.state or {}).get("messages") or []):
        return _GAPS_REFUSED.format(gaps="; ".join(gaps))
    return f"{FINDINGS_MARKER}\n{json.dumps(findings)}"


def recorded_findings(messages) -> dict:
    """Return the findings recorded for this report, or an empty dict when there are none.

    The thread is the record, so this survives the resume that re-executes a suspended
    tool and needs no state schema of its own.
    """
    for message in reversed(messages):
        if getattr(message, "name", None) != "record_findings":
            continue
        content = str(message.content)
        if content.startswith(FINDINGS_MARKER):
            return json.loads(content[len(FINDINGS_MARKER) :])
    return {}


def _sentence(text) -> str:
    """Collapse whitespace and add the full stop the model may have left off."""
    stripped = " ".join(str(text).split())
    if not stripped or stripped[-1] in ".!?":
        return stripped
    return f"{stripped}."


def issue_description(findings: dict) -> str:
    """Compose the ticket's Issue Description from the recorded findings.

    Established facts are joined in a fixed order so every bug reads the same way to a
    triager, and anything the user could not say is named in a closing sentence rather
    than quietly omitted -- a visible gap tells the team the answer is unknown, where a
    silent one leaves them unable to tell that from an agent that never asked.
    """
    parts = [
        _sentence(findings.get(field))
        for field, _ in AREAS
        if not is_unestablished(findings.get(field))
    ]
    if findings.get("reproducible") == "yes":
        parts.append("The user can reproduce this on demand.")
    if findings.get("reproducible") == "no":
        parts.append("The user cannot reproduce this on demand.")
    gaps = _gaps(findings)
    if gaps:
        parts.append(f"Not established: {'; '.join(gaps)}.")
    return " ".join(part for part in parts if part)
