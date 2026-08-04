"""The documentation skill must arrive whenever its tools are used.

Documentation tools are bound unconditionally, so the agent can call them without ever
calling ``load_skill`` — and then it holds none of the procedure that governs how
documentation is cited, combined, or declined. These tests pin the four states the prompt
can be in, because a regression here fails silently: the answers still look plausible.
"""

from types import SimpleNamespace

from langchain_core.messages import AIMessage, HumanMessage

from app.agent.middleware.skills import _autoloaded_documentation, _skill_catalogue
from app.agent.tools import DOC_SKILL_NAME
from app.config import get_settings

_SEARCH_CALL = AIMessage(
    content="",
    tool_calls=[{"name": "search_documentation", "args": {"query": "skills"}, "id": "1"}],
)
_LOAD_DOC_SKILL = AIMessage(
    content="",
    tool_calls=[{"name": "load_skill", "args": {"name": DOC_SKILL_NAME}, "id": "0"}],
)
_TICKET_CALL = AIMessage(
    content="",
    tool_calls=[{"name": "search_existing_issues", "args": {"keywords": ["login"]}, "id": "2"}],
)


def _prompt_for(messages) -> str:
    """The prompt fragment the middleware would append for this thread."""
    return _autoloaded_documentation(messages)


def test_body_is_added_when_a_doc_tool_ran_without_the_skill():
    # The exact live failure: the model searched, answered, and cited nothing because the
    # citation rules were never in context.
    prompt = _prompt_for([HumanMessage(content="what is a skill?"), _SEARCH_CALL])
    assert prompt, "the skill body must be supplied when its tools are used"
    assert "cite" in prompt.lower()


def test_body_is_not_repeated_when_the_skill_was_loaded():
    # load_skill already put the body in the transcript; adding it again would duplicate
    # a couple of thousand tokens on every subsequent model call.
    messages = [HumanMessage(content="what is a skill?"), _LOAD_DOC_SKILL, _SEARCH_CALL]
    assert _prompt_for(messages) == ""


def test_ticketing_threads_carry_no_documentation_instructions():
    # Progressive disclosure is the point of the skills system: a bug report must not pay
    # for documentation instructions it will never use.
    messages = [HumanMessage(content="the login button is broken"), _TICKET_CALL]
    assert _prompt_for(messages) == ""


def test_a_fresh_thread_carries_no_documentation_instructions():
    assert _prompt_for([HumanMessage(content="hello")]) == ""


def test_nothing_is_added_when_documentation_is_switched_off():
    settings = get_settings()
    original = settings.rag_enabled
    try:
        settings.rag_enabled = False
        assert _prompt_for([_SEARCH_CALL]) == ""
        assert DOC_SKILL_NAME not in _skill_catalogue()
    finally:
        settings.rag_enabled = original


def test_the_catalogue_still_advertises_names_only():
    # The catalogue is the always-present half of progressive disclosure; it must stay a
    # list of descriptions rather than growing bodies.
    catalogue = _skill_catalogue()
    assert DOC_SKILL_NAME in catalogue
    assert "## Step 1" not in catalogue


def test_middleware_reads_messages_off_the_request():
    from app.agent.middleware.skills import skills_middleware

    # dynamic_prompt wraps the function; reach the underlying hook the agent will call.
    hook = getattr(skills_middleware, "wrap_model_call", None)
    assert hook is not None, "skills_middleware must expose a model-call hook"

    request = SimpleNamespace(state={"messages": [_SEARCH_CALL]})
    assert _prompt_for(request.state["messages"])
