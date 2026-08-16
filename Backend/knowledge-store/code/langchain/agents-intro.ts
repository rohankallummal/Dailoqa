// --- Google ---
import { createAgent } from "langchain";

var agent = createAgent({ model: "google-genai:gemini-3.6-flash", tools });

// --- OpenAI ---
import { createAgent } from "langchain";

var agent = createAgent({ model: "openai:gpt-5.5", tools });

// --- Anthropic ---
import { createAgent } from "langchain";

var agent = createAgent({ model: "anthropic:claude-sonnet-4-6", tools });

// --- OpenRouter ---
import { createAgent } from "langchain";

var agent = createAgent({ model: "openrouter:openrouter:z-ai/glm-5.2", tools });

// --- Fireworks ---
import { createAgent } from "langchain";

var agent = createAgent({ model: "fireworks:accounts/fireworks/models/glm-5p2", tools });

// --- Baseten ---
import { createAgent } from "langchain";

var agent = createAgent({ model: "baseten:zai-org/GLM-5.2", tools });

// --- Ollama ---
import { createAgent } from "langchain";

var agent = createAgent({ model: "ollama:north-mini-code-1.0", tools });
