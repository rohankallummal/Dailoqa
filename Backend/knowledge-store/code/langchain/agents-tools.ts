// --- Google ---
import { tool } from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Results for: ${query}`, {
  name: "search",
  description: "Search for information",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({ model: "google-genai:gemini-3.6-flash", tools: [search] });

// --- OpenAI ---
import { tool } from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Results for: ${query}`, {
  name: "search",
  description: "Search for information",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({ model: "openai:gpt-5.5", tools: [search] });

// --- Anthropic ---
import { tool } from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Results for: ${query}`, {
  name: "search",
  description: "Search for information",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({ model: "anthropic:claude-sonnet-4-6", tools: [search] });

// --- OpenRouter ---
import { tool } from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Results for: ${query}`, {
  name: "search",
  description: "Search for information",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({ model: "openrouter:openrouter:z-ai/glm-5.2", tools: [search] });

// --- Fireworks ---
import { tool } from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Results for: ${query}`, {
  name: "search",
  description: "Search for information",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({ model: "fireworks:accounts/fireworks/models/glm-5p2", tools: [search] });

// --- Baseten ---
import { tool } from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Results for: ${query}`, {
  name: "search",
  description: "Search for information",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({ model: "baseten:zai-org/GLM-5.2", tools: [search] });

// --- Ollama ---
import { tool } from "langchain";
import * as z from "zod";

var search = tool(({ query }) => `Results for: ${query}`, {
  name: "search",
  description: "Search for information",
  schema: z.object({ query: z.string() }),
});

var agent = createAgent({ model: "ollama:north-mini-code-1.0", tools: [search] });
