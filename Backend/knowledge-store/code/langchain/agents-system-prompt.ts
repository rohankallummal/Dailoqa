// --- Google ---
var agent = createAgent({
  model: "google-genai:gemini-3.6-flash",
  tools,
  systemPrompt: "You are a helpful assistant. Be concise and accurate.",
});

// --- OpenAI ---
var agent = createAgent({
  model: "openai:gpt-5.5",
  tools,
  systemPrompt: "You are a helpful assistant. Be concise and accurate.",
});

// --- Anthropic ---
var agent = createAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools,
  systemPrompt: "You are a helpful assistant. Be concise and accurate.",
});

// --- OpenRouter ---
var agent = createAgent({
  model: "openrouter:openrouter:z-ai/glm-5.2",
  tools,
  systemPrompt: "You are a helpful assistant. Be concise and accurate.",
});

// --- Fireworks ---
var agent = createAgent({
  model: "fireworks:accounts/fireworks/models/glm-5p2",
  tools,
  systemPrompt: "You are a helpful assistant. Be concise and accurate.",
});

// --- Baseten ---
var agent = createAgent({
  model: "baseten:zai-org/GLM-5.2",
  tools,
  systemPrompt: "You are a helpful assistant. Be concise and accurate.",
});

// --- Ollama ---
var agent = createAgent({
  model: "ollama:north-mini-code-1.0",
  tools,
  systemPrompt: "You are a helpful assistant. Be concise and accurate.",
});
