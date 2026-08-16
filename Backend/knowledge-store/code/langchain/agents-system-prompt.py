# --- Google ---
agent = create_agent(
    model="google_genai:gemini-3.6-flash",
    tools=tools,
    system_prompt="You are a helpful assistant. Be concise and accurate.",
)

# --- OpenAI ---
agent = create_agent(
    model="openai:gpt-5.5",
    tools=tools,
    system_prompt="You are a helpful assistant. Be concise and accurate.",
)

# --- Anthropic ---
agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=tools,
    system_prompt="You are a helpful assistant. Be concise and accurate.",
)

# --- OpenRouter ---
agent = create_agent(
    model="openrouter:z-ai/glm-5.2",
    tools=tools,
    system_prompt="You are a helpful assistant. Be concise and accurate.",
)

# --- Fireworks ---
agent = create_agent(
    model="fireworks:accounts/fireworks/models/glm-5p2",
    tools=tools,
    system_prompt="You are a helpful assistant. Be concise and accurate.",
)

# --- Baseten ---
agent = create_agent(
    model="baseten:zai-org/GLM-5.2",
    tools=tools,
    system_prompt="You are a helpful assistant. Be concise and accurate.",
)

# --- Ollama ---
agent = create_agent(
    model="ollama:north-mini-code-1.0",
    tools=tools,
    system_prompt="You are a helpful assistant. Be concise and accurate.",
)
