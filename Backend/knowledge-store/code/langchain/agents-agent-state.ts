// --- Google ---
import { createAgent, createMiddleware } from "langchain";
import { StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const MyState = new StateSchema({
  userId: z.string(),
  callCount: z.number().default(0),
});

const stateMiddleware = createMiddleware({
  name: "StateExtension",
  stateSchema: MyState, // [!code highlight]
});

const agent = createAgent({
  model: "google-genai:gemini-3.5-flash",
  tools: [],
  middleware: [stateMiddleware],
});

// --- OpenAI ---
import { createAgent, createMiddleware } from "langchain";
import { StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const MyState = new StateSchema({
  userId: z.string(),
  callCount: z.number().default(0),
});

const stateMiddleware = createMiddleware({
  name: "StateExtension",
  stateSchema: MyState, // [!code highlight]
});

const agent = createAgent({
  model: "openai:gpt-5.5",
  tools: [],
  middleware: [stateMiddleware],
});

// --- Anthropic ---
import { createAgent, createMiddleware } from "langchain";
import { StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const MyState = new StateSchema({
  userId: z.string(),
  callCount: z.number().default(0),
});

const stateMiddleware = createMiddleware({
  name: "StateExtension",
  stateSchema: MyState, // [!code highlight]
});

const agent = createAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [],
  middleware: [stateMiddleware],
});

// --- OpenRouter ---
import { createAgent, createMiddleware } from "langchain";
import { StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const MyState = new StateSchema({
  userId: z.string(),
  callCount: z.number().default(0),
});

const stateMiddleware = createMiddleware({
  name: "StateExtension",
  stateSchema: MyState, // [!code highlight]
});

const agent = createAgent({
  model: "openrouter:openrouter:z-ai/glm-5.2",
  tools: [],
  middleware: [stateMiddleware],
});

// --- Fireworks ---
import { createAgent, createMiddleware } from "langchain";
import { StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const MyState = new StateSchema({
  userId: z.string(),
  callCount: z.number().default(0),
});

const stateMiddleware = createMiddleware({
  name: "StateExtension",
  stateSchema: MyState, // [!code highlight]
});

const agent = createAgent({
  model: "fireworks:accounts/fireworks/models/glm-5p2",
  tools: [],
  middleware: [stateMiddleware],
});

// --- Baseten ---
import { createAgent, createMiddleware } from "langchain";
import { StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const MyState = new StateSchema({
  userId: z.string(),
  callCount: z.number().default(0),
});

const stateMiddleware = createMiddleware({
  name: "StateExtension",
  stateSchema: MyState, // [!code highlight]
});

const agent = createAgent({
  model: "baseten:zai-org/GLM-5.2",
  tools: [],
  middleware: [stateMiddleware],
});

// --- Ollama ---
import { createAgent, createMiddleware } from "langchain";
import { StateSchema } from "@langchain/langgraph";
import * as z from "zod";

const MyState = new StateSchema({
  userId: z.string(),
  callCount: z.number().default(0),
});

const stateMiddleware = createMiddleware({
  name: "StateExtension",
  stateSchema: MyState, // [!code highlight]
});

const agent = createAgent({
  model: "ollama:north-mini-code-1.0",
  tools: [],
  middleware: [stateMiddleware],
});
