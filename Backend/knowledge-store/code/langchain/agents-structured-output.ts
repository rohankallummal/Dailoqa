// --- Google ---
const Answer = z.object({ summary: z.string(), confidence: z.number() });

var agent = createAgent({
  model: "google-genai:gemini-3.6-flash",
  tools,
  responseFormat: Answer,
});
const result = await agent.invoke({
  messages: [{ role: "user", content: "Summarize AI trends" }],
});
result.structuredResponse; // { summary: ..., confidence: ... }

// --- OpenAI ---
const Answer = z.object({ summary: z.string(), confidence: z.number() });

var agent = createAgent({
  model: "openai:gpt-5.5",
  tools,
  responseFormat: Answer,
});
const result = await agent.invoke({
  messages: [{ role: "user", content: "Summarize AI trends" }],
});
result.structuredResponse; // { summary: ..., confidence: ... }

// --- Anthropic ---
const Answer = z.object({ summary: z.string(), confidence: z.number() });

var agent = createAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools,
  responseFormat: Answer,
});
const result = await agent.invoke({
  messages: [{ role: "user", content: "Summarize AI trends" }],
});
result.structuredResponse; // { summary: ..., confidence: ... }

// --- OpenRouter ---
const Answer = z.object({ summary: z.string(), confidence: z.number() });

var agent = createAgent({
  model: "openrouter:openrouter:z-ai/glm-5.2",
  tools,
  responseFormat: Answer,
});
const result = await agent.invoke({
  messages: [{ role: "user", content: "Summarize AI trends" }],
});
result.structuredResponse; // { summary: ..., confidence: ... }

// --- Fireworks ---
const Answer = z.object({ summary: z.string(), confidence: z.number() });

var agent = createAgent({
  model: "fireworks:accounts/fireworks/models/glm-5p2",
  tools,
  responseFormat: Answer,
});
const result = await agent.invoke({
  messages: [{ role: "user", content: "Summarize AI trends" }],
});
result.structuredResponse; // { summary: ..., confidence: ... }

// --- Baseten ---
const Answer = z.object({ summary: z.string(), confidence: z.number() });

var agent = createAgent({
  model: "baseten:zai-org/GLM-5.2",
  tools,
  responseFormat: Answer,
});
const result = await agent.invoke({
  messages: [{ role: "user", content: "Summarize AI trends" }],
});
result.structuredResponse; // { summary: ..., confidence: ... }

// --- Ollama ---
const Answer = z.object({ summary: z.string(), confidence: z.number() });

var agent = createAgent({
  model: "ollama:north-mini-code-1.0",
  tools,
  responseFormat: Answer,
});
const result = await agent.invoke({
  messages: [{ role: "user", content: "Summarize AI trends" }],
});
result.structuredResponse; // { summary: ..., confidence: ... }
