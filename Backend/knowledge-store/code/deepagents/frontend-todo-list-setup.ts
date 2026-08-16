// --- Google ---
import { createDeepAgent } from "deepagents";
import { todoListMiddleware } from "langchain";

const agent = await createDeepAgent({
  model: "google-genai:gemini-3.6-flash",
  middleware: [todoListMiddleware()],
});

// --- OpenAI ---
import { createDeepAgent } from "deepagents";
import { todoListMiddleware } from "langchain";

const agent = await createDeepAgent({
  model: "openai:gpt-5.5",
  middleware: [todoListMiddleware()],
});

// --- Anthropic ---
import { createDeepAgent } from "deepagents";
import { todoListMiddleware } from "langchain";

const agent = await createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  middleware: [todoListMiddleware()],
});

// --- OpenRouter ---
import { createDeepAgent } from "deepagents";
import { todoListMiddleware } from "langchain";

const agent = await createDeepAgent({
  model: "openrouter:openrouter:z-ai/glm-5.2",
  middleware: [todoListMiddleware()],
});

// --- Fireworks ---
import { createDeepAgent } from "deepagents";
import { todoListMiddleware } from "langchain";

const agent = await createDeepAgent({
  model: "fireworks:accounts/fireworks/models/glm-5p2",
  middleware: [todoListMiddleware()],
});

// --- Baseten ---
import { createDeepAgent } from "deepagents";
import { todoListMiddleware } from "langchain";

const agent = await createDeepAgent({
  model: "baseten:zai-org/GLM-5.2",
  middleware: [todoListMiddleware()],
});

// --- Ollama ---
import { createDeepAgent } from "deepagents";
import { todoListMiddleware } from "langchain";

const agent = await createDeepAgent({
  model: "ollama:north-mini-code-1.0",
  middleware: [todoListMiddleware()],
});
