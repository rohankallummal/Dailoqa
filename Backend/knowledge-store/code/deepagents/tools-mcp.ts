// --- Google ---
import { createDeepAgent } from "deepagents";

const { MultiServerMCPClient } = await import("@langchain/mcp-adapters");

const client = new MultiServerMCPClient({
  my_server: {
    transport: "http",
    url: "http://localhost:8000/mcp",
  },
});

const tools = await client.getTools();

const agent = await createDeepAgent({
  model: "google-genai:gemini-3.6-flash",
  tools,
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "Use the MCP server to help me." }],
});

// --- OpenAI ---
import { createDeepAgent } from "deepagents";

const { MultiServerMCPClient } = await import("@langchain/mcp-adapters");

const client = new MultiServerMCPClient({
  my_server: {
    transport: "http",
    url: "http://localhost:8000/mcp",
  },
});

const tools = await client.getTools();

const agent = await createDeepAgent({
  model: "openai:gpt-5.5",
  tools,
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "Use the MCP server to help me." }],
});

// --- Anthropic ---
import { createDeepAgent } from "deepagents";

const { MultiServerMCPClient } = await import("@langchain/mcp-adapters");

const client = new MultiServerMCPClient({
  my_server: {
    transport: "http",
    url: "http://localhost:8000/mcp",
  },
});

const tools = await client.getTools();

const agent = await createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools,
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "Use the MCP server to help me." }],
});

// --- OpenRouter ---
import { createDeepAgent } from "deepagents";

const { MultiServerMCPClient } = await import("@langchain/mcp-adapters");

const client = new MultiServerMCPClient({
  my_server: {
    transport: "http",
    url: "http://localhost:8000/mcp",
  },
});

const tools = await client.getTools();

const agent = await createDeepAgent({
  model: "openrouter:openrouter:z-ai/glm-5.2",
  tools,
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "Use the MCP server to help me." }],
});

// --- Fireworks ---
import { createDeepAgent } from "deepagents";

const { MultiServerMCPClient } = await import("@langchain/mcp-adapters");

const client = new MultiServerMCPClient({
  my_server: {
    transport: "http",
    url: "http://localhost:8000/mcp",
  },
});

const tools = await client.getTools();

const agent = await createDeepAgent({
  model: "fireworks:accounts/fireworks/models/glm-5p2",
  tools,
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "Use the MCP server to help me." }],
});

// --- Baseten ---
import { createDeepAgent } from "deepagents";

const { MultiServerMCPClient } = await import("@langchain/mcp-adapters");

const client = new MultiServerMCPClient({
  my_server: {
    transport: "http",
    url: "http://localhost:8000/mcp",
  },
});

const tools = await client.getTools();

const agent = await createDeepAgent({
  model: "baseten:zai-org/GLM-5.2",
  tools,
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "Use the MCP server to help me." }],
});

// --- Ollama ---
import { createDeepAgent } from "deepagents";

const { MultiServerMCPClient } = await import("@langchain/mcp-adapters");

const client = new MultiServerMCPClient({
  my_server: {
    transport: "http",
    url: "http://localhost:8000/mcp",
  },
});

const tools = await client.getTools();

const agent = await createDeepAgent({
  model: "ollama:north-mini-code-1.0",
  tools,
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "Use the MCP server to help me." }],
});
