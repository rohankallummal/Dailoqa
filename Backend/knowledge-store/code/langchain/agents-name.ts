// --- Google ---
var agent = createAgent({
  model: "google-genai:gemini-3.6-flash",
  tools,
  name: "research_assistant",
});

// --- OpenAI ---
var agent = createAgent({
  model: "openai:gpt-5.5",
  tools,
  name: "research_assistant",
});

// --- Anthropic ---
var agent = createAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools,
  name: "research_assistant",
});

// --- OpenRouter ---
var agent = createAgent({
  model: "openrouter:openrouter:z-ai/glm-5.2",
  tools,
  name: "research_assistant",
});

// --- Fireworks ---
var agent = createAgent({
  model: "fireworks:accounts/fireworks/models/glm-5p2",
  tools,
  name: "research_assistant",
});

// --- Baseten ---
var agent = createAgent({
  model: "baseten:zai-org/GLM-5.2",
  tools,
  name: "research_assistant",
});

// --- Ollama ---
var agent = createAgent({
  model: "ollama:north-mini-code-1.0",
  tools,
  name: "research_assistant",
});
