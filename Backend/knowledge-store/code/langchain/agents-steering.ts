// --- Google ---
import { createAgent, humanInTheLoopMiddleware, tool } from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({
  model: "google-genai:gemini-3.6-flash",
  tools: [search],
  middleware: [humanInTheLoopMiddleware({ interruptOn: { writeFile: true } })],
});

// --- OpenAI ---
import { createAgent, humanInTheLoopMiddleware, tool } from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({
  model: "openai:gpt-5.5",
  tools: [search],
  middleware: [humanInTheLoopMiddleware({ interruptOn: { writeFile: true } })],
});

// --- Anthropic ---
import { createAgent, humanInTheLoopMiddleware, tool } from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [search],
  middleware: [humanInTheLoopMiddleware({ interruptOn: { writeFile: true } })],
});

// --- OpenRouter ---
import { createAgent, humanInTheLoopMiddleware, tool } from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({
  model: "openrouter:openrouter:z-ai/glm-5.2",
  tools: [search],
  middleware: [humanInTheLoopMiddleware({ interruptOn: { writeFile: true } })],
});

// --- Fireworks ---
import { createAgent, humanInTheLoopMiddleware, tool } from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({
  model: "fireworks:accounts/fireworks/models/glm-5p2",
  tools: [search],
  middleware: [humanInTheLoopMiddleware({ interruptOn: { writeFile: true } })],
});

// --- Baseten ---
import { createAgent, humanInTheLoopMiddleware, tool } from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({
  model: "baseten:zai-org/GLM-5.2",
  tools: [search],
  middleware: [humanInTheLoopMiddleware({ interruptOn: { writeFile: true } })],
});

// --- Ollama ---
import { createAgent, humanInTheLoopMiddleware, tool } from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Search results for: ${query}`, {
  name: "search",
  description: "Search for a query and return a short summary.",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({
  model: "ollama:north-mini-code-1.0",
  tools: [search],
  middleware: [humanInTheLoopMiddleware({ interruptOn: { writeFile: true } })],
});
