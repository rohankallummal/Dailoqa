"""End-to-end citation behaviour, against the real model and the real index.

Marked ``live``: these cost tokens and need both a model and a populated corpus, so CI runs
``pytest -m "not live"``. They are collected by default locally on purpose. This started life as
a standalone script, and a standalone script is exactly how a 16/16 citation rate quietly becomes
8/16 with nobody noticing — the middleware enforces that *a* citation exists, but only these
catch a regression in whether the answer is any good, whether the route is right, and whether an
off-corpus question is still declined.

Each case is one turn on a fresh thread. Nothing asserts on the model's prose, which varies run
to run; the assertions are on citation and retrieval behaviour, which should not.
"""

import re
from uuid import uuid4

import pytest
from langchain_core.messages import AIMessage

from app.agent.checkpointer import build_checkpointer
from app.agent.context import TurnContext
from app.agent.factory import build_agent
from app.agent.middleware.grounding import _claimed_topics
from app.rag.routes import route_for
from tests.conftest import corpus_page, corpus_sources

pytestmark = pytest.mark.live

_CITATION = re.compile(r"\[Doc\s*\d+", re.IGNORECASE)
# The trailing slash is captured, not discarded. An earlier version stopped before it, which
# meant a model writing "/docs/langgraph/" was silently normalised to the manifest value and the
# drift below could never be observed.
_ROUTE = re.compile(r"/docs/[a-z0-9-]+(?:/[a-z0-9-]+)*/?")


async def _answer(question: str) -> str:
    """One turn on a brand-new thread.

    The thread id must be unique per run. The checkpointer is persistent, so a fixed id makes
    every run append to the same conversation until it trips the per-thread model-call cap —
    tests that pass once and then fail forever, for a reason that looks like flakiness.
    """
    thread = f"live-test-{uuid4()}"
    context = TurnContext(
        user_sub="live-test", conversation_id=thread, surface="full", reporter_name="Live Test"
    )
    async with build_checkpointer() as saver:
        agent = build_agent(saver, lambda *_a, **_k: None)
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": question}]},
            {"configurable": {"thread_id": thread}},
            context=context,
        )
    answers = [m for m in result["messages"] if isinstance(m, AIMessage) and not m.tool_calls]
    return answers[-1].text if answers else ""


@pytest.mark.parametrize(
    "question",
    [
        # Two phrasings of a code request, because they behaved differently: the first was the
        # 0/4 case that exposed the missing code-citation rule, and the second still failed
        # after the first was fixed.
        "Show me the code to define a custom subagent.",
        "Give me a code example for creating an agent with a custom tool.",
        "What is a Skill and how does the agent load one?",
        "How do I add a guardrail to an agent?",
    ],
)
async def test_a_documentation_answer_cites_a_real_route(question):
    answer = await _answer(question)

    assert _CITATION.search(answer), f"no [Doc N] in the answer to {question!r}"
    routes = _ROUTE.findall(answer)
    assert routes, f"no /docs route in the answer to {question!r}"

    # Exact match, modulo a trailing slash. The slash is tolerated because Next 308-redirects it
    # so the link still lands, but nothing else is: SKILL.md tells the model to copy the label
    # verbatim, and a route it has edited in any other way is one that can 404. Catching the
    # difference here is the point — in the UI it looks like a broken citation, not a drift.
    known = {route_for(path) for path in corpus_sources()}
    for route in routes:
        assert route.rstrip("/") in known, (
            f"cited a route that is not in the manifest: {route!r}\n"
            f"the model is not copying the label verbatim; nearest known routes: "
            f"{sorted(k for k in known if k and k.split('/')[2] == route.split('/')[2])}"
        )


@pytest.mark.parametrize(
    "question",
    [
        "How do I configure single sign-on for Dailoqa?",
        "What does a Dailoqa Playbook cost per month?",
    ],
)
async def test_an_off_corpus_question_is_declined_without_citing(question):
    # The decline path must survive both the tightened gate and the new uncited-answer check:
    # a correct decline retrieves nothing, so it has nothing to cite and must not be bounced.
    answer = await _answer(question)
    assert not _CITATION.search(answer), f"cited documentation for an uncovered question: {answer[:160]}"


# Tolerates an adverb between the negation and the verb. The first version demanded "does not
# mention" adjacently and failed a perfectly correct "does not *specifically* mention", which is
# a test defect rather than a behaviour one -- the kind that gets a real fix reverted.
# Both apostrophe forms, because the model emits a curly one often enough to matter: a run
# failed on "doesn’t specifically mention" while the behaviour was perfectly correct. Tolerates
# an adverb between the negation and the verb for the same reason -- the first version demanded
# "does not mention" adjacently and reported a correct decline as a confabulation.
_DENIAL = re.compile(
    r"does(?:n['’]t| not)\s+(?:\w+\s+){0,2}"
    r"(?:mention|cover|describe|discuss|include|provide|specify|define|detail|address)"
    r"|no mention|not (?:mentioned|covered|documented|described)"
    r"|could(?:n['’]t| not) find|no .{0,12}reference",
    re.I,
)


@pytest.mark.parametrize(
    "question, invented_term",
    [
        ("i want you to explain me apache flow in deep agents", "apache flow"),
        ("what is the blorptastic subsystem in deep agents", "blorptastic"),
        ("how does the quantum tunneling module work in deep agents", "quantum tunneling"),
        ("explain the frobnicator in langgraph", "frobnicator"),
    ],
)
async def test_a_plausible_but_absent_concept_is_declined_not_explained(question, invented_term):
    """The hardest false positive: a question that borrows the corpus's own vocabulary.

    Retrieval cannot catch these and no gate value can. Measured on the live index, the best
    distance for these sits at 0.227-0.304 while legitimate questions run 0.126-0.314 -- "What
    is a Skill?" scores 0.314, worse than every nonsense query here, so any threshold that
    rejected these would reject the most basic real question in the corpus.

    What made it dangerous was the answer's shape: the model explained what the invented term
    "refers to" using whatever came back, then attached a real citation to it. The citation is
    precisely what makes an invented definition look verified.
    """
    answer = await _answer(question)
    assert _DENIAL.search(answer), (
        f"explained a term the documentation never mentions ({invented_term!r}):\n{answer[:400]}"
    )


@pytest.mark.parametrize(
    "question",
    ["how does context management work in deep agents", "What is a Skill?", "How do subagents work?"],
)
async def test_a_real_question_is_not_swept_up_by_the_relevance_check(question):
    # The counterweight. Declining everything would satisfy the test above, and this is what
    # stops that being a passing run.
    answer = await _answer(question)
    assert not _DENIAL.search(answer), f"declined a question the corpus covers:\n{answer[:300]}"
    assert _CITATION.search(answer), f"answered without citing:\n{answer[:300]}"


@pytest.mark.parametrize(
    "question",
    [
        "how can i calculate shortest distance between the nodes of langraph ?",
        "explain apache flow in deep agents",
        "How do subagents work in Deep Agents?",
        # Broad "how does X work" questions are what actually induce stacking: the answer spans
        # several sections and the easy ending is to list all of them. The three cases above
        # never triggered it, so the rule passed its test while "[Doc 1][Doc 2][Doc 3][Doc 4]
        # [Doc 5]" went out live on the question below. A test that cannot fail is not a guard.
        "How does persistence work in LangGraph?",
        "How do checkpointers and stores differ?",
        "How do Skills work in Deep Agents?",
    ],
)
async def test_tags_are_not_stacked_on_one_sentence(question):
    """One sentence, one source.

    A decline came back with "[Doc 1][Doc 2][Doc 3][Doc 4]" on a single line, from a sentence
    that surveyed everything the search had returned. Each tag was technically supported, which
    is why a rule about tags-per-claim did not stop it -- the fix was to say what a decline
    should *be*: what is missing, then one place to look, not an index of the search results.
    Four tags on a line tell a reader nothing about which source to open.
    """
    answer = await _answer(question)
    body = answer.split("Sources")[0]
    runs = [len(re.findall(r"\[Doc \d+\]", run)) for run in re.findall(r"(?:\[Doc \d+\]\s*){2,}", body)]
    worst = max(runs) if runs else 1
    assert worst <= 2, f"{worst} citations stacked on one sentence:\n{body[:300]}"


async def test_a_citation_points_at_the_section_it_quoted():
    # A page runs to thousands of words, so the page URL alone makes the reader hunt for the
    # paragraph. The anchor is what turns "here is my source" into "here is my source, here".
    answer = await _answer("can you provide me code for using subagents")
    anchored = re.findall(r"/docs/[a-z0-9/-]+#[a-z0-9-]+", answer)
    assert anchored, f"cited a page but not the section within it:\n{answer[-400:]}"


@pytest.mark.parametrize(
    "question",
    [
        "explain apache flow in deep agents",
        "how can i calculate shortest distance between the nodes of langraph ?",
        "How do subagents work in Deep Agents?",
        # Added after an audit found "https://docs/langgraph/subgraphs" in the wild -- the exact
        # shape this test's docstring names as the one that slips through. It escaped because
        # three fixed questions never produced it, not because the invariant held.
        "Why did LangGraph remove support for subgraphs?",
        "Where can I read more about checkpointers?",
        "Point me at the documentation for skills.",
    ],
)
async def test_an_invented_documentation_hostname_stays_repairable(question):
    """Doc links are site-relative, but the model sometimes writes them against a made-up host.

    Seen in the wild as "https://docs.dailoqa.com/docs/deepagents/subagents" and
    "https://docs.deepagents/subagents#using-compiledsubagent". Several rounds of instructing
    it not to did not hold, so the renderer now discards the host and keeps the path
    (`asDocsPath`), which is deterministic where the instruction was not.

    So this asserts what the repair depends on rather than pretending the model complies: any
    doc-ish URL it invents must carry a `/docs` path. One that did not — a bare
    "https://docs.dailoqa/deepagents" with the topic as the host — would slip through as a
    genuine external link and land the reader nowhere.
    """
    answer = await _answer(question)
    for url in re.findall(r"https?://[^\s)\]]*docs[^\s)\]]*", answer, re.I):
        path = re.sub(r"^https?://[^/]+", "", url)
        assert path.startswith("/docs"), (
            f"invented a documentation URL the renderer cannot repair: {url!r}"
        )


@pytest.mark.parametrize(
    "question, asked_about, documented_in",
    [
        ("What are guardrails in LangGraph?", "LangGraph", "LangChain"),
        ("How does persistence work in LangChain?", "LangChain", "LangGraph"),
    ],
)
async def test_the_answer_names_the_library_its_sources_document(
    question, asked_about, documented_in
):
    """The question's library is not automatically the answer's library.

    These three products are layered, so a question routinely names one and is answered out of
    another's page. Live, the model kept the questioner's word and produced "Guardrails in
    LangGraph are..." above five citations that were every one of them langchain/guardrails.md.

    Retrieval was not at fault -- it returned exactly the right passages, and for "subagents in
    LangChain" it ranked the genuinely correct cross-library page first. Only the prose was
    wrong, so this asserts on the pairing of prose and citation rather than on either alone.
    """
    answer = await _answer(question)
    assert re.search(rf"\b{documented_in}\b", answer), (
        f"never named {documented_in}, which is where this is actually documented:\n{answer[:300]}"
    )
    # Reuses the middleware's own reading of "credits" rather than a second regex here. A plain
    # search for "in LangGraph" reports the *correct* answer as a failure, because "does not cover
    # guardrails in LangGraph" contains it -- which is how the over-correction in the middleware
    # surfaced. One definition, used by both, cannot drift into disagreeing with itself.
    assert _claimed_topics(answer).isdisjoint({asked_about.lower().replace(" ", "")}), (
        f"credited the feature to {asked_about}, but it is documented under {documented_in}:"
        f"\n{answer[:300]}"
    )


@pytest.mark.parametrize(
    "question, false_premise",
    [
        ("Now that Skills are deprecated in Deep Agents, what should I use instead?", "deprecated"),
        ("Why did LangGraph remove support for subgraphs?", "removed"),
    ],
)
async def test_a_false_premise_in_the_question_is_corrected_not_adopted(question, false_premise):
    """A question can assert instead of ask, and answering it agrees to the assertion.

    Live, "now that Skills are deprecated" produced "With Skills deprecated in Deep Agents, you
    should now use Memory and Tools instead [Doc 1]" -- a fluent migration recommendation, with a
    real citation, for a deprecation that never happened. `deprecat` appears four times in the
    whole corpus and every one is about LangChain middleware parameters.

    The near-miss is just as bad and is why "did it decline?" is not the assertion: the subgraphs
    question came back with "it might be a recent change", which hands the premise back with an
    excuse attached rather than correcting it.
    """
    answer = await _answer(question)
    assert _DENIAL.search(answer) or re.search(r"\bnot\b.{0,30}" + false_premise, answer, re.I), (
        f"accepted a premise the documentation does not support:\n{answer[:400]}"
    )
    assert not re.search(r"might be|possible that|may have been|perhaps", answer, re.I), (
        f"speculated the false premise into plausibility instead of correcting it:\n{answer[:400]}"
    )


async def test_deep_agents_apis_are_not_relabelled_as_dailoqa():
    # LangChain, LangGraph and Deep Agents are libraries DailoQA builds on, not its own APIs.
    # Calling create_deep_agent "DailoQA" sends a reader looking in the wrong codebase, and it
    # crept in from the scope boundary naming DailoQA first.
    answer = await _answer("can you provide me code for using subagents")
    assert not re.search(r"(?:in|with|for|using)\s+DailoQA", answer, re.I), (
        f"attributed a Deep Agents API to DailoQA:\n{answer[:300]}"
    )


async def test_a_code_answer_carries_the_sample_and_its_source():
    # The end-to-end proof that snippet splicing reaches a user: this code exists only in
    # snippets/code-samples/subagents-compiled-subagent-py.mdx, never inline in the page.
    answer = await _answer("Show me the code to define a custom subagent.")
    assert "```" in answer, "expected a fenced code sample"
    assert "CompiledSubAgent" in answer
    assert route_for(corpus_page("subagents")) in answer
