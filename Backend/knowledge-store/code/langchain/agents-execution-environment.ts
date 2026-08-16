// --- Google ---
import { createAgent } from "langchain";
import { createFilesystemMiddleware, StateBackend } from "deepagents";

var agent = createAgent({
  model: "google-genai:gemini-3.6-flash",
  tools: [search],
  middleware: [createFilesystemMiddleware({ backend: new StateBackend() })],
});

// --- OpenAI ---
import { createAgent } from "langchain";
import { createFilesystemMiddleware, StateBackend } from "deepagents";

var agent = createAgent({
  model: "openai:gpt-5.5",
  tools: [search],
  middleware: [createFilesystemMiddleware({ backend: new StateBackend() })],
});

// --- Anthropic ---
import { createAgent } from "langchain";
import { createFilesystemMiddleware, StateBackend } from "deepagents";

var agent = createAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [search],
  middleware: [createFilesystemMiddleware({ backend: new StateBackend() })],
});

// --- OpenRouter ---
import { createAgent } from "langchain";
import { createFilesystemMiddleware, StateBackend } from "deepagents";

var agent = createAgent({
  model: "openrouter:openrouter:z-ai/glm-5.2",
  tools: [search],
  middleware: [createFilesystemMiddleware({ backend: new StateBackend() })],
});

// --- Fireworks ---
import { createAgent } from "langchain";
import { createFilesystemMiddleware, StateBackend } from "deepagents";

var agent = createAgent({
  model: "fireworks:accounts/fireworks/models/glm-5p2",
  tools: [search],
  middleware: [createFilesystemMiddleware({ backend: new StateBackend() })],
});

// --- Baseten ---
import { createAgent } from "langchain";
import { createFilesystemMiddleware, StateBackend } from "deepagents";

var agent = createAgent({
  model: "baseten:zai-org/GLM-5.2",
  tools: [search],
  middleware: [createFilesystemMiddleware({ backend: new StateBackend() })],
});

// --- Ollama ---
import { createAgent } from "langchain";
import { createFilesystemMiddleware, StateBackend } from "deepagents";

var agent = createAgent({
  model: "ollama:north-mini-code-1.0",
  tools: [search],
  middleware: [createFilesystemMiddleware({ backend: new StateBackend() })],
});
