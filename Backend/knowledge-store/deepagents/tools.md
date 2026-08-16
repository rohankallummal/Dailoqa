---
type: Documentation Page
title: Tools
description: Connect Deep Agents to custom functions, APIs, databases, and any MCP server
product: deepagents
resource: /docs/deepagents/tools
source: /oss/deepagents/tools
tags:
  - deepagents
  - tools
timestamp: 2026-08-11T15:35:33Z
code_examples:
  - ../code/deepagents/tools-pass-tools.py
  - ../code/deepagents/tools-pass-tools.ts
  - ../code/deepagents/customization-tools.py
  - ../code/deepagents/customization-tools.ts
  - ../code/deepagents/tools-mcp.py
  - ../code/deepagents/tools-mcp.ts
---

# Tools

Deep Agents can call any tool you define, any LangChain tool, and tools from any [MCP server](#mcp-tools).
Pass them to `create_deep_agent` via the `tools=` parameter alongside the [built-in harness tools](../deepagents/overview.md#execution-environment) for file management and subagent spawning.

**Python**

Code example: [`code/deepagents/tools-pass-tools.py`](../code/deepagents/tools-pass-tools.py)

```python Google
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    tools=[search, fetch_url, run_query],
)
```

```python OpenAI
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[search, fetch_url, run_query],
)
```

```python Anthropic
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[search, fetch_url, run_query],
)
```

```python OpenRouter
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="openrouter:z-ai/glm-5.2",
    tools=[search, fetch_url, run_query],
)
```

```python Fireworks
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="fireworks:accounts/fireworks/models/glm-5p2",
    tools=[search, fetch_url, run_query],
)
```

```python Baseten
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="baseten:zai-org/GLM-5.2",
    tools=[search, fetch_url, run_query],
)
```

```python Ollama
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="ollama:north-mini-code-1.0",
    tools=[search, fetch_url, run_query],
)
```

**JavaScript / TypeScript**

Code example: [`code/deepagents/tools-pass-tools.ts`](../code/deepagents/tools-pass-tools.ts)

```ts Google
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent({
  model: "google-genai:gemini-3.6-flash",
  tools: [search, fetchUrl, runQuery],
});
```

```ts OpenAI
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent({
  model: "openai:gpt-5.5",
  tools: [search, fetchUrl, runQuery],
});
```

```ts Anthropic
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [search, fetchUrl, runQuery],
});
```

```ts OpenRouter
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent({
  model: "openrouter:openrouter:z-ai/glm-5.2",
  tools: [search, fetchUrl, runQuery],
});
```

```ts Fireworks
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent({
  model: "fireworks:accounts/fireworks/models/glm-5p2",
  tools: [search, fetchUrl, runQuery],
});
```

```ts Baseten
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent({
  model: "baseten:zai-org/GLM-5.2",
  tools: [search, fetchUrl, runQuery],
});
```

```ts Ollama
import { createDeepAgent } from "deepagents";

const agent = await createDeepAgent({
  model: "ollama:north-mini-code-1.0",
  tools: [search, fetchUrl, runQuery],
});
```

## Custom tools

Pass any callable, such as plain functions, LangChain `@tool`-decorated functions, or tool dicts—directly to `tools=`.
Deep Agents infers the tool schema from the function signature and docstring, so you don't need to define a separate schema in most cases.

**Python**
Code example: [`code/deepagents/customization-tools.py`](../code/deepagents/customization-tools.py)

```python Google
import os
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )

agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    tools=[internet_search],
)
```

```python OpenAI
import os
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )

agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[internet_search],
)
```

```python Anthropic
import os
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[internet_search],
)
```

```python OpenRouter
import os
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )

agent = create_deep_agent(
    model="openrouter:z-ai/glm-5.2",
    tools=[internet_search],
)
```

```python Fireworks
import os
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )

agent = create_deep_agent(
    model="fireworks:accounts/fireworks/models/glm-5p2",
    tools=[internet_search],
)
```

```python Baseten
import os
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )

agent = create_deep_agent(
    model="baseten:zai-org/GLM-5.2",
    tools=[internet_search],
)
```

```python Ollama
import os
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )

agent = create_deep_agent(
    model="ollama:north-mini-code-1.0",
    tools=[internet_search],
)
```

**JavaScript / TypeScript**
Code example: [`code/deepagents/customization-tools.ts`](../code/deepagents/customization-tools.ts)

```ts Google
import { tool } from "langchain";
import { TavilySearch } from "@langchain/tavily";
import { createDeepAgent } from "deepagents";
import { z } from "zod";

const internetSearch = tool(
  async ({
    query,
    maxResults = 5,
    topic = "general",
    includeRawContent = false,
  }: {
    query: string;
    maxResults?: number;
    topic?: "general" | "news" | "finance";
    includeRawContent?: boolean;
  }) => {
    const tavilySearch = new TavilySearch({
      maxResults,
      tavilyApiKey: process.env.TAVILY_API_KEY,
      includeRawContent,
      topic,
    });
    return await tavilySearch._call({ query });
  },
  {
    name: "internet_search",
    description: "Run a web search",
    schema: z.object({
      query: z.string().describe("The search query"),
      maxResults: z.number().optional().default(5),
      topic: z
        .enum(["general", "news", "finance"])
        .optional()
        .default("general"),
      includeRawContent: z.boolean().optional().default(false),
    }),
  },
);

const agent = createDeepAgent({
  model: "google-genai:gemini-3.6-flash",
  tools: [internetSearch],
});
```

```ts OpenAI
import { tool } from "langchain";
import { TavilySearch } from "@langchain/tavily";
import { createDeepAgent } from "deepagents";
import { z } from "zod";

const internetSearch = tool(
  async ({
    query,
    maxResults = 5,
    topic = "general",
    includeRawContent = false,
  }: {
    query: string;
    maxResults?: number;
    topic?: "general" | "news" | "finance";
    includeRawContent?: boolean;
  }) => {
    const tavilySearch = new TavilySearch({
      maxResults,
      tavilyApiKey: process.env.TAVILY_API_KEY,
      includeRawContent,
      topic,
    });
    return await tavilySearch._call({ query });
  },
  {
    name: "internet_search",
    description: "Run a web search",
    schema: z.object({
      query: z.string().describe("The search query"),
      maxResults: z.number().optional().default(5),
      topic: z
        .enum(["general", "news", "finance"])
        .optional()
        .default("general"),
      includeRawContent: z.boolean().optional().default(false),
    }),
  },
);

const agent = createDeepAgent({
  model: "openai:gpt-5.5",
  tools: [internetSearch],
});
```

```ts Anthropic
import { tool } from "langchain";
import { TavilySearch } from "@langchain/tavily";
import { createDeepAgent } from "deepagents";
import { z } from "zod";

const internetSearch = tool(
  async ({
    query,
    maxResults = 5,
    topic = "general",
    includeRawContent = false,
  }: {
    query: string;
    maxResults?: number;
    topic?: "general" | "news" | "finance";
    includeRawContent?: boolean;
  }) => {
    const tavilySearch = new TavilySearch({
      maxResults,
      tavilyApiKey: process.env.TAVILY_API_KEY,
      includeRawContent,
      topic,
    });
    return await tavilySearch._call({ query });
  },
  {
    name: "internet_search",
    description: "Run a web search",
    schema: z.object({
      query: z.string().describe("The search query"),
      maxResults: z.number().optional().default(5),
      topic: z
        .enum(["general", "news", "finance"])
        .optional()
        .default("general"),
      includeRawContent: z.boolean().optional().default(false),
    }),
  },
);

const agent = createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [internetSearch],
});
```

```ts OpenRouter
import { tool } from "langchain";
import { TavilySearch } from "@langchain/tavily";
import { createDeepAgent } from "deepagents";
import { z } from "zod";

const internetSearch = tool(
  async ({
    query,
    maxResults = 5,
    topic = "general",
    includeRawContent = false,
  }: {
    query: string;
    maxResults?: number;
    topic?: "general" | "news" | "finance";
    includeRawContent?: boolean;
  }) => {
    const tavilySearch = new TavilySearch({
      maxResults,
      tavilyApiKey: process.env.TAVILY_API_KEY,
      includeRawContent,
      topic,
    });
    return await tavilySearch._call({ query });
  },
  {
    name: "internet_search",
    description: "Run a web search",
    schema: z.object({
      query: z.string().describe("The search query"),
      maxResults: z.number().optional().default(5),
      topic: z
        .enum(["general", "news", "finance"])
        .optional()
        .default("general"),
      includeRawContent: z.boolean().optional().default(false),
    }),
  },
);

const agent = createDeepAgent({
  model: "openrouter:openrouter:z-ai/glm-5.2",
  tools: [internetSearch],
});
```

```ts Fireworks
import { tool } from "langchain";
import { TavilySearch } from "@langchain/tavily";
import { createDeepAgent } from "deepagents";
import { z } from "zod";

const internetSearch = tool(
  async ({
    query,
    maxResults = 5,
    topic = "general",
    includeRawContent = false,
  }: {
    query: string;
    maxResults?: number;
    topic?: "general" | "news" | "finance";
    includeRawContent?: boolean;
  }) => {
    const tavilySearch = new TavilySearch({
      maxResults,
      tavilyApiKey: process.env.TAVILY_API_KEY,
      includeRawContent,
      topic,
    });
    return await tavilySearch._call({ query });
  },
  {
    name: "internet_search",
    description: "Run a web search",
    schema: z.object({
      query: z.string().describe("The search query"),
      maxResults: z.number().optional().default(5),
      topic: z
        .enum(["general", "news", "finance"])
        .optional()
        .default("general"),
      includeRawContent: z.boolean().optional().default(false),
    }),
  },
);

const agent = createDeepAgent({
  model: "fireworks:accounts/fireworks/models/glm-5p2",
  tools: [internetSearch],
});
```

```ts Baseten
import { tool } from "langchain";
import { TavilySearch } from "@langchain/tavily";
import { createDeepAgent } from "deepagents";
import { z } from "zod";

const internetSearch = tool(
  async ({
    query,
    maxResults = 5,
    topic = "general",
    includeRawContent = false,
  }: {
    query: string;
    maxResults?: number;
    topic?: "general" | "news" | "finance";
    includeRawContent?: boolean;
  }) => {
    const tavilySearch = new TavilySearch({
      maxResults,
      tavilyApiKey: process.env.TAVILY_API_KEY,
      includeRawContent,
      topic,
    });
    return await tavilySearch._call({ query });
  },
  {
    name: "internet_search",
    description: "Run a web search",
    schema: z.object({
      query: z.string().describe("The search query"),
      maxResults: z.number().optional().default(5),
      topic: z
        .enum(["general", "news", "finance"])
        .optional()
        .default("general"),
      includeRawContent: z.boolean().optional().default(false),
    }),
  },
);

const agent = createDeepAgent({
  model: "baseten:zai-org/GLM-5.2",
  tools: [internetSearch],
});
```

```ts Ollama
import { tool } from "langchain";
import { TavilySearch } from "@langchain/tavily";
import { createDeepAgent } from "deepagents";
import { z } from "zod";

const internetSearch = tool(
  async ({
    query,
    maxResults = 5,
    topic = "general",
    includeRawContent = false,
  }: {
    query: string;
    maxResults?: number;
    topic?: "general" | "news" | "finance";
    includeRawContent?: boolean;
  }) => {
    const tavilySearch = new TavilySearch({
      maxResults,
      tavilyApiKey: process.env.TAVILY_API_KEY,
      includeRawContent,
      topic,
    });
    return await tavilySearch._call({ query });
  },
  {
    name: "internet_search",
    description: "Run a web search",
    schema: z.object({
      query: z.string().describe("The search query"),
      maxResults: z.number().optional().default(5),
      topic: z
        .enum(["general", "news", "finance"])
        .optional()
        .default("general"),
      includeRawContent: z.boolean().optional().default(false),
    }),
  },
);

const agent = createDeepAgent({
  model: "ollama:north-mini-code-1.0",
  tools: [internetSearch],
});
```

For full details on defining and using LangChain tools (tool dicts, `StructuredTool`, return types, error handling, and more), see Tools.

## MCP tools

**Note**
  Deep Agents fully support Model Context Protocol (MCP), the open standard for connecting agents to external services. Load tools from any MCP server and pass them directly to `create_deep_agent`.

MCP is an open protocol that lets agents connect to a growing ecosystem of servers—databases, APIs, file systems, browsers, and more—through a standard interface. Instead of writing custom integration code for each service, you point Deep Agents at an MCP server and it gets all the tools that server exposes.

**Python**
Install `langchain-mcp-adapters` to connect to MCP servers:

```bash pip
pip install langchain-mcp-adapters
```

```bash uv
uv add langchain-mcp-adapters
```

Code example: [`code/deepagents/tools-mcp.py`](../code/deepagents/tools-mcp.py)

```python Google
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from deepagents import create_deep_agent

async def main():
    client = MultiServerMCPClient(
        {
            "my_server": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        }
    )
    tools = await client.get_tools()

    agent = create_deep_agent(
        model="google_genai:gemini-3.6-flash",
        tools=tools,
    )

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Use the MCP server to help me."}]},
        config={"configurable": {"thread_id": "1"}},
    )

asyncio.run(main())
```

```python OpenAI
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from deepagents import create_deep_agent

async def main():
    client = MultiServerMCPClient(
        {
            "my_server": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        }
    )
    tools = await client.get_tools()

    agent = create_deep_agent(
        model="openai:gpt-5.5",
        tools=tools,
    )

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Use the MCP server to help me."}]},
        config={"configurable": {"thread_id": "1"}},
    )

asyncio.run(main())
```

```python Anthropic
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from deepagents import create_deep_agent

async def main():
    client = MultiServerMCPClient(
        {
            "my_server": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        }
    )
    tools = await client.get_tools()

    agent = create_deep_agent(
        model="anthropic:claude-sonnet-4-6",
        tools=tools,
    )

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Use the MCP server to help me."}]},
        config={"configurable": {"thread_id": "1"}},
    )

asyncio.run(main())
```

```python OpenRouter
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from deepagents import create_deep_agent

async def main():
    client = MultiServerMCPClient(
        {
            "my_server": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        }
    )
    tools = await client.get_tools()

    agent = create_deep_agent(
        model="openrouter:z-ai/glm-5.2",
        tools=tools,
    )

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Use the MCP server to help me."}]},
        config={"configurable": {"thread_id": "1"}},
    )

asyncio.run(main())
```

```python Fireworks
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from deepagents import create_deep_agent

async def main():
    client = MultiServerMCPClient(
        {
            "my_server": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        }
    )
    tools = await client.get_tools()

    agent = create_deep_agent(
        model="fireworks:accounts/fireworks/models/glm-5p2",
        tools=tools,
    )

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Use the MCP server to help me."}]},
        config={"configurable": {"thread_id": "1"}},
    )

asyncio.run(main())
```

```python Baseten
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from deepagents import create_deep_agent

async def main():
    client = MultiServerMCPClient(
        {
            "my_server": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        }
    )
    tools = await client.get_tools()

    agent = create_deep_agent(
        model="baseten:zai-org/GLM-5.2",
        tools=tools,
    )

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Use the MCP server to help me."}]},
        config={"configurable": {"thread_id": "1"}},
    )

asyncio.run(main())
```

```python Ollama
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from deepagents import create_deep_agent

async def main():
    client = MultiServerMCPClient(
        {
            "my_server": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        }
    )
    tools = await client.get_tools()

    agent = create_deep_agent(
        model="ollama:north-mini-code-1.0",
        tools=tools,
    )

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Use the MCP server to help me."}]},
        config={"configurable": {"thread_id": "1"}},
    )

asyncio.run(main())
```

**JavaScript / TypeScript**
Install `@langchain/mcp-adapters` to connect to MCP servers:

```bash
npm install @langchain/mcp-adapters
```

Code example: [`code/deepagents/tools-mcp.ts`](../code/deepagents/tools-mcp.ts)

```ts Google
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
```

```ts OpenAI
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
```

```ts Anthropic
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
```

```ts OpenRouter
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
```

```ts Fireworks
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
```

```ts Baseten
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
```

```ts Ollama
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
```

For detailed configuration options—including stdio servers, OAuth authentication, tool filtering, and stateful sessions—see the full MCP guide.

## Built-in harness tools

In addition to the tools you provide, every Deep Agent comes with a built-in set of tools from the harness:

**Python**

| Tool | Description |
| ---- | ----------- |
| `ls` | List files in a directory. |
| `read_file` | Read file contents (with pagination and multimodal support). |
| `write_file` | Create a new file, or overwrite an existing one. |
| `edit_file` | Perform exact string replacements in files. |
| `delete` | Delete a file, or a directory and its contents recursively. The `delete` tool requires `deepagents>=0.7`. |
| `glob` | Find files matching a glob pattern. |
| `grep` | Search file contents. |
| `execute` | Run shell commands (sandbox backends only). |
| `task` | Spawn a subagent to handle a delegated task. |

**JavaScript / TypeScript**

| Tool | Description |
| ---- | ----------- |
| `ls` | List files in a directory. |
| `read_file` | Read file contents (with pagination and multimodal support). |
| `write_file` | Create new files. |
| `edit_file` | Perform exact string replacements in files. |
| `glob` | Find files matching a glob pattern. |
| `grep` | Search file contents. |
| `execute` | Run shell commands (sandbox backends only). |
| `task` | Spawn a subagent to handle a delegated task. |

To add structured task planning with `write_todos`, opt in with `TodoListMiddleware`. See [Task planning](../deepagents/overview.md#task-planning).

For a full breakdown of what each built-in tool does, see [Harness overview](../deepagents/overview.md#execution-environment).

## Multimodal tool outputs

Custom tools can return plain text or standard content blocks (text, images, audio, video, and files) when the selected model supports multimodal tool results. The built-in `read_file` tool also returns multimodal blocks for supported non-text file types.

Return a string for text-only results, or an ordered list of content blocks for text plus media or interleaved multimodal output. See [Multimodal](../deepagents/multimodality.md) and Tool return values for examples and context-compression considerations.
