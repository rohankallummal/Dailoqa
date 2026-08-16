# --- Google ---
from langchain.agents import create_agent

agent = create_agent(model="google_genai:gemini-3.6-flash", tools=tools)

# --- OpenAI ---
from langchain.agents import create_agent

agent = create_agent(model="openai:gpt-5.5", tools=tools)

# --- Anthropic ---
from langchain.agents import create_agent

agent = create_agent(model="anthropic:claude-sonnet-4-6", tools=tools)

# --- OpenRouter ---
from langchain.agents import create_agent

agent = create_agent(model="openrouter:z-ai/glm-5.2", tools=tools)

# --- Fireworks ---
from langchain.agents import create_agent

agent = create_agent(model="fireworks:accounts/fireworks/models/glm-5p2", tools=tools)

# --- Baseten ---
from langchain.agents import create_agent

agent = create_agent(model="baseten:zai-org/GLM-5.2", tools=tools)

# --- Ollama ---
from langchain.agents import create_agent

agent = create_agent(model="ollama:north-mini-code-1.0", tools=tools)
