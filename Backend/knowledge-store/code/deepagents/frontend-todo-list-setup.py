# --- Google ---
from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware

agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    middleware=[TodoListMiddleware()],
)

# --- OpenAI ---
from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware

agent = create_deep_agent(
    model="openai:gpt-5.5",
    middleware=[TodoListMiddleware()],
)

# --- Anthropic ---
from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    middleware=[TodoListMiddleware()],
)

# --- OpenRouter ---
from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware

agent = create_deep_agent(
    model="openrouter:z-ai/glm-5.2",
    middleware=[TodoListMiddleware()],
)

# --- Fireworks ---
from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware

agent = create_deep_agent(
    model="fireworks:accounts/fireworks/models/glm-5p2",
    middleware=[TodoListMiddleware()],
)

# --- Baseten ---
from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware

agent = create_deep_agent(
    model="baseten:zai-org/GLM-5.2",
    middleware=[TodoListMiddleware()],
)

# --- Ollama ---
from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware

agent = create_deep_agent(
    model="ollama:north-mini-code-1.0",
    middleware=[TodoListMiddleware()],
)
