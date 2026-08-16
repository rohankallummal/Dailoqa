// --- Google ---
import {
  createAgent,
  modelRetryMiddleware,
  tool,
  toolRetryMiddleware,
} from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({
  model: "google-genai:gemini-3.6-flash",
  tools: [search],
  middleware: [
    modelRetryMiddleware({ maxRetries: 3 }),
    toolRetryMiddleware({ maxRetries: 2 }),
  ],
});

// --- OpenAI ---
import {
  createAgent,
  modelRetryMiddleware,
  tool,
  toolRetryMiddleware,
} from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({
  model: "openai:gpt-5.5",
  tools: [search],
  middleware: [
    modelRetryMiddleware({ maxRetries: 3 }),
    toolRetryMiddleware({ maxRetries: 2 }),
  ],
});

// --- Anthropic ---
import {
  createAgent,
  modelRetryMiddleware,
  tool,
  toolRetryMiddleware,
} from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [search],
  middleware: [
    modelRetryMiddleware({ maxRetries: 3 }),
    toolRetryMiddleware({ maxRetries: 2 }),
  ],
});

// --- OpenRouter ---
import {
  createAgent,
  modelRetryMiddleware,
  tool,
  toolRetryMiddleware,
} from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({
  model: "openrouter:openrouter:z-ai/glm-5.2",
  tools: [search],
  middleware: [
    modelRetryMiddleware({ maxRetries: 3 }),
    toolRetryMiddleware({ maxRetries: 2 }),
  ],
});

// --- Fireworks ---
import {
  createAgent,
  modelRetryMiddleware,
  tool,
  toolRetryMiddleware,
} from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({
  model: "fireworks:accounts/fireworks/models/glm-5p2",
  tools: [search],
  middleware: [
    modelRetryMiddleware({ maxRetries: 3 }),
    toolRetryMiddleware({ maxRetries: 2 }),
  ],
});

// --- Baseten ---
import {
  createAgent,
  modelRetryMiddleware,
  tool,
  toolRetryMiddleware,
} from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({
  model: "baseten:zai-org/GLM-5.2",
  tools: [search],
  middleware: [
    modelRetryMiddleware({ maxRetries: 3 }),
    toolRetryMiddleware({ maxRetries: 2 }),
  ],
});

// --- Ollama ---
import {
  createAgent,
  modelRetryMiddleware,
  tool,
  toolRetryMiddleware,
} from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({
  model: "ollama:north-mini-code-1.0",
  tools: [search],
  middleware: [
    modelRetryMiddleware({ maxRetries: 3 }),
    toolRetryMiddleware({ maxRetries: 2 }),
  ],
});
