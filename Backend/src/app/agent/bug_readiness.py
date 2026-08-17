"""What a bug report must have before it may be written anywhere.

Both write tools answer to this, which is why it sits outside them.

It runs inside the tool body, which means after the user has approved the filing:
``HumanInTheLoopMiddleware`` suspends the call from ``after_model``, a hook that fires before
the tool node, so nothing at the tool layer can precede the confirmation. That makes this a
hard backstop rather than an early warning -- an incomplete report can be drafted and shown,
but it cannot be written. Keeping the agent from drafting one in the first place is the
skill's job, not this one's.
"""

from app.agent.tools.evidence import evidence_requested
from app.agent.tools.investigation import FINDINGS_REQUIRED, recorded_findings
from app.agent.tools.steps import captured_steps, missing_steps

STEPS_REQUIRED = (
    "Not filed. A bug the user can reproduce needs its steps before it can reach the team, "
    "and they have not given any. Call request_steps to ask them. Do not write the steps "
    "yourself: they are captured from the user's own reply and attached for you."
)

EVIDENCE_REQUIRED = (
    "Not filed. The user has not been offered the chance to attach a screenshot or a "
    "recording yet. Call request_evidence first. They are free to decline and the report "
    "is filed either way, but they have to be asked."
)


def bug_refusal(messages) -> str | None:
    """Return why this bug cannot be written yet, or None when it is ready.

    Both write paths answer to it: a link is judged to be the same problem from the same
    understanding a new ticket is written from, so neither may skip the investigation.
    """
    findings = recorded_findings(messages)
    if not findings:
        return FINDINGS_REQUIRED
    if missing_steps(captured_steps(messages), findings.get("reproducible")):
        return STEPS_REQUIRED
    if not evidence_requested(messages):
        return EVIDENCE_REQUIRED
    return None
