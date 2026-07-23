"""Assembly of the ticket agent StateGraph and the enqueue step."""

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from app.agent.classify import classify_message
from app.agent.dedupe import find_duplicate
from app.agent.gather import missing_fields, next_follow_up
from app.agent.state import AgentState
from app.db.models import Job


async def enqueue_job(session, state: AgentState) -> str:
    """Insert a queued create_ticket job from confirmed agent state; return its id."""
    job = Job(
        type="create_ticket",
        status="queued",
        conversation_id=state["conversation_id"],
        user_sub=state["user_sub"],
        payload={
            "kind": state["kind"],
            "fields": state.get("fields", {}),
            "dedupe_key": state.get("dedupe_key"),
        },
    )
    session.add(job)
    await session.flush()
    return job.id


def build_graph(model_classifier=None, model_agent=None, jira_client=None):
    """Build the (uncompiled) ticket agent graph.

    Compile with a checkpointer at run time: build_graph().compile(checkpointer=saver).
    """
    builder = StateGraph(AgentState)

    async def classify(state: AgentState) -> AgentState:
        text = state["messages"][-1]
        result = await classify_message(text, model=model_classifier)
        return {"kind": result.kind, "reply": result.reason}

    async def gather(state: AgentState) -> AgentState:
        missing = missing_fields(state["kind"], state.get("fields", {}))
        if missing:
            question = await next_follow_up(state["kind"], state.get("fields", {}), model=model_agent)
            answer = interrupt({"question": question, "missing": missing})
            fields = {**state.get("fields", {}), **answer}
            return {"fields": fields}
        return {}

    async def preview_dedupe(state: AgentState) -> AgentState:
        verdict = await find_duplicate(state["kind"], state.get("fields", {}), client=jira_client, model=model_agent)
        return {"dedupe_key": verdict.match_key}

    async def confirm(state: AgentState) -> AgentState:
        decision = interrupt({"summary": state.get("fields", {}), "dedupe_key": state.get("dedupe_key")})
        return {"confirmed": bool(decision)}

    async def enqueue(state: AgentState) -> AgentState:
        return {"reply": "Creating your ticket in the background."}

    builder.add_node("classify", classify)
    builder.add_node("gather", gather)
    builder.add_node("preview_dedupe", preview_dedupe)
    builder.add_node("confirm", confirm)
    builder.add_node("enqueue", enqueue)

    builder.add_edge(START, "classify")
    builder.add_conditional_edges(
        "classify",
        lambda s: "gather" if s["kind"] in ("bug", "feature") else END,
        {"gather": "gather", END: END},
    )
    builder.add_conditional_edges(
        "gather",
        lambda s: "gather" if missing_fields(s["kind"], s.get("fields", {})) else "preview_dedupe",
        {"gather": "gather", "preview_dedupe": "preview_dedupe"},
    )
    builder.add_edge("preview_dedupe", "confirm")
    builder.add_conditional_edges(
        "confirm",
        lambda s: "enqueue" if s.get("confirmed") else END,
        {"enqueue": "enqueue", END: END},
    )
    builder.add_edge("enqueue", END)
    return builder
