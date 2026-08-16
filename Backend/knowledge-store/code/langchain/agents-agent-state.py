# --- Google ---
from langchain.agents import AgentState, create_agent


class MyState(AgentState):
    user_id: str
    call_count: int


agent = create_agent(
    model="google_genai:gemini-3.5-flash",
    tools=[],
    state_schema=MyState,  # [!code highlight]
)

# --- OpenAI ---
from langchain.agents import AgentState, create_agent


class MyState(AgentState):
    user_id: str
    call_count: int


agent = create_agent(
    model="openai:gpt-5.5",
    tools=[],
    state_schema=MyState,  # [!code highlight]
)

# --- Anthropic ---
from langchain.agents import AgentState, create_agent


class MyState(AgentState):
    user_id: str
    call_count: int


agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[],
    state_schema=MyState,  # [!code highlight]
)

# --- OpenRouter ---
from langchain.agents import AgentState, create_agent


class MyState(AgentState):
    user_id: str
    call_count: int


agent = create_agent(
    model="openrouter:z-ai/glm-5.2",
    tools=[],
    state_schema=MyState,  # [!code highlight]
)

# --- Fireworks ---
from langchain.agents import AgentState, create_agent


class MyState(AgentState):
    user_id: str
    call_count: int


agent = create_agent(
    model="fireworks:accounts/fireworks/models/glm-5p2",
    tools=[],
    state_schema=MyState,  # [!code highlight]
)

# --- Baseten ---
from langchain.agents import AgentState, create_agent


class MyState(AgentState):
    user_id: str
    call_count: int


agent = create_agent(
    model="baseten:zai-org/GLM-5.2",
    tools=[],
    state_schema=MyState,  # [!code highlight]
)

# --- Ollama ---
from langchain.agents import AgentState, create_agent


class MyState(AgentState):
    user_id: str
    call_count: int


agent = create_agent(
    model="ollama:north-mini-code-1.0",
    tools=[],
    state_schema=MyState,  # [!code highlight]
)
