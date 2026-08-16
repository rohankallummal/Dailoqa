# --- Google ---
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    system_prompt="""...your instructions...

    IMPORTANT: For complex tasks, delegate to your subagents using the task() tool.
    This keeps your context clean and improves results.""",
    subagents=[
        {
            "name": "research-agent",
            "description": "Conducts research",
            "system_prompt": "You are a researcher.",
        },
    ],
)

# --- OpenAI ---
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="openai:gpt-5.5",
    system_prompt="""...your instructions...

    IMPORTANT: For complex tasks, delegate to your subagents using the task() tool.
    This keeps your context clean and improves results.""",
    subagents=[
        {
            "name": "research-agent",
            "description": "Conducts research",
            "system_prompt": "You are a researcher.",
        },
    ],
)

# --- Anthropic ---
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="""...your instructions...

    IMPORTANT: For complex tasks, delegate to your subagents using the task() tool.
    This keeps your context clean and improves results.""",
    subagents=[
        {
            "name": "research-agent",
            "description": "Conducts research",
            "system_prompt": "You are a researcher.",
        },
    ],
)

# --- OpenRouter ---
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="openrouter:z-ai/glm-5.2",
    system_prompt="""...your instructions...

    IMPORTANT: For complex tasks, delegate to your subagents using the task() tool.
    This keeps your context clean and improves results.""",
    subagents=[
        {
            "name": "research-agent",
            "description": "Conducts research",
            "system_prompt": "You are a researcher.",
        },
    ],
)

# --- Fireworks ---
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="fireworks:accounts/fireworks/models/glm-5p2",
    system_prompt="""...your instructions...

    IMPORTANT: For complex tasks, delegate to your subagents using the task() tool.
    This keeps your context clean and improves results.""",
    subagents=[
        {
            "name": "research-agent",
            "description": "Conducts research",
            "system_prompt": "You are a researcher.",
        },
    ],
)

# --- Baseten ---
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="baseten:zai-org/GLM-5.2",
    system_prompt="""...your instructions...

    IMPORTANT: For complex tasks, delegate to your subagents using the task() tool.
    This keeps your context clean and improves results.""",
    subagents=[
        {
            "name": "research-agent",
            "description": "Conducts research",
            "system_prompt": "You are a researcher.",
        },
    ],
)

# --- Ollama ---
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="ollama:north-mini-code-1.0",
    system_prompt="""...your instructions...

    IMPORTANT: For complex tasks, delegate to your subagents using the task() tool.
    This keeps your context clean and improves results.""",
    subagents=[
        {
            "name": "research-agent",
            "description": "Conducts research",
            "system_prompt": "You are a researcher.",
        },
    ],
)
