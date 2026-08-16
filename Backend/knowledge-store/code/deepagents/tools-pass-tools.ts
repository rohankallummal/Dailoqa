// --- Google ---
import { createDeepAgent } from "deepagents";


const agent = await createDeepAgent({
  model: "google-genai:gemini-3.6-flash",
  tools: [search, fetchUrl, runQuery],
});

// --- OpenAI ---
import { createDeepAgent } from "deepagents";


const agent = await createDeepAgent({
  model: "openai:gpt-5.5",
  tools: [search, fetchUrl, runQuery],
});

// --- Anthropic ---
import { createDeepAgent } from "deepagents";


const agent = await createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [search, fetchUrl, runQuery],
});

// --- OpenRouter ---
import { createDeepAgent } from "deepagents";


const agent = await createDeepAgent({
  model: "openrouter:openrouter:z-ai/glm-5.2",
  tools: [search, fetchUrl, runQuery],
});

// --- Fireworks ---
import { createDeepAgent } from "deepagents";


const agent = await createDeepAgent({
  model: "fireworks:accounts/fireworks/models/glm-5p2",
  tools: [search, fetchUrl, runQuery],
});

// --- Baseten ---
import { createDeepAgent } from "deepagents";


const agent = await createDeepAgent({
  model: "baseten:zai-org/GLM-5.2",
  tools: [search, fetchUrl, runQuery],
});

// --- Ollama ---
import { createDeepAgent } from "deepagents";


const agent = await createDeepAgent({
  model: "ollama:north-mini-code-1.0",
  tools: [search, fetchUrl, runQuery],
});
