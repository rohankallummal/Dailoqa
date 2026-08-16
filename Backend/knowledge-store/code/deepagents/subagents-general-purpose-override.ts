// --- Google ---
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import { z } from "zod";

const internetSearch = tool(
  async ({ query }: { query: string }) => `search results for ${query}`,
  {
    name: "internet_search",
    description: "Run a web search",
    schema: z.object({ query: z.string() }),
  },
);

// Main agent uses Gemini; general-purpose subagent uses GPT
const agent = await createDeepAgent({
  model: "google-genai:gemini-3.6-flash",
  tools: [internetSearch],
  subagents: [
    {
      name: "general-purpose",
      description: "General-purpose agent for research and multi-step tasks",
      systemPrompt: "You are a general-purpose assistant.",
      tools: [internetSearch],
      model: "openai:gpt-5.5", // Different model for delegated tasks
    },
  ],
});

// --- OpenAI ---
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import { z } from "zod";

const internetSearch = tool(
  async ({ query }: { query: string }) => `search results for ${query}`,
  {
    name: "internet_search",
    description: "Run a web search",
    schema: z.object({ query: z.string() }),
  },
);

// Main agent uses Gemini; general-purpose subagent uses GPT
const agent = await createDeepAgent({
  model: "openai:gpt-5.5",
  tools: [internetSearch],
  subagents: [
    {
      name: "general-purpose",
      description: "General-purpose agent for research and multi-step tasks",
      systemPrompt: "You are a general-purpose assistant.",
      tools: [internetSearch],
      model: "openai:gpt-5.5", // Different model for delegated tasks
    },
  ],
});

// --- Anthropic ---
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import { z } from "zod";

const internetSearch = tool(
  async ({ query }: { query: string }) => `search results for ${query}`,
  {
    name: "internet_search",
    description: "Run a web search",
    schema: z.object({ query: z.string() }),
  },
);

// Main agent uses Gemini; general-purpose subagent uses GPT
const agent = await createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [internetSearch],
  subagents: [
    {
      name: "general-purpose",
      description: "General-purpose agent for research and multi-step tasks",
      systemPrompt: "You are a general-purpose assistant.",
      tools: [internetSearch],
      model: "openai:gpt-5.5", // Different model for delegated tasks
    },
  ],
});

// --- OpenRouter ---
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import { z } from "zod";

const internetSearch = tool(
  async ({ query }: { query: string }) => `search results for ${query}`,
  {
    name: "internet_search",
    description: "Run a web search",
    schema: z.object({ query: z.string() }),
  },
);

// Main agent uses Gemini; general-purpose subagent uses GPT
const agent = await createDeepAgent({
  model: "openrouter:openrouter:z-ai/glm-5.2",
  tools: [internetSearch],
  subagents: [
    {
      name: "general-purpose",
      description: "General-purpose agent for research and multi-step tasks",
      systemPrompt: "You are a general-purpose assistant.",
      tools: [internetSearch],
      model: "openai:gpt-5.5", // Different model for delegated tasks
    },
  ],
});

// --- Fireworks ---
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import { z } from "zod";

const internetSearch = tool(
  async ({ query }: { query: string }) => `search results for ${query}`,
  {
    name: "internet_search",
    description: "Run a web search",
    schema: z.object({ query: z.string() }),
  },
);

// Main agent uses Gemini; general-purpose subagent uses GPT
const agent = await createDeepAgent({
  model: "fireworks:accounts/fireworks/models/glm-5p2",
  tools: [internetSearch],
  subagents: [
    {
      name: "general-purpose",
      description: "General-purpose agent for research and multi-step tasks",
      systemPrompt: "You are a general-purpose assistant.",
      tools: [internetSearch],
      model: "openai:gpt-5.5", // Different model for delegated tasks
    },
  ],
});

// --- Baseten ---
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import { z } from "zod";

const internetSearch = tool(
  async ({ query }: { query: string }) => `search results for ${query}`,
  {
    name: "internet_search",
    description: "Run a web search",
    schema: z.object({ query: z.string() }),
  },
);

// Main agent uses Gemini; general-purpose subagent uses GPT
const agent = await createDeepAgent({
  model: "baseten:zai-org/GLM-5.2",
  tools: [internetSearch],
  subagents: [
    {
      name: "general-purpose",
      description: "General-purpose agent for research and multi-step tasks",
      systemPrompt: "You are a general-purpose assistant.",
      tools: [internetSearch],
      model: "openai:gpt-5.5", // Different model for delegated tasks
    },
  ],
});

// --- Ollama ---
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import { z } from "zod";

const internetSearch = tool(
  async ({ query }: { query: string }) => `search results for ${query}`,
  {
    name: "internet_search",
    description: "Run a web search",
    schema: z.object({ query: z.string() }),
  },
);

// Main agent uses Gemini; general-purpose subagent uses GPT
const agent = await createDeepAgent({
  model: "ollama:north-mini-code-1.0",
  tools: [internetSearch],
  subagents: [
    {
      name: "general-purpose",
      description: "General-purpose agent for research and multi-step tasks",
      systemPrompt: "You are a general-purpose assistant.",
      tools: [internetSearch],
      model: "openai:gpt-5.5", // Different model for delegated tasks
    },
  ],
});
