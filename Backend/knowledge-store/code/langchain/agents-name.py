# --- Google ---
agent = create_agent(model="google_genai:gemini-3.6-flash", tools=tools, name="research_assistant")

# --- OpenAI ---
agent = create_agent(model="openai:gpt-5.5", tools=tools, name="research_assistant")

# --- Anthropic ---
agent = create_agent(model="anthropic:claude-sonnet-4-6", tools=tools, name="research_assistant")

# --- OpenRouter ---
agent = create_agent(model="openrouter:z-ai/glm-5.2", tools=tools, name="research_assistant")

# --- Fireworks ---
agent = create_agent(model="fireworks:accounts/fireworks/models/glm-5p2", tools=tools, name="research_assistant")

# --- Baseten ---
agent = create_agent(model="baseten:zai-org/GLM-5.2", tools=tools, name="research_assistant")

# --- Ollama ---
agent = create_agent(model="ollama:north-mini-code-1.0", tools=tools, name="research_assistant")
