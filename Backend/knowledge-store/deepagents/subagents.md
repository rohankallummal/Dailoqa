---
type: Documentation Page
title: Subagents
description: Learn how to use subagents to delegate work and keep context clean
product: deepagents
resource: /docs/deepagents/subagents
source: /oss/deepagents/subagents
tags:
  - deepagents
  - subagents
timestamp: 2026-08-13T16:33:11Z
code_examples:
  - ../code/deepagents/subagent-basic.py
  - ../code/deepagents/subagent-basic.ts
  - ../code/deepagents/subagents-compiled-subagent.py
  - ../code/deepagents/subagents-compiled-subagent.ts
  - ../code/deepagents/dynamic-subagents-quickstart.py
  - ../code/deepagents/dynamic-subagents-quickstart.ts
  - ../code/deepagents/dynamic-subagents-invoke.py
  - ../code/deepagents/dynamic-subagents-invoke.ts
  - ../code/deepagents/subagent-stream-progress.py
  - ../code/deepagents/subagent-stream-progress.ts
  - ../code/deepagents/subagents-structured-output.py
  - ../code/deepagents/subagents-structured-output.ts
  - ../code/deepagents/subagents-general-purpose-override.py
  - ../code/deepagents/subagents-general-purpose-override.ts
  - ../code/deepagents/skills-subagents.py
  - ../code/deepagents/skills-subagents.ts
  - ../code/deepagents/subagents-research-prompt.py
  - ../code/deepagents/subagents-research-prompt.ts
  - ../code/deepagents/subagents-email-tools-good.py
  - ../code/deepagents/subagents-email-tools-good.ts
  - ../code/deepagents/subagents-email-tools-bad.py
  - ../code/deepagents/subagents-email-tools-bad.ts
  - ../code/deepagents/subagents-choose-models.py
  - ../code/deepagents/subagents-choose-models.ts
  - ../code/deepagents/subagents-concise-results.py
  - ../code/deepagents/subagents-concise-results.ts
  - ../code/deepagents/subagents-multiple-specialized.py
  - ../code/deepagents/subagents-multiple-specialized.ts
  - ../code/deepagents/subagents-context-propagation.py
  - ../code/deepagents/subagents-context-propagation.ts
  - ../code/deepagents/subagents-per-subagent-context.py
  - ../code/deepagents/subagents-per-subagent-context.ts
  - ../code/deepagents/subagents-shared-lookup.py
  - ../code/deepagents/subagents-shared-lookup.ts
  - ../code/deepagents/subagents-flexible-search.py
  - ../code/deepagents/subagents-flexible-search.ts
  - ../code/deepagents/subagents-troubleshooting-description-good.py
  - ../code/deepagents/subagents-troubleshooting-description-good.ts
  - ../code/deepagents/subagents-troubleshooting-description-bad.py
  - ../code/deepagents/subagents-troubleshooting-description-bad.ts
  - ../code/deepagents/subagents-troubleshooting-delegate.py
  - ../code/deepagents/subagents-troubleshooting-delegate.ts
  - ../code/deepagents/subagents-troubleshooting-concise-prompt.py
  - ../code/deepagents/subagents-troubleshooting-concise-prompt.ts
  - ../code/deepagents/subagents-troubleshooting-filesystem-prompt.py
  - ../code/deepagents/subagents-troubleshooting-filesystem-prompt.ts
  - ../code/deepagents/subagents-troubleshooting-differentiate.py
  - ../code/deepagents/subagents-troubleshooting-differentiate.ts
---

# Subagents

A deep agent can create subagents to delegate work. You can specify custom subagents in the `subagents` parameter. Subagents are useful for context quarantine (keeping the main agent's context clean) and for providing specialized instructions.

This page covers **synchronous** subagents, where the supervisor blocks until the subagent finishes. For long-running tasks, parallel workstreams, or cases where you need mid-flight steering and cancellation, see Async subagents.

```mermaid
graph TB
    Main[Main Agent] --> |task tool| Sub[Subagent]

    Sub --> Research[Research]
    Sub --> Code[Code]
    Sub --> General[General]

    Research --> |isolated work| Result[Final Result]
    Code --> |isolated work| Result
    General --> |isolated work| Result

    Result --> Main
```

## Why use subagents?

Subagents solve the **context bloat problem**. When agents use tools with large outputs (web search, file reads, database queries), the context window fills up quickly with intermediate results. Subagents isolate this detailed work—the main agent receives only the final result, not the dozens of tool calls that produced it.

**When to use subagents:**
- ✅ Multi-step tasks that would clutter the main agent's context
- ✅ Specialized domains that need custom instructions or tools
- ✅ Tasks requiring different model capabilities
- ✅ When you want to keep the main agent focused on high-level coordination

**When NOT to use subagents:**
- ❌ Simple, single-step tasks
- ❌ When you need to maintain intermediate context
- ❌ When the overhead outweighs benefits

## Configuration

`subagents` should be a list of dictionaries or `CompiledSubAgent` objects. There are two types:

### Default subagent

Deep Agents automatically adds a synchronous `general-purpose` subagent unless you already provide a synchronous subagent with that name.

The `general-purpose` subagent has filesystem tools by default and can be customized with additional tools/middleware.

- To replace it, pass your own subagent named `general-purpose`.
- To rename or re-prompt the auto-added version, set `general_purpose_subagent=GeneralPurposeSubagentProfile(...)` on the active harness profile.
- To disable it, see [Running without subagents](#running-without-subagents) below.

### Running without subagents

To run an agent without the `task` tool, do two things:

1. Set `general_purpose_subagent=GeneralPurposeSubagentProfile(enabled=False)` on the active harness profile.
2. Pass no synchronous subagents via `subagents=` on `create_deep_agent`.

Deep Agents only attaches `SubAgentMiddleware` (and the `task` tool) when at least one synchronous subagent exists. With neither the default nor a caller-provided one, the agent runs without delegation.

Async subagents are unaffected—they flow through their own middleware and tools, described in Async subagents.

**Tip**
    Don't reach for `excluded_middleware` here—`SubAgentMiddleware` is required scaffolding and listing it raises `ValueError`. The `general_purpose_subagent.enabled = False` knob is the supported path.

## Custom subagents

You can define specialized subagents with specific tool by using the `subagents` parameter. For example to serve as a code reviewer, web researcher, or test runner.

For most use cases, define subagents as dictionaries with [SubAgent dictionaries](#subagent-dictionary-based). For complex workflows, use a [`CompiledSubAgent`](#compiledsubagent):

### SubAgent (Dictionary-based)

Define subagents as dictionaries matching the `SubAgent` spec with the following fields:

**Python**

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Required. Unique identifier for the subagent. The main agent uses this name when calling the `task()` tool. The subagent name becomes metadata for `AIMessage`s and for streaming, which helps to differentiate between agents. |
| `description` | `str` | Required. Description of what this subagent does. Be specific and action-oriented. The main agent uses this to decide when to delegate. |
| `system_prompt` | `str` | Required. Instructions for the subagent. Custom subagents must define their own. Include tool usage guidance and output format requirements.  Does not inherit from main agent. |
| `tools` | `list[Callable]` | Optional. Tools the subagent can use. Keep this minimal and include only what's needed.  Inherits from main agent by default. When specified, overrides the inherited tools entirely. |
| `model` | `str` \| `BaseChatModel` | Optional. Overrides the main agent's model. Omit to use the main agent's model.  Inherits from main agent by default. You can pass either a model identifier string like `'openai:gpt-5.5'` (using the `'provider:model'` format) or a LangChain chat model object (`init_chat_model("gpt-5.5")` or `ChatOpenAI(model="gpt-5.5")`). |
| `middleware` | `list[Middleware]` | Optional. Additional middleware for custom behavior, logging, or rate limiting.  Does not inherit from the main agent. Merged into the synchronous subagent stack: an instance whose `.name` matches a default replaces it in place, anything else lands after the last core middleware entry and before profile, prompt-caching, and memory. See Override a default middleware instance. For example, include a `FilesystemMiddleware` instance with a `tools` allowlist here to restrict the subagent's filesystem tools independently of the main agent. For more information, see the "Restricting filesystem tools" section under [Virtual filesystem access](../deepagents/overview.md#virtual-filesystem-access). |
| `interrupt_on` | `dict[str, bool \| InterruptOnConfig]` | Optional. Configure human-in-the-loop for specific tools. Options:`True`, `False`, or an `InterruptOnConfig` with `allowed_decisions`. Requires checkpointer.  Inherits from main agent by default. Subagent value overrides the default. |
| `skills` | `list[str]` | Optional. [Skills](../deepagents/skills.md) source paths. When specified, the subagent will load skills from these directories (e.g., `["/skills/research/", "/skills/web-search/"]`). This allows subagents to have different skill sets than the main agent.  Does not inherit from main agent. Only the general-purpose subagent inherits the main agent's skills. When a subagent has skills, it runs its own independent `SkillsMiddleware` instance. Skill state is fully isolated—a subagent's loaded skills are not visible to the parent, and vice versa. |
| `response_format` | `ResponseFormat` | Optional. [Structured output](../langchain/structured-output.md) schema for the subagent. When set, the parent receives the subagent's result as JSON instead of free-form text. Accepts Pydantic models, `ToolStrategy(...)`, `ProviderStrategy(...)`, or a raw schema type. See [Structured output](#structured-output). |
| `permissions` | `list[FilesystemPermission]` | Optional. Filesystem permission rules for the subagent. When set, **replaces** the parent agent's permissions entirely.  Inherits from main agent by default. |

**JavaScript / TypeScript**

| Field | Type | Description |
|-------|------|-------------|
| `name` | `string` | Required. Unique identifier for the subagent. The main agent uses this name when calling the `task()` tool. The subagent name becomes metadata for `AIMessage`s and for streaming, which helps to differentiate between agents. |
| `description` | `string` | Required. Description of what this subagent does. Be specific and action-oriented. The main agent uses this to decide when to delegate. |
| `systemPrompt` | `string` | Required. Instructions for the subagent. Custom subagents must define their own. Include tool usage guidance and output format requirements.  Does not inherit from main agent. |
| `tools` | `StructuredTool[]` | Optional. Tools the subagent can use. Keep this minimal and include only what's needed.  Inherits from main agent by default. When specified, overrides the inherited tools entirely. |
| `model` | `LanguageModelLike \| string` | Optional. Overrides the main agent's model. Omit to use the main agent's model.  Inherits from main agent by default. You can pass either a model identifier string like `'openai:gpt-5.5'` (using the `'provider:model'` format) or a LangChain chat model object (`await initChatModel("gpt-5.5")` or `new ChatOpenAI({ model: "gpt-5.5" })`). |
| `middleware` | `AgentMiddleware[]` | Optional. Additional middleware for custom behavior, logging, or rate limiting.  Does not inherit from the main agent. Appended to the synchronous subagent stack. |
| `interruptOn` | `Record<string, boolean \| InterruptOnConfig>` | Optional. Configure human-in-the-loop for specific tools. Options: `True`, `False`. or an `InterruptOnConfig` with `allowed_decisions`. Requires checkpointer.  Inherits from main agent by default. Subagent value overrides the default. |
| `skills` | `string[]` | Optional. [Skills](../deepagents/skills.md) source paths. When specified, the subagent will load skills from these directories (e.g., `["/skills/research/", "/skills/web-search/"]`). This allows subagents to have different skill sets than the main agent.  Does not inherit from main agent. Only the general-purpose subagent inherits the main agent's skills. When a subagent has skills, it runs its own independent `SkillsMiddleware` instance. Skill state is fully isolated—a subagent's loaded skills are not visible to the parent, and vice versa. |
| `responseFormat` | `ResponseFormat` | Optional. [Structured output](../langchain/structured-output.md) schema for the subagent. When set, the parent receives the subagent's result as JSON instead of free-form text. Accepts Zod schemas, JSON schema objects, `toolStrategy(...)`, or `providerStrategy(...)`. See [Structured output](#structured-output). |
| `permissions` | `FilesystemPermission[]` | Optional. Filesystem permission rules for the subagent. When set, **replaces** the parent agent's permissions entirely.  Inherits from main agent by default. |

### CompiledSubAgent

For complex workflows, use a prebuilt LangGraph graph as a `CompiledSubAgent`:

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Required. Unique identifier for the subagent. The subagent name becomes metadata for `AIMessage`s and for streaming, which helps to differentiate between agents. |
| `description` | `str` | Required. What this subagent does. |
| `runnable` | `Runnable` | Required. A compiled LangGraph graph (must call `.compile()` first). |

## Using SubAgent

**Python**
Code example: [`code/deepagents/subagent-basic.py`](../code/deepagents/subagent-basic.py)

```python
import os
from typing import Literal

from deepagents import create_deep_agent
from tavily import TavilyClient

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

research_subagent = {
    "name": "research-agent",
    "description": "Used to research more in depth questions",
    "system_prompt": "You are a great researcher",
    "tools": [internet_search],
    "model": "openai:gpt-5.5",  # Optional override, defaults to main agent model
}
subagents = [research_subagent]

agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    subagents=subagents,
)
```

**JavaScript / TypeScript**
Code example: [`code/deepagents/subagent-basic.ts`](../code/deepagents/subagent-basic.ts)

```ts Google
import { tool } from "langchain";
import { TavilySearch } from "@langchain/tavily";
import { createDeepAgent, type SubAgent } from "deepagents";
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

const researchSubagent: SubAgent = {
  name: "research-agent",
  description: "Used to research more in depth questions",
  systemPrompt: "You are a great researcher",
  tools: [internetSearch],
  model: "google-genai:gemini-3.6-flash", // Optional override, defaults to main agent model
};
const subagents = [researchSubagent];

const agent = createDeepAgent({
  model: "google_genai:gemini-3.6-flash",
  subagents,
});
```

```ts OpenAI
import { tool } from "langchain";
import { TavilySearch } from "@langchain/tavily";
import { createDeepAgent, type SubAgent } from "deepagents";
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

const researchSubagent: SubAgent = {
  name: "research-agent",
  description: "Used to research more in depth questions",
  systemPrompt: "You are a great researcher",
  tools: [internetSearch],
  model: "openai:gpt-5.5", // Optional override, defaults to main agent model
};
const subagents = [researchSubagent];

const agent = createDeepAgent({
  model: "google_genai:gemini-3.6-flash",
  subagents,
});
```

```ts Anthropic
import { tool } from "langchain";
import { TavilySearch } from "@langchain/tavily";
import { createDeepAgent, type SubAgent } from "deepagents";
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

const researchSubagent: SubAgent = {
  name: "research-agent",
  description: "Used to research more in depth questions",
  systemPrompt: "You are a great researcher",
  tools: [internetSearch],
  model: "anthropic:claude-sonnet-4-6", // Optional override, defaults to main agent model
};
const subagents = [researchSubagent];

const agent = createDeepAgent({
  model: "google_genai:gemini-3.6-flash",
  subagents,
});
```

```ts OpenRouter
import { tool } from "langchain";
import { TavilySearch } from "@langchain/tavily";
import { createDeepAgent, type SubAgent } from "deepagents";
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

const researchSubagent: SubAgent = {
  name: "research-agent",
  description: "Used to research more in depth questions",
  systemPrompt: "You are a great researcher",
  tools: [internetSearch],
  model: "openrouter:openrouter:z-ai/glm-5.2", // Optional override, defaults to main agent model
};
const subagents = [researchSubagent];

const agent = createDeepAgent({
  model: "google_genai:gemini-3.6-flash",
  subagents,
});
```

```ts Fireworks
import { tool } from "langchain";
import { TavilySearch } from "@langchain/tavily";
import { createDeepAgent, type SubAgent } from "deepagents";
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

const researchSubagent: SubAgent = {
  name: "research-agent",
  description: "Used to research more in depth questions",
  systemPrompt: "You are a great researcher",
  tools: [internetSearch],
  model: "fireworks:accounts/fireworks/models/glm-5p2", // Optional override, defaults to main agent model
};
const subagents = [researchSubagent];

const agent = createDeepAgent({
  model: "google_genai:gemini-3.6-flash",
  subagents,
});
```

```ts Baseten
import { tool } from "langchain";
import { TavilySearch } from "@langchain/tavily";
import { createDeepAgent, type SubAgent } from "deepagents";
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

const researchSubagent: SubAgent = {
  name: "research-agent",
  description: "Used to research more in depth questions",
  systemPrompt: "You are a great researcher",
  tools: [internetSearch],
  model: "baseten:zai-org/GLM-5.2", // Optional override, defaults to main agent model
};
const subagents = [researchSubagent];

const agent = createDeepAgent({
  model: "google_genai:gemini-3.6-flash",
  subagents,
});
```

```ts Ollama
import { tool } from "langchain";
import { TavilySearch } from "@langchain/tavily";
import { createDeepAgent, type SubAgent } from "deepagents";
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

const researchSubagent: SubAgent = {
  name: "research-agent",
  description: "Used to research more in depth questions",
  systemPrompt: "You are a great researcher",
  tools: [internetSearch],
  model: "ollama:north-mini-code-1.0", // Optional override, defaults to main agent model
};
const subagents = [researchSubagent];

const agent = createDeepAgent({
  model: "google_genai:gemini-3.6-flash",
  subagents,
});
```

## Using CompiledSubAgent

For more complex use cases, you can provide your custom subagents with `CompiledSubAgent`.
You can create a custom subagent using LangChain's `create_agent` or by making a custom LangGraph graph using the graph API.

If you're creating a custom LangGraph graph, make sure that the graph has a state key called `"messages"`:

**Python**
Code example: [`code/deepagents/subagents-compiled-subagent.py`](../code/deepagents/subagents-compiled-subagent.py)

```python Google
from deepagents import CompiledSubAgent, create_deep_agent
from langchain.agents import create_agent

def internet_search(query: str) -> str:
    """Run a web search."""
    return f"search results for {query}"

research_instructions = "You are a research coordinator."
your_model = "openai:gpt-5.5"
specialized_tools: list = []

# Create a custom agent graph
custom_graph = create_agent(
    model=your_model,
    tools=specialized_tools,
    system_prompt="You are a specialized agent for data analysis...",
)

# Use it as a custom subagent
custom_subagent = CompiledSubAgent(
    name="data-analyzer",
    description="Specialized agent for complex data analysis tasks",
    runnable=custom_graph,
)

subagents = [custom_subagent]

agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    tools=[internet_search],
    system_prompt=research_instructions,
    subagents=subagents,
)
```

```python OpenAI
from deepagents import CompiledSubAgent, create_deep_agent
from langchain.agents import create_agent

def internet_search(query: str) -> str:
    """Run a web search."""
    return f"search results for {query}"

research_instructions = "You are a research coordinator."
your_model = "openai:gpt-5.5"
specialized_tools: list = []

# Create a custom agent graph
custom_graph = create_agent(
    model=your_model,
    tools=specialized_tools,
    system_prompt="You are a specialized agent for data analysis...",
)

# Use it as a custom subagent
custom_subagent = CompiledSubAgent(
    name="data-analyzer",
    description="Specialized agent for complex data analysis tasks",
    runnable=custom_graph,
)

subagents = [custom_subagent]

agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[internet_search],
    system_prompt=research_instructions,
    subagents=subagents,
)
```

```python Anthropic
from deepagents import CompiledSubAgent, create_deep_agent
from langchain.agents import create_agent

def internet_search(query: str) -> str:
    """Run a web search."""
    return f"search results for {query}"

research_instructions = "You are a research coordinator."
your_model = "openai:gpt-5.5"
specialized_tools: list = []

# Create a custom agent graph
custom_graph = create_agent(
    model=your_model,
    tools=specialized_tools,
    system_prompt="You are a specialized agent for data analysis...",
)

# Use it as a custom subagent
custom_subagent = CompiledSubAgent(
    name="data-analyzer",
    description="Specialized agent for complex data analysis tasks",
    runnable=custom_graph,
)

subagents = [custom_subagent]

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[internet_search],
    system_prompt=research_instructions,
    subagents=subagents,
)
```

```python OpenRouter
from deepagents import CompiledSubAgent, create_deep_agent
from langchain.agents import create_agent

def internet_search(query: str) -> str:
    """Run a web search."""
    return f"search results for {query}"

research_instructions = "You are a research coordinator."
your_model = "openai:gpt-5.5"
specialized_tools: list = []

# Create a custom agent graph
custom_graph = create_agent(
    model=your_model,
    tools=specialized_tools,
    system_prompt="You are a specialized agent for data analysis...",
)

# Use it as a custom subagent
custom_subagent = CompiledSubAgent(
    name="data-analyzer",
    description="Specialized agent for complex data analysis tasks",
    runnable=custom_graph,
)

subagents = [custom_subagent]

agent = create_deep_agent(
    model="openrouter:z-ai/glm-5.2",
    tools=[internet_search],
    system_prompt=research_instructions,
    subagents=subagents,
)
```

```python Fireworks
from deepagents import CompiledSubAgent, create_deep_agent
from langchain.agents import create_agent

def internet_search(query: str) -> str:
    """Run a web search."""
    return f"search results for {query}"

research_instructions = "You are a research coordinator."
your_model = "openai:gpt-5.5"
specialized_tools: list = []

# Create a custom agent graph
custom_graph = create_agent(
    model=your_model,
    tools=specialized_tools,
    system_prompt="You are a specialized agent for data analysis...",
)

# Use it as a custom subagent
custom_subagent = CompiledSubAgent(
    name="data-analyzer",
    description="Specialized agent for complex data analysis tasks",
    runnable=custom_graph,
)

subagents = [custom_subagent]

agent = create_deep_agent(
    model="fireworks:accounts/fireworks/models/glm-5p2",
    tools=[internet_search],
    system_prompt=research_instructions,
    subagents=subagents,
)
```

```python Baseten
from deepagents import CompiledSubAgent, create_deep_agent
from langchain.agents import create_agent

def internet_search(query: str) -> str:
    """Run a web search."""
    return f"search results for {query}"

research_instructions = "You are a research coordinator."
your_model = "openai:gpt-5.5"
specialized_tools: list = []

# Create a custom agent graph
custom_graph = create_agent(
    model=your_model,
    tools=specialized_tools,
    system_prompt="You are a specialized agent for data analysis...",
)

# Use it as a custom subagent
custom_subagent = CompiledSubAgent(
    name="data-analyzer",
    description="Specialized agent for complex data analysis tasks",
    runnable=custom_graph,
)

subagents = [custom_subagent]

agent = create_deep_agent(
    model="baseten:zai-org/GLM-5.2",
    tools=[internet_search],
    system_prompt=research_instructions,
    subagents=subagents,
)
```

```python Ollama
from deepagents import CompiledSubAgent, create_deep_agent
from langchain.agents import create_agent

def internet_search(query: str) -> str:
    """Run a web search."""
    return f"search results for {query}"

research_instructions = "You are a research coordinator."
your_model = "openai:gpt-5.5"
specialized_tools: list = []

# Create a custom agent graph
custom_graph = create_agent(
    model=your_model,
    tools=specialized_tools,
    system_prompt="You are a specialized agent for data analysis...",
)

# Use it as a custom subagent
custom_subagent = CompiledSubAgent(
    name="data-analyzer",
    description="Specialized agent for complex data analysis tasks",
    runnable=custom_graph,
)

subagents = [custom_subagent]

agent = create_deep_agent(
    model="ollama:north-mini-code-1.0",
    tools=[internet_search],
    system_prompt=research_instructions,
    subagents=subagents,
)
```

**JavaScript / TypeScript**
Code example: [`code/deepagents/subagents-compiled-subagent.ts`](../code/deepagents/subagents-compiled-subagent.ts)

```ts Google
import { CompiledSubAgent, createDeepAgent } from "deepagents";
import { createAgent } from "langchain";
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

const researchInstructions = "You are a research coordinator.";
const yourModel = "google_genai:gemini-3.6-flash";
const specializedTools: never[] = [];

// Create a custom agent graph
const customGraph = createAgent({
  model: yourModel,
  tools: specializedTools,
  prompt: "You are a specialized agent for data analysis...",
});

// Use it as a custom subagent
const customSubagent: CompiledSubAgent = {
  name: "data-analyzer",
  description: "Specialized agent for complex data analysis tasks",
  runnable: customGraph,
};

const subagents = [customSubagent];

const agent = createDeepAgent({
  model: "google-genai:gemini-3.6-flash",
  tools: [internetSearch],
  systemPrompt: researchInstructions,
  subagents: subagents,
});
```

```ts OpenAI
import { CompiledSubAgent, createDeepAgent } from "deepagents";
import { createAgent } from "langchain";
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

const researchInstructions = "You are a research coordinator.";
const yourModel = "google_genai:gemini-3.6-flash";
const specializedTools: never[] = [];

// Create a custom agent graph
const customGraph = createAgent({
  model: yourModel,
  tools: specializedTools,
  prompt: "You are a specialized agent for data analysis...",
});

// Use it as a custom subagent
const customSubagent: CompiledSubAgent = {
  name: "data-analyzer",
  description: "Specialized agent for complex data analysis tasks",
  runnable: customGraph,
};

const subagents = [customSubagent];

const agent = createDeepAgent({
  model: "openai:gpt-5.5",
  tools: [internetSearch],
  systemPrompt: researchInstructions,
  subagents: subagents,
});
```

```ts Anthropic
import { CompiledSubAgent, createDeepAgent } from "deepagents";
import { createAgent } from "langchain";
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

const researchInstructions = "You are a research coordinator.";
const yourModel = "google_genai:gemini-3.6-flash";
const specializedTools: never[] = [];

// Create a custom agent graph
const customGraph = createAgent({
  model: yourModel,
  tools: specializedTools,
  prompt: "You are a specialized agent for data analysis...",
});

// Use it as a custom subagent
const customSubagent: CompiledSubAgent = {
  name: "data-analyzer",
  description: "Specialized agent for complex data analysis tasks",
  runnable: customGraph,
};

const subagents = [customSubagent];

const agent = createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  tools: [internetSearch],
  systemPrompt: researchInstructions,
  subagents: subagents,
});
```

```ts OpenRouter
import { CompiledSubAgent, createDeepAgent } from "deepagents";
import { createAgent } from "langchain";
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

const researchInstructions = "You are a research coordinator.";
const yourModel = "google_genai:gemini-3.6-flash";
const specializedTools: never[] = [];

// Create a custom agent graph
const customGraph = createAgent({
  model: yourModel,
  tools: specializedTools,
  prompt: "You are a specialized agent for data analysis...",
});

// Use it as a custom subagent
const customSubagent: CompiledSubAgent = {
  name: "data-analyzer",
  description: "Specialized agent for complex data analysis tasks",
  runnable: customGraph,
};

const subagents = [customSubagent];

const agent = createDeepAgent({
  model: "openrouter:openrouter:z-ai/glm-5.2",
  tools: [internetSearch],
  systemPrompt: researchInstructions,
  subagents: subagents,
});
```

```ts Fireworks
import { CompiledSubAgent, createDeepAgent } from "deepagents";
import { createAgent } from "langchain";
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

const researchInstructions = "You are a research coordinator.";
const yourModel = "google_genai:gemini-3.6-flash";
const specializedTools: never[] = [];

// Create a custom agent graph
const customGraph = createAgent({
  model: yourModel,
  tools: specializedTools,
  prompt: "You are a specialized agent for data analysis...",
});

// Use it as a custom subagent
const customSubagent: CompiledSubAgent = {
  name: "data-analyzer",
  description: "Specialized agent for complex data analysis tasks",
  runnable: customGraph,
};

const subagents = [customSubagent];

const agent = createDeepAgent({
  model: "fireworks:accounts/fireworks/models/glm-5p2",
  tools: [internetSearch],
  systemPrompt: researchInstructions,
  subagents: subagents,
});
```

```ts Baseten
import { CompiledSubAgent, createDeepAgent } from "deepagents";
import { createAgent } from "langchain";
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

const researchInstructions = "You are a research coordinator.";
const yourModel = "google_genai:gemini-3.6-flash";
const specializedTools: never[] = [];

// Create a custom agent graph
const customGraph = createAgent({
  model: yourModel,
  tools: specializedTools,
  prompt: "You are a specialized agent for data analysis...",
});

// Use it as a custom subagent
const customSubagent: CompiledSubAgent = {
  name: "data-analyzer",
  description: "Specialized agent for complex data analysis tasks",
  runnable: customGraph,
};

const subagents = [customSubagent];

const agent = createDeepAgent({
  model: "baseten:zai-org/GLM-5.2",
  tools: [internetSearch],
  systemPrompt: researchInstructions,
  subagents: subagents,
});
```

```ts Ollama
import { CompiledSubAgent, createDeepAgent } from "deepagents";
import { createAgent } from "langchain";
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

const researchInstructions = "You are a research coordinator.";
const yourModel = "google_genai:gemini-3.6-flash";
const specializedTools: never[] = [];

// Create a custom agent graph
const customGraph = createAgent({
  model: yourModel,
  tools: specializedTools,
  prompt: "You are a specialized agent for data analysis...",
});

// Use it as a custom subagent
const customSubagent: CompiledSubAgent = {
  name: "data-analyzer",
  description: "Specialized agent for complex data analysis tasks",
  runnable: customGraph,
};

const subagents = [customSubagent];

const agent = createDeepAgent({
  model: "ollama:north-mini-code-1.0",
  tools: [internetSearch],
  systemPrompt: researchInstructions,
  subagents: subagents,
});
```

## Dynamic subagents

By default, the main agent delegates to subagents through `task` tool calls (it can issue several in a single turn to run them in parallel). With an interpreter attached, the agent can instead dispatch subagents **from code**—using loops, branches, and parallel batches to fan work out across many items and synthesize the results programmatically. This is called dynamic subagents.

Reach for dynamic subagents when work spans many independent units (reviewing every file in a directory, triaging a batch of tickets), needs multiple perspectives, or benefits from recursive analysis.

**Warning**
    Dynamic subagents use the interpreter runtime, which is in **beta**. APIs and lifecycle behavior may change between releases.

### Enable dynamic subagents

Dynamic subagents become available as soon as the agent has both subagents and the interpreter middleware. Install the QuickJS interpreter package, then add `CodeInterpreterMiddleware` to your agent.

**Python**

```bash pip
pip install -U "deepagents[quickjs]"
```

```bash uv
uv add "deepagents[quickjs]"
```

Code example: [`code/deepagents/dynamic-subagents-quickstart.py`](../code/deepagents/dynamic-subagents-quickstart.py)

```python Google
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    subagents=[{
        "name": "reviewer",
        "description": "Reviews code for security issues, citing lines and severity",
        "system_prompt": "You are a security-focused code reviewer. Report issues with line numbers and severity.",
    }],
    middleware=[CodeInterpreterMiddleware()],
)
```

```python OpenAI
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="openai:gpt-5.5",
    subagents=[{
        "name": "reviewer",
        "description": "Reviews code for security issues, citing lines and severity",
        "system_prompt": "You are a security-focused code reviewer. Report issues with line numbers and severity.",
    }],
    middleware=[CodeInterpreterMiddleware()],
)
```

```python Anthropic
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    subagents=[{
        "name": "reviewer",
        "description": "Reviews code for security issues, citing lines and severity",
        "system_prompt": "You are a security-focused code reviewer. Report issues with line numbers and severity.",
    }],
    middleware=[CodeInterpreterMiddleware()],
)
```

```python OpenRouter
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="openrouter:z-ai/glm-5.2",
    subagents=[{
        "name": "reviewer",
        "description": "Reviews code for security issues, citing lines and severity",
        "system_prompt": "You are a security-focused code reviewer. Report issues with line numbers and severity.",
    }],
    middleware=[CodeInterpreterMiddleware()],
)
```

```python Fireworks
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="fireworks:accounts/fireworks/models/glm-5p2",
    subagents=[{
        "name": "reviewer",
        "description": "Reviews code for security issues, citing lines and severity",
        "system_prompt": "You are a security-focused code reviewer. Report issues with line numbers and severity.",
    }],
    middleware=[CodeInterpreterMiddleware()],
)
```

```python Baseten
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="baseten:zai-org/GLM-5.2",
    subagents=[{
        "name": "reviewer",
        "description": "Reviews code for security issues, citing lines and severity",
        "system_prompt": "You are a security-focused code reviewer. Report issues with line numbers and severity.",
    }],
    middleware=[CodeInterpreterMiddleware()],
)
```

```python Ollama
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="ollama:north-mini-code-1.0",
    subagents=[{
        "name": "reviewer",
        "description": "Reviews code for security issues, citing lines and severity",
        "system_prompt": "You are a security-focused code reviewer. Report issues with line numbers and severity.",
    }],
    middleware=[CodeInterpreterMiddleware()],
)
```

**Note**
    Dynamic subagent dispatch is on by default whenever the agent has subagents and the interpreter middleware. Pass `CodeInterpreterMiddleware(subagents=False)` to require dispatch through the normal `task` tool path. Interpreters require `langchain-quickjs>=0.2.0` and Python `>=3.11`.

**JavaScript / TypeScript**

```bash npm
npm install deepagents @langchain/quickjs
```

```bash pnpm
pnpm add deepagents @langchain/quickjs
```

```bash yarn
yarn add deepagents @langchain/quickjs
```

Code example: [`code/deepagents/dynamic-subagents-quickstart.ts`](../code/deepagents/dynamic-subagents-quickstart.ts)

```ts Google
import { createDeepAgent } from "deepagents";
import { createCodeInterpreterMiddleware } from "@langchain/quickjs";

const agent = createDeepAgent({
  model: "google-genai:gemini-3.6-flash",
  subagents: [{
    name: "reviewer",
    description: "Reviews code for security issues, citing lines and severity",
    systemPrompt: "You are a security-focused code reviewer. Report issues with line numbers and severity.",
  }],
  middleware: [createCodeInterpreterMiddleware()],
});
```

```ts OpenAI
import { createDeepAgent } from "deepagents";
import { createCodeInterpreterMiddleware } from "@langchain/quickjs";

const agent = createDeepAgent({
  model: "openai:gpt-5.5",
  subagents: [{
    name: "reviewer",
    description: "Reviews code for security issues, citing lines and severity",
    systemPrompt: "You are a security-focused code reviewer. Report issues with line numbers and severity.",
  }],
  middleware: [createCodeInterpreterMiddleware()],
});
```

```ts Anthropic
import { createDeepAgent } from "deepagents";
import { createCodeInterpreterMiddleware } from "@langchain/quickjs";

const agent = createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  subagents: [{
    name: "reviewer",
    description: "Reviews code for security issues, citing lines and severity",
    systemPrompt: "You are a security-focused code reviewer. Report issues with line numbers and severity.",
  }],
  middleware: [createCodeInterpreterMiddleware()],
});
```

```ts OpenRouter
import { createDeepAgent } from "deepagents";
import { createCodeInterpreterMiddleware } from "@langchain/quickjs";

const agent = createDeepAgent({
  model: "openrouter:openrouter:z-ai/glm-5.2",
  subagents: [{
    name: "reviewer",
    description: "Reviews code for security issues, citing lines and severity",
    systemPrompt: "You are a security-focused code reviewer. Report issues with line numbers and severity.",
  }],
  middleware: [createCodeInterpreterMiddleware()],
});
```

```ts Fireworks
import { createDeepAgent } from "deepagents";
import { createCodeInterpreterMiddleware } from "@langchain/quickjs";

const agent = createDeepAgent({
  model: "fireworks:accounts/fireworks/models/glm-5p2",
  subagents: [{
    name: "reviewer",
    description: "Reviews code for security issues, citing lines and severity",
    systemPrompt: "You are a security-focused code reviewer. Report issues with line numbers and severity.",
  }],
  middleware: [createCodeInterpreterMiddleware()],
});
```

```ts Baseten
import { createDeepAgent } from "deepagents";
import { createCodeInterpreterMiddleware } from "@langchain/quickjs";

const agent = createDeepAgent({
  model: "baseten:zai-org/GLM-5.2",
  subagents: [{
    name: "reviewer",
    description: "Reviews code for security issues, citing lines and severity",
    systemPrompt: "You are a security-focused code reviewer. Report issues with line numbers and severity.",
  }],
  middleware: [createCodeInterpreterMiddleware()],
});
```

```ts Ollama
import { createDeepAgent } from "deepagents";
import { createCodeInterpreterMiddleware } from "@langchain/quickjs";

const agent = createDeepAgent({
  model: "ollama:north-mini-code-1.0",
  subagents: [{
    name: "reviewer",
    description: "Reviews code for security issues, citing lines and severity",
    systemPrompt: "You are a security-focused code reviewer. Report issues with line numbers and severity.",
  }],
  middleware: [createCodeInterpreterMiddleware()],
});
```

**Note**
    Dynamic subagent dispatch is on by default whenever the agent has subagents and the interpreter middleware. Pass `createCodeInterpreterMiddleware({ subagents: false })` to require dispatch through the normal `task` tool path.

### Trigger dynamic orchestration

Dynamic dispatch is implicit: the agent decides to fan work out from code based on the shape of the task, not a per-call flag.

**Tip**
    **The word "workflow" is a useful trigger.** The built-in interpreter system prompt treats a "workflow" as a signal to organize work through the interpreter—dispatching subagents with `task()` from code. Phrasing a request as a "workflow" is a deliberate lever you can pull to opt into dynamic orchestration: include it when you want the agent to fan work out from code. For a single, direct delegation, phrase the request plainly instead.

For example, phrasing the request as a "workflow" opts into fan-out from code:

**Python**
Code example: [`code/deepagents/dynamic-subagents-invoke.py`](../code/deepagents/dynamic-subagents-invoke.py)

```python
result = agent.invoke({
    "messages": [{"role": "user", "content": "Run a workflow that reviews every file in src/routes/ and summarizes the top risks."}]
})
```

**JavaScript / TypeScript**
Code example: [`code/deepagents/dynamic-subagents-invoke.ts`](../code/deepagents/dynamic-subagents-invoke.ts)

```ts
const result = await agent.invoke({
  messages: [{ role: "user", content: "Run a workflow that reviews every file in src/routes/ and summarizes the top risks." }],
});
```

For configuration, advanced orchestration patterns, and safety notes, see Dynamic subagents.

### Use with a coding agent

The fastest way to try dynamic subagents is with `dcode`, the LangChain terminal coding agent built on a Deep Agent. It ships with the code interpreter enabled, so dynamic subagents work out of the box with nothing to wire up.

Install `dcode`:

```bash
curl -LsSf https://langch.in/dcode | bash
```

Run it:

```bash
dcode
```

To trigger dynamic subagents, ask for a "workflow". Instead of grinding through the work itself or managing fan-out through its native `task` tool, the agent writes an orchestration script that calls the built-in `task()` global and runs it in the code interpreter. For example: "Run a workflow to review every file in src/ for SQL injection."

As subagents spawn, `dcode` shows them live in the dynamic subagents panel, grouped into phases by dispatch.

  _Figure: The dcode dynamic subagents panel showing spawned subagents grouped into phases by dispatch_

`dcode` is the fastest way to try this, but you can also use dynamic subagents in the coding agent of your choice over ACP (for example, Zed).

## Streaming

Deep Agents support streaming updates from both the coordinator and every delegated subagent.

**Python**
Use `stream_events` to get typed projections—separate iterators for subagents, messages, tool calls, and values—so you can consume each independently.

**JavaScript / TypeScript**
Use `streamEvents` to get typed projections—separate iterators for subagents, messages, tool calls, and values—so you can consume each independently.

### Stream subagent progress

The simplest pattern is to iterate `stream.subagents` to track each delegated task as it starts, runs, and completes. Each subagent handle exposes `.name`, `.messages`, `.tool_calls`, and `.output`.

**Python**

Code example: [`code/deepagents/subagent-stream-progress.py`](../code/deepagents/subagent-stream-progress.py)

```python Google
from deepagents import (
    create_deep_agent
)

agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    system_prompt=(
        "You are a project coordinator with no research knowledge. "
        "For every user request, you must call the task() tool with "
        "subagent_type set to research-agent. Never answer research "
        "questions yourself."
    ),
    subagents=[
        {
            "name": "research-agent",
            "description": (
                "Delegate research to this subagent. Give one topic at a time."
            ),
            "system_prompt": (
                "You are a great researcher. Return a brief summary."
            ),
        },
    ],
    name="main-agent",
)

if __name__ == "__main__":
    stream = agent.stream_events(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Research one recent advance in quantum computing.",
                }
            ]
        },
        version="v3",
    )

    coordinator_messages: list[str] = []
    subagent_handles = []

    for name, item in stream.interleave("messages", "subagents"):
        if name == "messages":
            print("[coordinator]", item.text)
            coordinator_messages.append(item.text)
        else:
            print(f"[{item.name}] started")
            subagent_handles.append(item)
            for message in item.messages:
                print(f"[{item.name}]", message.text)
            print(f"[{item.name}] status: {item.status}")
```

```python OpenAI
from deepagents import (
    create_deep_agent
)

agent = create_deep_agent(
    model="openai:gpt-5.5",
    system_prompt=(
        "You are a project coordinator with no research knowledge. "
        "For every user request, you must call the task() tool with "
        "subagent_type set to research-agent. Never answer research "
        "questions yourself."
    ),
    subagents=[
        {
            "name": "research-agent",
            "description": (
                "Delegate research to this subagent. Give one topic at a time."
            ),
            "system_prompt": (
                "You are a great researcher. Return a brief summary."
            ),
        },
    ],
    name="main-agent",
)

if __name__ == "__main__":
    stream = agent.stream_events(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Research one recent advance in quantum computing.",
                }
            ]
        },
        version="v3",
    )

    coordinator_messages: list[str] = []
    subagent_handles = []

    for name, item in stream.interleave("messages", "subagents"):
        if name == "messages":
            print("[coordinator]", item.text)
            coordinator_messages.append(item.text)
        else:
            print(f"[{item.name}] started")
            subagent_handles.append(item)
            for message in item.messages:
                print(f"[{item.name}]", message.text)
            print(f"[{item.name}] status: {item.status}")
```

```python Anthropic
from deepagents import (
    create_deep_agent
)

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt=(
        "You are a project coordinator with no research knowledge. "
        "For every user request, you must call the task() tool with "
        "subagent_type set to research-agent. Never answer research "
        "questions yourself."
    ),
    subagents=[
        {
            "name": "research-agent",
            "description": (
                "Delegate research to this subagent. Give one topic at a time."
            ),
            "system_prompt": (
                "You are a great researcher. Return a brief summary."
            ),
        },
    ],
    name="main-agent",
)

if __name__ == "__main__":
    stream = agent.stream_events(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Research one recent advance in quantum computing.",
                }
            ]
        },
        version="v3",
    )

    coordinator_messages: list[str] = []
    subagent_handles = []

    for name, item in stream.interleave("messages", "subagents"):
        if name == "messages":
            print("[coordinator]", item.text)
            coordinator_messages.append(item.text)
        else:
            print(f"[{item.name}] started")
            subagent_handles.append(item)
            for message in item.messages:
                print(f"[{item.name}]", message.text)
            print(f"[{item.name}] status: {item.status}")
```

```python OpenRouter
from deepagents import (
    create_deep_agent
)

agent = create_deep_agent(
    model="openrouter:z-ai/glm-5.2",
    system_prompt=(
        "You are a project coordinator with no research knowledge. "
        "For every user request, you must call the task() tool with "
        "subagent_type set to research-agent. Never answer research "
        "questions yourself."
    ),
    subagents=[
        {
            "name": "research-agent",
            "description": (
                "Delegate research to this subagent. Give one topic at a time."
            ),
            "system_prompt": (
                "You are a great researcher. Return a brief summary."
            ),
        },
    ],
    name="main-agent",
)

if __name__ == "__main__":
    stream = agent.stream_events(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Research one recent advance in quantum computing.",
                }
            ]
        },
        version="v3",
    )

    coordinator_messages: list[str] = []
    subagent_handles = []

    for name, item in stream.interleave("messages", "subagents"):
        if name == "messages":
            print("[coordinator]", item.text)
            coordinator_messages.append(item.text)
        else:
            print(f"[{item.name}] started")
            subagent_handles.append(item)
            for message in item.messages:
                print(f"[{item.name}]", message.text)
            print(f"[{item.name}] status: {item.status}")
```

```python Fireworks
from deepagents import (
    create_deep_agent
)

agent = create_deep_agent(
    model="fireworks:accounts/fireworks/models/glm-5p2",
    system_prompt=(
        "You are a project coordinator with no research knowledge. "
        "For every user request, you must call the task() tool with "
        "subagent_type set to research-agent. Never answer research "
        "questions yourself."
    ),
    subagents=[
        {
            "name": "research-agent",
            "description": (
                "Delegate research to this subagent. Give one topic at a time."
            ),
            "system_prompt": (
                "You are a great researcher. Return a brief summary."
            ),
        },
    ],
    name="main-agent",
)

if __name__ == "__main__":
    stream = agent.stream_events(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Research one recent advance in quantum computing.",
                }
            ]
        },
        version="v3",
    )

    coordinator_messages: list[str] = []
    subagent_handles = []

    for name, item in stream.interleave("messages", "subagents"):
        if name == "messages":
            print("[coordinator]", item.text)
            coordinator_messages.append(item.text)
        else:
            print(f"[{item.name}] started")
            subagent_handles.append(item)
            for message in item.messages:
                print(f"[{item.name}]", message.text)
            print(f"[{item.name}] status: {item.status}")
```

```python Baseten
from deepagents import (
    create_deep_agent
)

agent = create_deep_agent(
    model="baseten:zai-org/GLM-5.2",
    system_prompt=(
        "You are a project coordinator with no research knowledge. "
        "For every user request, you must call the task() tool with "
        "subagent_type set to research-agent. Never answer research "
        "questions yourself."
    ),
    subagents=[
        {
            "name": "research-agent",
            "description": (
                "Delegate research to this subagent. Give one topic at a time."
            ),
            "system_prompt": (
                "You are a great researcher. Return a brief summary."
            ),
        },
    ],
    name="main-agent",
)

if __name__ == "__main__":
    stream = agent.stream_events(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Research one recent advance in quantum computing.",
                }
            ]
        },
        version="v3",
    )

    coordinator_messages: list[str] = []
    subagent_handles = []

    for name, item in stream.interleave("messages", "subagents"):
        if name == "messages":
            print("[coordinator]", item.text)
            coordinator_messages.append(item.text)
        else:
            print(f"[{item.name}] started")
            subagent_handles.append(item)
            for message in item.messages:
                print(f"[{item.name}]", message.text)
            print(f"[{item.name}] status: {item.status}")
```

```python Ollama
from deepagents import (
    create_deep_agent
)

agent = create_deep_agent(
    model="ollama:north-mini-code-1.0",
    system_prompt=(
        "You are a project coordinator with no research knowledge. "
        "For every user request, you must call the task() tool with "
        "subagent_type set to research-agent. Never answer research "
        "questions yourself."
    ),
    subagents=[
        {
            "name": "research-agent",
            "description": (
                "Delegate research to this subagent. Give one topic at a time."
            ),
            "system_prompt": (
                "You are a great researcher. Return a brief summary."
            ),
        },
    ],
    name="main-agent",
)

if __name__ == "__main__":
    stream = agent.stream_events(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Research one recent advance in quantum computing.",
                }
            ]
        },
        version="v3",
    )

    coordinator_messages: list[str] = []
    subagent_handles = []

    for name, item in stream.interleave("messages", "subagents"):
        if name == "messages":
            print("[coordinator]", item.text)
            coordinator_messages.append(item.text)
        else:
            print(f"[{item.name}] started")
            subagent_handles.append(item)
            for message in item.messages:
                print(f"[{item.name}]", message.text)
            print(f"[{item.name}] status: {item.status}")
```

**JavaScript / TypeScript**

Code example: [`code/deepagents/subagent-stream-progress.ts`](../code/deepagents/subagent-stream-progress.ts)

```ts Google
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  model: "google-genai:gemini-3.6-flash",
  systemPrompt:
    "You are a project coordinator with no research knowledge. " +
    "For every user request, you must call the task() tool with " +
    "subagent_type set to research-agent. Never answer research " +
    "questions yourself.",
  subagents: [
    {
      name: "research-agent",
      description:
        "Delegate research to this subagent. Give one topic at a time.",
      systemPrompt: "You are a great researcher. Return a brief summary.",
    },
  ],
});

async function streamSubagentProgress() {
  const stream = await agent.streamEvents(
    {
      messages: [
        {
          role: "user",
          content: "Research one recent advance in quantum computing.",
        },
      ],
    },
    { version: "v3" },
  );

  const coordinatorMessages: string[] = [];
  const subagentHandles: { name: string }[] = [];

  await Promise.all([
    (async () => {
      for await (const message of stream.messages) {
        console.log("[coordinator]", await message.text);
        coordinatorMessages.push(await message.text);
      }
    })(),
    (async () => {
      for await (const subagent of stream.subagents) {
        console.log(`[${subagent.name}] started`);
        subagentHandles.push({ name: subagent.name });
        for await (const message of subagent.messages) {
          console.log(`[${subagent.name}]`, await message.text);
        }
      }
    })(),
  ]);

  return { coordinatorMessages, subagentHandles };
}
```

```ts OpenAI
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  model: "openai:gpt-5.5",
  systemPrompt:
    "You are a project coordinator with no research knowledge. " +
    "For every user request, you must call the task() tool with " +
    "subagent_type set to research-agent. Never answer research " +
    "questions yourself.",
  subagents: [
    {
      name: "research-agent",
      description:
        "Delegate research to this subagent. Give one topic at a time.",
      systemPrompt: "You are a great researcher. Return a brief summary.",
    },
  ],
});

async function streamSubagentProgress() {
  const stream = await agent.streamEvents(
    {
      messages: [
        {
          role: "user",
          content: "Research one recent advance in quantum computing.",
        },
      ],
    },
    { version: "v3" },
  );

  const coordinatorMessages: string[] = [];
  const subagentHandles: { name: string }[] = [];

  await Promise.all([
    (async () => {
      for await (const message of stream.messages) {
        console.log("[coordinator]", await message.text);
        coordinatorMessages.push(await message.text);
      }
    })(),
    (async () => {
      for await (const subagent of stream.subagents) {
        console.log(`[${subagent.name}] started`);
        subagentHandles.push({ name: subagent.name });
        for await (const message of subagent.messages) {
          console.log(`[${subagent.name}]`, await message.text);
        }
      }
    })(),
  ]);

  return { coordinatorMessages, subagentHandles };
}
```

```ts Anthropic
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  systemPrompt:
    "You are a project coordinator with no research knowledge. " +
    "For every user request, you must call the task() tool with " +
    "subagent_type set to research-agent. Never answer research " +
    "questions yourself.",
  subagents: [
    {
      name: "research-agent",
      description:
        "Delegate research to this subagent. Give one topic at a time.",
      systemPrompt: "You are a great researcher. Return a brief summary.",
    },
  ],
});

async function streamSubagentProgress() {
  const stream = await agent.streamEvents(
    {
      messages: [
        {
          role: "user",
          content: "Research one recent advance in quantum computing.",
        },
      ],
    },
    { version: "v3" },
  );

  const coordinatorMessages: string[] = [];
  const subagentHandles: { name: string }[] = [];

  await Promise.all([
    (async () => {
      for await (const message of stream.messages) {
        console.log("[coordinator]", await message.text);
        coordinatorMessages.push(await message.text);
      }
    })(),
    (async () => {
      for await (const subagent of stream.subagents) {
        console.log(`[${subagent.name}] started`);
        subagentHandles.push({ name: subagent.name });
        for await (const message of subagent.messages) {
          console.log(`[${subagent.name}]`, await message.text);
        }
      }
    })(),
  ]);

  return { coordinatorMessages, subagentHandles };
}
```

```ts OpenRouter
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  model: "openrouter:openrouter:z-ai/glm-5.2",
  systemPrompt:
    "You are a project coordinator with no research knowledge. " +
    "For every user request, you must call the task() tool with " +
    "subagent_type set to research-agent. Never answer research " +
    "questions yourself.",
  subagents: [
    {
      name: "research-agent",
      description:
        "Delegate research to this subagent. Give one topic at a time.",
      systemPrompt: "You are a great researcher. Return a brief summary.",
    },
  ],
});

async function streamSubagentProgress() {
  const stream = await agent.streamEvents(
    {
      messages: [
        {
          role: "user",
          content: "Research one recent advance in quantum computing.",
        },
      ],
    },
    { version: "v3" },
  );

  const coordinatorMessages: string[] = [];
  const subagentHandles: { name: string }[] = [];

  await Promise.all([
    (async () => {
      for await (const message of stream.messages) {
        console.log("[coordinator]", await message.text);
        coordinatorMessages.push(await message.text);
      }
    })(),
    (async () => {
      for await (const subagent of stream.subagents) {
        console.log(`[${subagent.name}] started`);
        subagentHandles.push({ name: subagent.name });
        for await (const message of subagent.messages) {
          console.log(`[${subagent.name}]`, await message.text);
        }
      }
    })(),
  ]);

  return { coordinatorMessages, subagentHandles };
}
```

```ts Fireworks
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  model: "fireworks:accounts/fireworks/models/glm-5p2",
  systemPrompt:
    "You are a project coordinator with no research knowledge. " +
    "For every user request, you must call the task() tool with " +
    "subagent_type set to research-agent. Never answer research " +
    "questions yourself.",
  subagents: [
    {
      name: "research-agent",
      description:
        "Delegate research to this subagent. Give one topic at a time.",
      systemPrompt: "You are a great researcher. Return a brief summary.",
    },
  ],
});

async function streamSubagentProgress() {
  const stream = await agent.streamEvents(
    {
      messages: [
        {
          role: "user",
          content: "Research one recent advance in quantum computing.",
        },
      ],
    },
    { version: "v3" },
  );

  const coordinatorMessages: string[] = [];
  const subagentHandles: { name: string }[] = [];

  await Promise.all([
    (async () => {
      for await (const message of stream.messages) {
        console.log("[coordinator]", await message.text);
        coordinatorMessages.push(await message.text);
      }
    })(),
    (async () => {
      for await (const subagent of stream.subagents) {
        console.log(`[${subagent.name}] started`);
        subagentHandles.push({ name: subagent.name });
        for await (const message of subagent.messages) {
          console.log(`[${subagent.name}]`, await message.text);
        }
      }
    })(),
  ]);

  return { coordinatorMessages, subagentHandles };
}
```

```ts Baseten
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  model: "baseten:zai-org/GLM-5.2",
  systemPrompt:
    "You are a project coordinator with no research knowledge. " +
    "For every user request, you must call the task() tool with " +
    "subagent_type set to research-agent. Never answer research " +
    "questions yourself.",
  subagents: [
    {
      name: "research-agent",
      description:
        "Delegate research to this subagent. Give one topic at a time.",
      systemPrompt: "You are a great researcher. Return a brief summary.",
    },
  ],
});

async function streamSubagentProgress() {
  const stream = await agent.streamEvents(
    {
      messages: [
        {
          role: "user",
          content: "Research one recent advance in quantum computing.",
        },
      ],
    },
    { version: "v3" },
  );

  const coordinatorMessages: string[] = [];
  const subagentHandles: { name: string }[] = [];

  await Promise.all([
    (async () => {
      for await (const message of stream.messages) {
        console.log("[coordinator]", await message.text);
        coordinatorMessages.push(await message.text);
      }
    })(),
    (async () => {
      for await (const subagent of stream.subagents) {
        console.log(`[${subagent.name}] started`);
        subagentHandles.push({ name: subagent.name });
        for await (const message of subagent.messages) {
          console.log(`[${subagent.name}]`, await message.text);
        }
      }
    })(),
  ]);

  return { coordinatorMessages, subagentHandles };
}
```

```ts Ollama
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  model: "ollama:north-mini-code-1.0",
  systemPrompt:
    "You are a project coordinator with no research knowledge. " +
    "For every user request, you must call the task() tool with " +
    "subagent_type set to research-agent. Never answer research " +
    "questions yourself.",
  subagents: [
    {
      name: "research-agent",
      description:
        "Delegate research to this subagent. Give one topic at a time.",
      systemPrompt: "You are a great researcher. Return a brief summary.",
    },
  ],
});

async function streamSubagentProgress() {
  const stream = await agent.streamEvents(
    {
      messages: [
        {
          role: "user",
          content: "Research one recent advance in quantum computing.",
        },
      ],
    },
    { version: "v3" },
  );

  const coordinatorMessages: string[] = [];
  const subagentHandles: { name: string }[] = [];

  await Promise.all([
    (async () => {
      for await (const message of stream.messages) {
        console.log("[coordinator]", await message.text);
        coordinatorMessages.push(await message.text);
      }
    })(),
    (async () => {
      for await (const subagent of stream.subagents) {
        console.log(`[${subagent.name}] started`);
        subagentHandles.push({ name: subagent.name });
        for await (const message of subagent.messages) {
          console.log(`[${subagent.name}]`, await message.text);
        }
      }
    })(),
  ]);

  return { coordinatorMessages, subagentHandles };
}
```

### LangSmith tracing

As your deep agent runs, all runs executed by a subagent or the coordinator will have the agent name in their metadata under the `lc_agent_name` key—for example, `{'lc_agent_name': 'research-agent'}`. This lets you identify and filter runs by subagent in LangSmith.

_Figure: LangSmith Example trace showing the metadata_

## Filter by subagent in LangSmith

Because each subagent's `name` is written to the `lc_agent_name` metadata key on every run it produces, you can use LangSmith's metadata filtering to isolate all runs from a specific subagent — useful for debugging, monitoring, or comparing subagent behavior over time.

### Filter in the LangSmith UI

1. Open your tracing project in LangSmith.
2. Switch the view to **Runs** on the Tracing project page to see individual spans.
3. Click **Add filter** and select **Metadata**.
4. Set the **Key** to `lc_agent_name` and the **Value** to the subagent name, for example `coordinator`.

_Figure: LangSmith Runs view with a metadata filter on lc_agent_name set to coordinator_

This shows only the runs produced by that subagent. You can save the filter as a named view for reuse. For a full reference on filtering options, see Filter traces.

### Filter programmatically with the SDK

Use the `has` comparator in the LangSmith filter query language to match runs by metadata key-value pair:

```python
from langsmith import Client

client = Client()

runs = client.list_runs(
    project_name="<your-project>",
    filter='has(metadata, \'{"lc_agent_name": "research-agent"}\')',
)

for run in runs:
    print(run.name, run.start_time, run.status)
```

To fetch runs from _any_ named subagent (excluding the main agent), filter for runs that have the `lc_agent_name` key at all:

```python
runs = client.list_runs(
    project_name="<your-project>",
    filter="has(metadata, 'lc_agent_name')",
)
```

For the full filter query language reference, see Trace query syntax.

## Structured output

Subagents support [structured output](../langchain/structured-output.md), so the parent agent receives predictable, parseable JSON instead of free-form text.

**Python**
**Note**
    Structured output for subagents requires `deepagents>=0.5.3`.

Pass `response_format` on the subagent config. When the subagent finishes, its structured response is JSON-serialized and returned as the `ToolMessage` content to the parent agent. The schema accepts anything supported by `create_agent`: Pydantic models, `ToolStrategy(...)`, `ProviderStrategy(...)`, or a raw schema type.

Code example: [`code/deepagents/subagents-structured-output.py`](../code/deepagents/subagents-structured-output.py)

```python Google
import asyncio

from pydantic import BaseModel, Field

from deepagents import create_deep_agent

def web_search(query: str) -> str:
    """Search the web."""
    return f"web results for {query}"

class ResearchFindings(BaseModel):
    """Structured findings from a research task."""

    summary: str = Field(description="Summary of findings")
    confidence: float = Field(description="Confidence score from 0 to 1")
    sources: list[str] = Field(description="List of source URLs")

research_subagent = {
    "name": "researcher",
    "description": "Researches topics and returns structured findings",
    "system_prompt": "Research the given topic thoroughly. Return your findings.",
    "tools": [web_search],
    "response_format": ResearchFindings,
}

agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    subagents=[research_subagent],
)

async def main():
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Research recent advances in quantum computing"}]}
    )
    return result

result = asyncio.run(main())

# The parent's ToolMessage contains JSON-serialized structured data:
# '{"summary": "...", "confidence": 0.87, "sources": ["https://..."]}'
```

```python OpenAI
import asyncio

from pydantic import BaseModel, Field

from deepagents import create_deep_agent

def web_search(query: str) -> str:
    """Search the web."""
    return f"web results for {query}"

class ResearchFindings(BaseModel):
    """Structured findings from a research task."""

    summary: str = Field(description="Summary of findings")
    confidence: float = Field(description="Confidence score from 0 to 1")
    sources: list[str] = Field(description="List of source URLs")

research_subagent = {
    "name": "researcher",
    "description": "Researches topics and returns structured findings",
    "system_prompt": "Research the given topic thoroughly. Return your findings.",
    "tools": [web_search],
    "response_format": ResearchFindings,
}

agent = create_deep_agent(
    model="openai:gpt-5.5",
    subagents=[research_subagent],
)

async def main():
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Research recent advances in quantum computing"}]}
    )
    return result

result = asyncio.run(main())

# The parent's ToolMessage contains JSON-serialized structured data:
# '{"summary": "...", "confidence": 0.87, "sources": ["https://..."]}'
```

```python Anthropic
import asyncio

from pydantic import BaseModel, Field

from deepagents import create_deep_agent

def web_search(query: str) -> str:
    """Search the web."""
    return f"web results for {query}"

class ResearchFindings(BaseModel):
    """Structured findings from a research task."""

    summary: str = Field(description="Summary of findings")
    confidence: float = Field(description="Confidence score from 0 to 1")
    sources: list[str] = Field(description="List of source URLs")

research_subagent = {
    "name": "researcher",
    "description": "Researches topics and returns structured findings",
    "system_prompt": "Research the given topic thoroughly. Return your findings.",
    "tools": [web_search],
    "response_format": ResearchFindings,
}

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    subagents=[research_subagent],
)

async def main():
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Research recent advances in quantum computing"}]}
    )
    return result

result = asyncio.run(main())

# The parent's ToolMessage contains JSON-serialized structured data:
# '{"summary": "...", "confidence": 0.87, "sources": ["https://..."]}'
```

```python OpenRouter
import asyncio

from pydantic import BaseModel, Field

from deepagents import create_deep_agent

def web_search(query: str) -> str:
    """Search the web."""
    return f"web results for {query}"

class ResearchFindings(BaseModel):
    """Structured findings from a research task."""

    summary: str = Field(description="Summary of findings")
    confidence: float = Field(description="Confidence score from 0 to 1")
    sources: list[str] = Field(description="List of source URLs")

research_subagent = {
    "name": "researcher",
    "description": "Researches topics and returns structured findings",
    "system_prompt": "Research the given topic thoroughly. Return your findings.",
    "tools": [web_search],
    "response_format": ResearchFindings,
}

agent = create_deep_agent(
    model="openrouter:z-ai/glm-5.2",
    subagents=[research_subagent],
)

async def main():
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Research recent advances in quantum computing"}]}
    )
    return result

result = asyncio.run(main())

# The parent's ToolMessage contains JSON-serialized structured data:
# '{"summary": "...", "confidence": 0.87, "sources": ["https://..."]}'
```

```python Fireworks
import asyncio

from pydantic import BaseModel, Field

from deepagents import create_deep_agent

def web_search(query: str) -> str:
    """Search the web."""
    return f"web results for {query}"

class ResearchFindings(BaseModel):
    """Structured findings from a research task."""

    summary: str = Field(description="Summary of findings")
    confidence: float = Field(description="Confidence score from 0 to 1")
    sources: list[str] = Field(description="List of source URLs")

research_subagent = {
    "name": "researcher",
    "description": "Researches topics and returns structured findings",
    "system_prompt": "Research the given topic thoroughly. Return your findings.",
    "tools": [web_search],
    "response_format": ResearchFindings,
}

agent = create_deep_agent(
    model="fireworks:accounts/fireworks/models/glm-5p2",
    subagents=[research_subagent],
)

async def main():
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Research recent advances in quantum computing"}]}
    )
    return result

result = asyncio.run(main())

# The parent's ToolMessage contains JSON-serialized structured data:
# '{"summary": "...", "confidence": 0.87, "sources": ["https://..."]}'
```

```python Baseten
import asyncio

from pydantic import BaseModel, Field

from deepagents import create_deep_agent

def web_search(query: str) -> str:
    """Search the web."""
    return f"web results for {query}"

class ResearchFindings(BaseModel):
    """Structured findings from a research task."""

    summary: str = Field(description="Summary of findings")
    confidence: float = Field(description="Confidence score from 0 to 1")
    sources: list[str] = Field(description="List of source URLs")

research_subagent = {
    "name": "researcher",
    "description": "Researches topics and returns structured findings",
    "system_prompt": "Research the given topic thoroughly. Return your findings.",
    "tools": [web_search],
    "response_format": ResearchFindings,
}

agent = create_deep_agent(
    model="baseten:zai-org/GLM-5.2",
    subagents=[research_subagent],
)

async def main():
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Research recent advances in quantum computing"}]}
    )
    return result

result = asyncio.run(main())

# The parent's ToolMessage contains JSON-serialized structured data:
# '{"summary": "...", "confidence": 0.87, "sources": ["https://..."]}'
```

```python Ollama
import asyncio

from pydantic import BaseModel, Field

from deepagents import create_deep_agent

def web_search(query: str) -> str:
    """Search the web."""
    return f"web results for {query}"

class ResearchFindings(BaseModel):
    """Structured findings from a research task."""

    summary: str = Field(description="Summary of findings")
    confidence: float = Field(description="Confidence score from 0 to 1")
    sources: list[str] = Field(description="List of source URLs")

research_subagent = {
    "name": "researcher",
    "description": "Researches topics and returns structured findings",
    "system_prompt": "Research the given topic thoroughly. Return your findings.",
    "tools": [web_search],
    "response_format": ResearchFindings,
}

agent = create_deep_agent(
    model="ollama:north-mini-code-1.0",
    subagents=[research_subagent],
)

async def main():
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Research recent advances in quantum computing"}]}
    )
    return result

result = asyncio.run(main())

# The parent's ToolMessage contains JSON-serialized structured data:
# '{"summary": "...", "confidence": 0.87, "sources": ["https://..."]}'
```

**JavaScript / TypeScript**
**Note**
    Structured output for subagents requires `deepagents>=1.8.4`.

Pass `responseFormat` on the subagent config. When the subagent finishes, its structured response is JSON-serialized and returned as the `ToolMessage` content to the parent agent. The schema accepts anything supported by `createAgent`: Zod schemas, JSON schema objects, `toolStrategy(...)`, or `providerStrategy(...)`.

Code example: [`code/deepagents/subagents-structured-output.ts`](../code/deepagents/subagents-structured-output.ts)

```ts Google
import { z } from "zod";
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";

const webSearch = tool(
  async ({ query }: { query: string }) => `web results for ${query}`,
  {
    name: "web_search",
    description: "Search the web",
    schema: z.object({ query: z.string() }),
  },
);

const ResearchFindings = z.object({
  summary: z.string().describe("Summary of findings"),
  confidence: z.number().describe("Confidence score from 0 to 1"),
  sources: z.array(z.string()).describe("List of source URLs"),
});

const researchSubagent = {
  name: "researcher",
  description: "Researches topics and returns structured findings",
  systemPrompt: "Research the given topic thoroughly. Return your findings.",
  tools: [webSearch],
  responseFormat: ResearchFindings,
};

const agent = createDeepAgent({
  model: "google-genai:gemini-3.6-flash",
  subagents: [researchSubagent],
});

const result = await agent.invoke({
  messages: [
    { role: "user", content: "Research recent advances in quantum computing" },
  ],
});

// The parent's ToolMessage contains JSON-serialized structured data:
// '{"summary": "...", "confidence": 0.87, "sources": ["https://..."]}'
```

```ts OpenAI
import { z } from "zod";
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";

const webSearch = tool(
  async ({ query }: { query: string }) => `web results for ${query}`,
  {
    name: "web_search",
    description: "Search the web",
    schema: z.object({ query: z.string() }),
  },
);

const ResearchFindings = z.object({
  summary: z.string().describe("Summary of findings"),
  confidence: z.number().describe("Confidence score from 0 to 1"),
  sources: z.array(z.string()).describe("List of source URLs"),
});

const researchSubagent = {
  name: "researcher",
  description: "Researches topics and returns structured findings",
  systemPrompt: "Research the given topic thoroughly. Return your findings.",
  tools: [webSearch],
  responseFormat: ResearchFindings,
};

const agent = createDeepAgent({
  model: "openai:gpt-5.5",
  subagents: [researchSubagent],
});

const result = await agent.invoke({
  messages: [
    { role: "user", content: "Research recent advances in quantum computing" },
  ],
});

// The parent's ToolMessage contains JSON-serialized structured data:
// '{"summary": "...", "confidence": 0.87, "sources": ["https://..."]}'
```

```ts Anthropic
import { z } from "zod";
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";

const webSearch = tool(
  async ({ query }: { query: string }) => `web results for ${query}`,
  {
    name: "web_search",
    description: "Search the web",
    schema: z.object({ query: z.string() }),
  },
);

const ResearchFindings = z.object({
  summary: z.string().describe("Summary of findings"),
  confidence: z.number().describe("Confidence score from 0 to 1"),
  sources: z.array(z.string()).describe("List of source URLs"),
});

const researchSubagent = {
  name: "researcher",
  description: "Researches topics and returns structured findings",
  systemPrompt: "Research the given topic thoroughly. Return your findings.",
  tools: [webSearch],
  responseFormat: ResearchFindings,
};

const agent = createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  subagents: [researchSubagent],
});

const result = await agent.invoke({
  messages: [
    { role: "user", content: "Research recent advances in quantum computing" },
  ],
});

// The parent's ToolMessage contains JSON-serialized structured data:
// '{"summary": "...", "confidence": 0.87, "sources": ["https://..."]}'
```

```ts OpenRouter
import { z } from "zod";
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";

const webSearch = tool(
  async ({ query }: { query: string }) => `web results for ${query}`,
  {
    name: "web_search",
    description: "Search the web",
    schema: z.object({ query: z.string() }),
  },
);

const ResearchFindings = z.object({
  summary: z.string().describe("Summary of findings"),
  confidence: z.number().describe("Confidence score from 0 to 1"),
  sources: z.array(z.string()).describe("List of source URLs"),
});

const researchSubagent = {
  name: "researcher",
  description: "Researches topics and returns structured findings",
  systemPrompt: "Research the given topic thoroughly. Return your findings.",
  tools: [webSearch],
  responseFormat: ResearchFindings,
};

const agent = createDeepAgent({
  model: "openrouter:openrouter:z-ai/glm-5.2",
  subagents: [researchSubagent],
});

const result = await agent.invoke({
  messages: [
    { role: "user", content: "Research recent advances in quantum computing" },
  ],
});

// The parent's ToolMessage contains JSON-serialized structured data:
// '{"summary": "...", "confidence": 0.87, "sources": ["https://..."]}'
```

```ts Fireworks
import { z } from "zod";
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";

const webSearch = tool(
  async ({ query }: { query: string }) => `web results for ${query}`,
  {
    name: "web_search",
    description: "Search the web",
    schema: z.object({ query: z.string() }),
  },
);

const ResearchFindings = z.object({
  summary: z.string().describe("Summary of findings"),
  confidence: z.number().describe("Confidence score from 0 to 1"),
  sources: z.array(z.string()).describe("List of source URLs"),
});

const researchSubagent = {
  name: "researcher",
  description: "Researches topics and returns structured findings",
  systemPrompt: "Research the given topic thoroughly. Return your findings.",
  tools: [webSearch],
  responseFormat: ResearchFindings,
};

const agent = createDeepAgent({
  model: "fireworks:accounts/fireworks/models/glm-5p2",
  subagents: [researchSubagent],
});

const result = await agent.invoke({
  messages: [
    { role: "user", content: "Research recent advances in quantum computing" },
  ],
});

// The parent's ToolMessage contains JSON-serialized structured data:
// '{"summary": "...", "confidence": 0.87, "sources": ["https://..."]}'
```

```ts Baseten
import { z } from "zod";
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";

const webSearch = tool(
  async ({ query }: { query: string }) => `web results for ${query}`,
  {
    name: "web_search",
    description: "Search the web",
    schema: z.object({ query: z.string() }),
  },
);

const ResearchFindings = z.object({
  summary: z.string().describe("Summary of findings"),
  confidence: z.number().describe("Confidence score from 0 to 1"),
  sources: z.array(z.string()).describe("List of source URLs"),
});

const researchSubagent = {
  name: "researcher",
  description: "Researches topics and returns structured findings",
  systemPrompt: "Research the given topic thoroughly. Return your findings.",
  tools: [webSearch],
  responseFormat: ResearchFindings,
};

const agent = createDeepAgent({
  model: "baseten:zai-org/GLM-5.2",
  subagents: [researchSubagent],
});

const result = await agent.invoke({
  messages: [
    { role: "user", content: "Research recent advances in quantum computing" },
  ],
});

// The parent's ToolMessage contains JSON-serialized structured data:
// '{"summary": "...", "confidence": 0.87, "sources": ["https://..."]}'
```

```ts Ollama
import { z } from "zod";
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";

const webSearch = tool(
  async ({ query }: { query: string }) => `web results for ${query}`,
  {
    name: "web_search",
    description: "Search the web",
    schema: z.object({ query: z.string() }),
  },
);

const ResearchFindings = z.object({
  summary: z.string().describe("Summary of findings"),
  confidence: z.number().describe("Confidence score from 0 to 1"),
  sources: z.array(z.string()).describe("List of source URLs"),
});

const researchSubagent = {
  name: "researcher",
  description: "Researches topics and returns structured findings",
  systemPrompt: "Research the given topic thoroughly. Return your findings.",
  tools: [webSearch],
  responseFormat: ResearchFindings,
};

const agent = createDeepAgent({
  model: "ollama:north-mini-code-1.0",
  subagents: [researchSubagent],
});

const result = await agent.invoke({
  messages: [
    { role: "user", content: "Research recent advances in quantum computing" },
  ],
});

// The parent's ToolMessage contains JSON-serialized structured data:
// '{"summary": "...", "confidence": 0.87, "sources": ["https://..."]}'
```

Without `response_format`, the parent receives the subagent's last message text as-is. With it, the parent always gets valid JSON matching the schema, which is useful when the parent needs to process the result programmatically or pass it to downstream tools.

For full details on schema types and strategies (tool calling vs. provider-native), see [Structured output](../langchain/structured-output.md).

## The general-purpose subagent

In addition to any user-defined subagents, every deep agent has access to a `general-purpose` subagent at all times. This subagent:

- Uses its own default system prompt with profile overlays applied
- Has access to all the same tools
- Uses the same model (unless overridden)
- Inherits skills from the main agent (when skills are configured)

### Override the general-purpose subagent

**Python**
Include a subagent with `name="general-purpose"` in your `subagents` list to replace the default. Use this to configure a different model, tools, or system prompt for the general-purpose subagent:

Code example: [`code/deepagents/subagents-general-purpose-override.py`](../code/deepagents/subagents-general-purpose-override.py)

```python Google
from deepagents import create_deep_agent

def internet_search(query: str) -> str:
    """Run a web search."""
    return f"search results for {query}"

# Main agent uses Gemini; general-purpose subagent uses GPT
agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    tools=[internet_search],
    subagents=[
        {
            "name": "general-purpose",
            "description": "General-purpose agent for research and multi-step tasks",
            "system_prompt": "You are a general-purpose assistant.",
            "tools": [internet_search],
            "model": "openai:gpt-5.5",  # Different model for delegated tasks
        },
    ],
)
```

```python OpenAI
from deepagents import create_deep_agent

def internet_search(query: str) -> str:
    """Run a web search."""
    return f"search results for {query}"

# Main agent uses Gemini; general-purpose subagent uses GPT
agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[internet_search],
    subagents=[
        {
            "name": "general-purpose",
            "description": "General-purpose agent for research and multi-step tasks",
            "system_prompt": "You are a general-purpose assistant.",
            "tools": [internet_search],
            "model": "openai:gpt-5.5",  # Different model for delegated tasks
        },
    ],
)
```

```python Anthropic
from deepagents import create_deep_agent

def internet_search(query: str) -> str:
    """Run a web search."""
    return f"search results for {query}"

# Main agent uses Gemini; general-purpose subagent uses GPT
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[internet_search],
    subagents=[
        {
            "name": "general-purpose",
            "description": "General-purpose agent for research and multi-step tasks",
            "system_prompt": "You are a general-purpose assistant.",
            "tools": [internet_search],
            "model": "openai:gpt-5.5",  # Different model for delegated tasks
        },
    ],
)
```

```python OpenRouter
from deepagents import create_deep_agent

def internet_search(query: str) -> str:
    """Run a web search."""
    return f"search results for {query}"

# Main agent uses Gemini; general-purpose subagent uses GPT
agent = create_deep_agent(
    model="openrouter:z-ai/glm-5.2",
    tools=[internet_search],
    subagents=[
        {
            "name": "general-purpose",
            "description": "General-purpose agent for research and multi-step tasks",
            "system_prompt": "You are a general-purpose assistant.",
            "tools": [internet_search],
            "model": "openai:gpt-5.5",  # Different model for delegated tasks
        },
    ],
)
```

```python Fireworks
from deepagents import create_deep_agent

def internet_search(query: str) -> str:
    """Run a web search."""
    return f"search results for {query}"

# Main agent uses Gemini; general-purpose subagent uses GPT
agent = create_deep_agent(
    model="fireworks:accounts/fireworks/models/glm-5p2",
    tools=[internet_search],
    subagents=[
        {
            "name": "general-purpose",
            "description": "General-purpose agent for research and multi-step tasks",
            "system_prompt": "You are a general-purpose assistant.",
            "tools": [internet_search],
            "model": "openai:gpt-5.5",  # Different model for delegated tasks
        },
    ],
)
```

```python Baseten
from deepagents import create_deep_agent

def internet_search(query: str) -> str:
    """Run a web search."""
    return f"search results for {query}"

# Main agent uses Gemini; general-purpose subagent uses GPT
agent = create_deep_agent(
    model="baseten:zai-org/GLM-5.2",
    tools=[internet_search],
    subagents=[
        {
            "name": "general-purpose",
            "description": "General-purpose agent for research and multi-step tasks",
            "system_prompt": "You are a general-purpose assistant.",
            "tools": [internet_search],
            "model": "openai:gpt-5.5",  # Different model for delegated tasks
        },
    ],
)
```

```python Ollama
from deepagents import create_deep_agent

def internet_search(query: str) -> str:
    """Run a web search."""
    return f"search results for {query}"

# Main agent uses Gemini; general-purpose subagent uses GPT
agent = create_deep_agent(
    model="ollama:north-mini-code-1.0",
    tools=[internet_search],
    subagents=[
        {
            "name": "general-purpose",
            "description": "General-purpose agent for research and multi-step tasks",
            "system_prompt": "You are a general-purpose assistant.",
            "tools": [internet_search],
            "model": "openai:gpt-5.5",  # Different model for delegated tasks
        },
    ],
)
```

**JavaScript / TypeScript**
Include a subagent with `name: "general-purpose"` in your `subagents` list to replace the default. Use this to configure a different model, tools, or system prompt for the general-purpose subagent:

Code example: [`code/deepagents/subagents-general-purpose-override.ts`](../code/deepagents/subagents-general-purpose-override.ts)

```ts Google
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
```

```ts OpenAI
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
```

```ts Anthropic
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
```

```ts OpenRouter
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
```

```ts Fireworks
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
```

```ts Baseten
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
```

```ts Ollama
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
```

When you provide a subagent with the general-purpose name, the default general-purpose subagent is not added. Your spec fully replaces it.

To remove the built-in general-purpose subagent entirely instead of replacing it, set the active harness profile's general-purpose subagent `enabled` flag to `False`.

### When to use it

The general-purpose subagent is ideal for context isolation without specialized behavior. The main agent can delegate a complex multi-step task to this subagent and get a concise result back without bloat from intermediate tool calls.

**Example**
    Instead of the main agent making 10 web searches and filling its context with results, it delegates to the general-purpose subagent: `task(name="general-purpose", task="Research quantum computing trends")`. The subagent performs all the searches internally and returns only a summary.

### Skills inheritance

When configuring [skills](../deepagents/skills.md) with `create_deep_agent`:

- **General-purpose subagent**: Automatically inherits skills from the main agent
- **Custom subagents**: Do NOT inherit skills by default—use the `skills` parameter to give them their own skills

**Note**
    Only subagents configured with skills get a `SkillsMiddleware` instance—custom subagents without a `skills` parameter do not. When present, skill state is fully isolated in both directions: the parent's skills are not visible to the child, and the child's skills are not propagated back to the parent.

**Python**
Code example: [`code/deepagents/skills-subagents.py`](../code/deepagents/skills-subagents.py)

```python
from deepagents import create_deep_agent

research_subagent = {
    "name": "researcher",
    "description": "Research assistant with specialized skills",
    "system_prompt": "You are a researcher.",
    "tools": [web_search],
    "skills": ["/skills/research/", "/skills/web-search/"],  # Subagent-specific skills
}

agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    skills=["/skills/main/"],  # Main agent and GP subagent get these
    subagents=[research_subagent],  # Researcher gets only its own skills
)
```

**JavaScript / TypeScript**
Code example: [`code/deepagents/skills-subagents.ts`](../code/deepagents/skills-subagents.ts)

```ts
import { createDeepAgent } from "deepagents";

const researchSubagent = {
  name: "researcher",
  description: "Research assistant with specialized skills",
  systemPrompt: "You are a researcher.",
  tools: [webSearch],
  skills: ["/skills/research/", "/skills/web-search/"], // Subagent-specific skills
};

const agent = await createDeepAgent({
  model: "google_genai:gemini-3.6-flash",
  skills: ["/skills/main/"], // Main agent and GP subagent get these
  subagents: [researchSubagent], // Researcher gets only its own skills
});
```

## Best practices

### Write clear descriptions

The main agent uses descriptions to decide which subagent to call. Be specific:

✅ **Good:** `"Analyzes financial data and generates investment insights with confidence scores"`

❌ **Bad:** `"Does finance stuff"`

### Keep system prompts detailed

Include specific guidance on how to use tools and format outputs:

**Python**
Code example: [`code/deepagents/subagents-research-prompt.py`](../code/deepagents/subagents-research-prompt.py)

```python
research_subagent = {
    "name": "research-agent",
    "description": "Conducts in-depth research using web search and synthesizes findings",
    "system_prompt": """You are a thorough researcher. Your job is to:

    1. Break down the research question into searchable queries
    2. Use internet_search to find relevant information
    3. Synthesize findings into a comprehensive but concise summary
    4. Cite sources when making claims

    Output format:
    - Summary (2-3 paragraphs)
    - Key findings (bullet points)
    - Sources (with URLs)

    Keep your response under 500 words to maintain clean context.""",
    "tools": [internet_search],
}
```

**JavaScript / TypeScript**
Code example: [`code/deepagents/subagents-research-prompt.ts`](../code/deepagents/subagents-research-prompt.ts)

```ts
const researchSubagent = {
  name: "research-agent",
  description:
    "Conducts in-depth research using web search and synthesizes findings",
  systemPrompt: `You are a thorough researcher. Your job is to:

  1. Break down the research question into searchable queries
  2. Use internet_search to find relevant information
  3. Synthesize findings into a comprehensive but concise summary
  4. Cite sources when making claims

  Output format:
  - Summary (2-3 paragraphs)
  - Key findings (bullet points)
  - Sources (with URLs)

  Keep your response under 500 words to maintain clean context.`,
  tools: [internetSearch],
};
```

### Minimize tool sets

Only give subagents the tools they need. This improves focus and security:

**Python**
Code example: [`code/deepagents/subagents-email-tools-good.py`](../code/deepagents/subagents-email-tools-good.py)

```python
# ✅ Good: Focused tool set
email_agent = {
    "name": "email-sender",
    "tools": [send_email, validate_email],  # Only email-related
}
```

**JavaScript / TypeScript**
Code example: [`code/deepagents/subagents-email-tools-good.ts`](../code/deepagents/subagents-email-tools-good.ts)

```ts
// ✅ Good: Focused tool set
const emailAgent = {
  name: "email-sender",
  tools: [sendEmail, validateEmail], // Only email-related
};
```

**Python**
Code example: [`code/deepagents/subagents-email-tools-bad.py`](../code/deepagents/subagents-email-tools-bad.py)

```python
# ❌ Bad: Too many tools
email_agent = {
    "name": "email-sender",
    "tools": [send_email, web_search_tool, database_query, format_document],  # Unfocused
}
```

**JavaScript / TypeScript**
Code example: [`code/deepagents/subagents-email-tools-bad.ts`](../code/deepagents/subagents-email-tools-bad.ts)

```ts
// ❌ Bad: Too many tools
const emailAgentBad = {
  name: "email-sender",
  tools: [sendEmail, webSearch, databaseQuery, fileUpload], // Unfocused
};
```

### Choose models by task

Different models excel at different tasks:

**Python**
Code example: [`code/deepagents/subagents-choose-models.py`](../code/deepagents/subagents-choose-models.py)

```python
subagents = [
    {
        "name": "contract-reviewer",
        "description": "Reviews legal documents and contracts",
        "system_prompt": "You are an expert legal reviewer...",
        "tools": [read_document, analyze_contract],
        "model": "google_genai:gemini-3.6-flash",  # Large context for long documents
    },
    {
        "name": "financial-analyst",
        "description": "Analyzes financial data and market trends",
        "system_prompt": "You are an expert financial analyst...",
        "tools": [get_stock_price, analyze_fundamentals],
        "model": "openai:gpt-5.5",  # Better for numerical analysis
    },
]
```

**JavaScript / TypeScript**
Code example: [`code/deepagents/subagents-choose-models.ts`](../code/deepagents/subagents-choose-models.ts)

```ts Google
const subagents = [
  {
    name: "contract-reviewer",
    description: "Reviews legal documents and contracts",
    systemPrompt: "You are an expert legal reviewer...",
    tools: [readDocument, analyzeContract],
    model: "google-genai:gemini-3.6-flash", // Large context for long documents
  },
  {
    name: "financial-analyst",
    description: "Analyzes financial data and market trends",
    systemPrompt: "You are an expert financial analyst...",
    tools: [getStockPrice, analyzeFundamentals],
    model: "openai:gpt-5.5", // Better for numerical analysis
  },
];
```

```ts OpenAI
const subagents = [
  {
    name: "contract-reviewer",
    description: "Reviews legal documents and contracts",
    systemPrompt: "You are an expert legal reviewer...",
    tools: [readDocument, analyzeContract],
    model: "openai:gpt-5.5", // Large context for long documents
  },
  {
    name: "financial-analyst",
    description: "Analyzes financial data and market trends",
    systemPrompt: "You are an expert financial analyst...",
    tools: [getStockPrice, analyzeFundamentals],
    model: "openai:gpt-5.5", // Better for numerical analysis
  },
];
```

```ts Anthropic
const subagents = [
  {
    name: "contract-reviewer",
    description: "Reviews legal documents and contracts",
    systemPrompt: "You are an expert legal reviewer...",
    tools: [readDocument, analyzeContract],
    model: "anthropic:claude-sonnet-4-6", // Large context for long documents
  },
  {
    name: "financial-analyst",
    description: "Analyzes financial data and market trends",
    systemPrompt: "You are an expert financial analyst...",
    tools: [getStockPrice, analyzeFundamentals],
    model: "openai:gpt-5.5", // Better for numerical analysis
  },
];
```

```ts OpenRouter
const subagents = [
  {
    name: "contract-reviewer",
    description: "Reviews legal documents and contracts",
    systemPrompt: "You are an expert legal reviewer...",
    tools: [readDocument, analyzeContract],
    model: "openrouter:openrouter:z-ai/glm-5.2", // Large context for long documents
  },
  {
    name: "financial-analyst",
    description: "Analyzes financial data and market trends",
    systemPrompt: "You are an expert financial analyst...",
    tools: [getStockPrice, analyzeFundamentals],
    model: "openai:gpt-5.5", // Better for numerical analysis
  },
];
```

```ts Fireworks
const subagents = [
  {
    name: "contract-reviewer",
    description: "Reviews legal documents and contracts",
    systemPrompt: "You are an expert legal reviewer...",
    tools: [readDocument, analyzeContract],
    model: "fireworks:accounts/fireworks/models/glm-5p2", // Large context for long documents
  },
  {
    name: "financial-analyst",
    description: "Analyzes financial data and market trends",
    systemPrompt: "You are an expert financial analyst...",
    tools: [getStockPrice, analyzeFundamentals],
    model: "openai:gpt-5.5", // Better for numerical analysis
  },
];
```

```ts Baseten
const subagents = [
  {
    name: "contract-reviewer",
    description: "Reviews legal documents and contracts",
    systemPrompt: "You are an expert legal reviewer...",
    tools: [readDocument, analyzeContract],
    model: "baseten:zai-org/GLM-5.2", // Large context for long documents
  },
  {
    name: "financial-analyst",
    description: "Analyzes financial data and market trends",
    systemPrompt: "You are an expert financial analyst...",
    tools: [getStockPrice, analyzeFundamentals],
    model: "openai:gpt-5.5", // Better for numerical analysis
  },
];
```

```ts Ollama
const subagents = [
  {
    name: "contract-reviewer",
    description: "Reviews legal documents and contracts",
    systemPrompt: "You are an expert legal reviewer...",
    tools: [readDocument, analyzeContract],
    model: "ollama:north-mini-code-1.0", // Large context for long documents
  },
  {
    name: "financial-analyst",
    description: "Analyzes financial data and market trends",
    systemPrompt: "You are an expert financial analyst...",
    tools: [getStockPrice, analyzeFundamentals],
    model: "openai:gpt-5.5", // Better for numerical analysis
  },
];
```

### Return concise results

Instruct subagents to return summaries, not raw data:

**Python**
Code example: [`code/deepagents/subagents-concise-results.py`](../code/deepagents/subagents-concise-results.py)

```python
data_analyst = {
    "system_prompt": """Analyze the data and return:
    1. Key insights (3-5 bullet points)
    2. Overall confidence score
    3. Recommended next actions

    Do NOT include:
    - Raw data
    - Intermediate calculations
    - Detailed tool outputs

    Keep response under 300 words."""
}
```

**JavaScript / TypeScript**
Code example: [`code/deepagents/subagents-concise-results.ts`](../code/deepagents/subagents-concise-results.ts)

```ts
const dataAnalyst = {
  systemPrompt: `Analyze the data and return:
  1. Key insights (3-5 bullet points)
  2. Overall confidence score
  3. Recommended next actions

  Do NOT include:
  - Raw data
  - Intermediate calculations
  - Detailed tool outputs

  Keep response under 300 words.`,
};
```

## Common patterns

### Multiple specialized subagents

Create specialized subagents for different domains:

**Python**
Code example: [`code/deepagents/subagents-multiple-specialized.py`](../code/deepagents/subagents-multiple-specialized.py)

```python Google
from deepagents import create_deep_agent

subagents = [
    {
        "name": "data-collector",
        "description": "Gathers raw data from various sources",
        "system_prompt": "Collect comprehensive data on the topic",
        "tools": [web_search_tool, api_call, database_query],
    },
    {
        "name": "data-analyzer",
        "description": "Analyzes collected data for insights",
        "system_prompt": "Analyze data and extract key insights",
        "tools": [statistical_analysis],
    },
    {
        "name": "report-writer",
        "description": "Writes polished reports from analysis",
        "system_prompt": "Create professional reports from insights",
        "tools": [format_document],
    },
]

agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    system_prompt="You coordinate data analysis and reporting. Use subagents for specialized tasks.",
    subagents=subagents,
)
```

```python OpenAI
from deepagents import create_deep_agent

subagents = [
    {
        "name": "data-collector",
        "description": "Gathers raw data from various sources",
        "system_prompt": "Collect comprehensive data on the topic",
        "tools": [web_search_tool, api_call, database_query],
    },
    {
        "name": "data-analyzer",
        "description": "Analyzes collected data for insights",
        "system_prompt": "Analyze data and extract key insights",
        "tools": [statistical_analysis],
    },
    {
        "name": "report-writer",
        "description": "Writes polished reports from analysis",
        "system_prompt": "Create professional reports from insights",
        "tools": [format_document],
    },
]

agent = create_deep_agent(
    model="openai:gpt-5.5",
    system_prompt="You coordinate data analysis and reporting. Use subagents for specialized tasks.",
    subagents=subagents,
)
```

```python Anthropic
from deepagents import create_deep_agent

subagents = [
    {
        "name": "data-collector",
        "description": "Gathers raw data from various sources",
        "system_prompt": "Collect comprehensive data on the topic",
        "tools": [web_search_tool, api_call, database_query],
    },
    {
        "name": "data-analyzer",
        "description": "Analyzes collected data for insights",
        "system_prompt": "Analyze data and extract key insights",
        "tools": [statistical_analysis],
    },
    {
        "name": "report-writer",
        "description": "Writes polished reports from analysis",
        "system_prompt": "Create professional reports from insights",
        "tools": [format_document],
    },
]

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="You coordinate data analysis and reporting. Use subagents for specialized tasks.",
    subagents=subagents,
)
```

```python OpenRouter
from deepagents import create_deep_agent

subagents = [
    {
        "name": "data-collector",
        "description": "Gathers raw data from various sources",
        "system_prompt": "Collect comprehensive data on the topic",
        "tools": [web_search_tool, api_call, database_query],
    },
    {
        "name": "data-analyzer",
        "description": "Analyzes collected data for insights",
        "system_prompt": "Analyze data and extract key insights",
        "tools": [statistical_analysis],
    },
    {
        "name": "report-writer",
        "description": "Writes polished reports from analysis",
        "system_prompt": "Create professional reports from insights",
        "tools": [format_document],
    },
]

agent = create_deep_agent(
    model="openrouter:z-ai/glm-5.2",
    system_prompt="You coordinate data analysis and reporting. Use subagents for specialized tasks.",
    subagents=subagents,
)
```

```python Fireworks
from deepagents import create_deep_agent

subagents = [
    {
        "name": "data-collector",
        "description": "Gathers raw data from various sources",
        "system_prompt": "Collect comprehensive data on the topic",
        "tools": [web_search_tool, api_call, database_query],
    },
    {
        "name": "data-analyzer",
        "description": "Analyzes collected data for insights",
        "system_prompt": "Analyze data and extract key insights",
        "tools": [statistical_analysis],
    },
    {
        "name": "report-writer",
        "description": "Writes polished reports from analysis",
        "system_prompt": "Create professional reports from insights",
        "tools": [format_document],
    },
]

agent = create_deep_agent(
    model="fireworks:accounts/fireworks/models/glm-5p2",
    system_prompt="You coordinate data analysis and reporting. Use subagents for specialized tasks.",
    subagents=subagents,
)
```

```python Baseten
from deepagents import create_deep_agent

subagents = [
    {
        "name": "data-collector",
        "description": "Gathers raw data from various sources",
        "system_prompt": "Collect comprehensive data on the topic",
        "tools": [web_search_tool, api_call, database_query],
    },
    {
        "name": "data-analyzer",
        "description": "Analyzes collected data for insights",
        "system_prompt": "Analyze data and extract key insights",
        "tools": [statistical_analysis],
    },
    {
        "name": "report-writer",
        "description": "Writes polished reports from analysis",
        "system_prompt": "Create professional reports from insights",
        "tools": [format_document],
    },
]

agent = create_deep_agent(
    model="baseten:zai-org/GLM-5.2",
    system_prompt="You coordinate data analysis and reporting. Use subagents for specialized tasks.",
    subagents=subagents,
)
```

```python Ollama
from deepagents import create_deep_agent

subagents = [
    {
        "name": "data-collector",
        "description": "Gathers raw data from various sources",
        "system_prompt": "Collect comprehensive data on the topic",
        "tools": [web_search_tool, api_call, database_query],
    },
    {
        "name": "data-analyzer",
        "description": "Analyzes collected data for insights",
        "system_prompt": "Analyze data and extract key insights",
        "tools": [statistical_analysis],
    },
    {
        "name": "report-writer",
        "description": "Writes polished reports from analysis",
        "system_prompt": "Create professional reports from insights",
        "tools": [format_document],
    },
]

agent = create_deep_agent(
    model="ollama:north-mini-code-1.0",
    system_prompt="You coordinate data analysis and reporting. Use subagents for specialized tasks.",
    subagents=subagents,
)
```

**JavaScript / TypeScript**
Code example: [`code/deepagents/subagents-multiple-specialized.ts`](../code/deepagents/subagents-multiple-specialized.ts)

```ts Google
import { createDeepAgent } from "deepagents";

const subagents = [
  {
    name: "data-collector",
    description: "Gathers raw data from various sources",
    systemPrompt: "Collect comprehensive data on the topic",
    tools: [webSearch, apiCall, databaseQuery],
  },
  {
    name: "data-analyzer",
    description: "Analyzes collected data for insights",
    systemPrompt: "Analyze data and extract key insights",
    tools: [statisticalAnalysis],
  },
  {
    name: "report-writer",
    description: "Writes polished reports from analysis",
    systemPrompt: "Create professional reports from insights",
    tools: [formatDocument],
  },
];

const agent = createDeepAgent({
  model: "google-genai:gemini-3.6-flash",
  systemPrompt:
    "You coordinate data analysis and reporting. Use subagents for specialized tasks.",
  subagents: subagents,
});
```

```ts OpenAI
import { createDeepAgent } from "deepagents";

const subagents = [
  {
    name: "data-collector",
    description: "Gathers raw data from various sources",
    systemPrompt: "Collect comprehensive data on the topic",
    tools: [webSearch, apiCall, databaseQuery],
  },
  {
    name: "data-analyzer",
    description: "Analyzes collected data for insights",
    systemPrompt: "Analyze data and extract key insights",
    tools: [statisticalAnalysis],
  },
  {
    name: "report-writer",
    description: "Writes polished reports from analysis",
    systemPrompt: "Create professional reports from insights",
    tools: [formatDocument],
  },
];

const agent = createDeepAgent({
  model: "openai:gpt-5.5",
  systemPrompt:
    "You coordinate data analysis and reporting. Use subagents for specialized tasks.",
  subagents: subagents,
});
```

```ts Anthropic
import { createDeepAgent } from "deepagents";

const subagents = [
  {
    name: "data-collector",
    description: "Gathers raw data from various sources",
    systemPrompt: "Collect comprehensive data on the topic",
    tools: [webSearch, apiCall, databaseQuery],
  },
  {
    name: "data-analyzer",
    description: "Analyzes collected data for insights",
    systemPrompt: "Analyze data and extract key insights",
    tools: [statisticalAnalysis],
  },
  {
    name: "report-writer",
    description: "Writes polished reports from analysis",
    systemPrompt: "Create professional reports from insights",
    tools: [formatDocument],
  },
];

const agent = createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  systemPrompt:
    "You coordinate data analysis and reporting. Use subagents for specialized tasks.",
  subagents: subagents,
});
```

```ts OpenRouter
import { createDeepAgent } from "deepagents";

const subagents = [
  {
    name: "data-collector",
    description: "Gathers raw data from various sources",
    systemPrompt: "Collect comprehensive data on the topic",
    tools: [webSearch, apiCall, databaseQuery],
  },
  {
    name: "data-analyzer",
    description: "Analyzes collected data for insights",
    systemPrompt: "Analyze data and extract key insights",
    tools: [statisticalAnalysis],
  },
  {
    name: "report-writer",
    description: "Writes polished reports from analysis",
    systemPrompt: "Create professional reports from insights",
    tools: [formatDocument],
  },
];

const agent = createDeepAgent({
  model: "openrouter:openrouter:z-ai/glm-5.2",
  systemPrompt:
    "You coordinate data analysis and reporting. Use subagents for specialized tasks.",
  subagents: subagents,
});
```

```ts Fireworks
import { createDeepAgent } from "deepagents";

const subagents = [
  {
    name: "data-collector",
    description: "Gathers raw data from various sources",
    systemPrompt: "Collect comprehensive data on the topic",
    tools: [webSearch, apiCall, databaseQuery],
  },
  {
    name: "data-analyzer",
    description: "Analyzes collected data for insights",
    systemPrompt: "Analyze data and extract key insights",
    tools: [statisticalAnalysis],
  },
  {
    name: "report-writer",
    description: "Writes polished reports from analysis",
    systemPrompt: "Create professional reports from insights",
    tools: [formatDocument],
  },
];

const agent = createDeepAgent({
  model: "fireworks:accounts/fireworks/models/glm-5p2",
  systemPrompt:
    "You coordinate data analysis and reporting. Use subagents for specialized tasks.",
  subagents: subagents,
});
```

```ts Baseten
import { createDeepAgent } from "deepagents";

const subagents = [
  {
    name: "data-collector",
    description: "Gathers raw data from various sources",
    systemPrompt: "Collect comprehensive data on the topic",
    tools: [webSearch, apiCall, databaseQuery],
  },
  {
    name: "data-analyzer",
    description: "Analyzes collected data for insights",
    systemPrompt: "Analyze data and extract key insights",
    tools: [statisticalAnalysis],
  },
  {
    name: "report-writer",
    description: "Writes polished reports from analysis",
    systemPrompt: "Create professional reports from insights",
    tools: [formatDocument],
  },
];

const agent = createDeepAgent({
  model: "baseten:zai-org/GLM-5.2",
  systemPrompt:
    "You coordinate data analysis and reporting. Use subagents for specialized tasks.",
  subagents: subagents,
});
```

```ts Ollama
import { createDeepAgent } from "deepagents";

const subagents = [
  {
    name: "data-collector",
    description: "Gathers raw data from various sources",
    systemPrompt: "Collect comprehensive data on the topic",
    tools: [webSearch, apiCall, databaseQuery],
  },
  {
    name: "data-analyzer",
    description: "Analyzes collected data for insights",
    systemPrompt: "Analyze data and extract key insights",
    tools: [statisticalAnalysis],
  },
  {
    name: "report-writer",
    description: "Writes polished reports from analysis",
    systemPrompt: "Create professional reports from insights",
    tools: [formatDocument],
  },
];

const agent = createDeepAgent({
  model: "ollama:north-mini-code-1.0",
  systemPrompt:
    "You coordinate data analysis and reporting. Use subagents for specialized tasks.",
  subagents: subagents,
});
```

**Workflow:**
1. Main agent creates high-level plan
2. Delegates data collection to data-collector
3. Passes results to data-analyzer
4. Sends insights to report-writer
5. Compiles final output

Each subagent works with clean context focused only on its task.

## Context management

When you invoke a parent agent with runtime context, that context automatically propagates to all subagents. Each subagent run receives the same runtime context you passed on the parent `invoke` / `ainvoke` call.

This means tools running inside any subagent can access the same context values you provided to the parent:

**Python**
Code example: [`code/deepagents/subagents-context-propagation.py`](../code/deepagents/subagents-context-propagation.py)

```python Google
from dataclasses import dataclass

from deepagents import create_deep_agent
from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool

@dataclass
class Context:
    user_id: str
    session_id: str

@tool
def get_user_data(query: str, runtime: ToolRuntime[Context]) -> str:
    """Fetch data for the current user."""
    user_id = runtime.context.user_id
    return f"Data for user {user_id}: {query}"

research_subagent = {
    "name": "researcher",
    "description": "Conducts research for the current user",
    "system_prompt": "You are a research assistant.",
    "tools": [get_user_data],
}

agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    subagents=[research_subagent],
    context_schema=Context,
)

# Context flows to the researcher subagent and its tools automatically
result = agent.invoke(
    {"messages": [HumanMessage("Look up my recent activity")]},
    context=Context(user_id="user-123", session_id="abc"),
)
```

```python OpenAI
from dataclasses import dataclass

from deepagents import create_deep_agent
from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool

@dataclass
class Context:
    user_id: str
    session_id: str

@tool
def get_user_data(query: str, runtime: ToolRuntime[Context]) -> str:
    """Fetch data for the current user."""
    user_id = runtime.context.user_id
    return f"Data for user {user_id}: {query}"

research_subagent = {
    "name": "researcher",
    "description": "Conducts research for the current user",
    "system_prompt": "You are a research assistant.",
    "tools": [get_user_data],
}

agent = create_deep_agent(
    model="openai:gpt-5.5",
    subagents=[research_subagent],
    context_schema=Context,
)

# Context flows to the researcher subagent and its tools automatically
result = agent.invoke(
    {"messages": [HumanMessage("Look up my recent activity")]},
    context=Context(user_id="user-123", session_id="abc"),
)
```

```python Anthropic
from dataclasses import dataclass

from deepagents import create_deep_agent
from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool

@dataclass
class Context:
    user_id: str
    session_id: str

@tool
def get_user_data(query: str, runtime: ToolRuntime[Context]) -> str:
    """Fetch data for the current user."""
    user_id = runtime.context.user_id
    return f"Data for user {user_id}: {query}"

research_subagent = {
    "name": "researcher",
    "description": "Conducts research for the current user",
    "system_prompt": "You are a research assistant.",
    "tools": [get_user_data],
}

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    subagents=[research_subagent],
    context_schema=Context,
)

# Context flows to the researcher subagent and its tools automatically
result = agent.invoke(
    {"messages": [HumanMessage("Look up my recent activity")]},
    context=Context(user_id="user-123", session_id="abc"),
)
```

```python OpenRouter
from dataclasses import dataclass

from deepagents import create_deep_agent
from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool

@dataclass
class Context:
    user_id: str
    session_id: str

@tool
def get_user_data(query: str, runtime: ToolRuntime[Context]) -> str:
    """Fetch data for the current user."""
    user_id = runtime.context.user_id
    return f"Data for user {user_id}: {query}"

research_subagent = {
    "name": "researcher",
    "description": "Conducts research for the current user",
    "system_prompt": "You are a research assistant.",
    "tools": [get_user_data],
}

agent = create_deep_agent(
    model="openrouter:z-ai/glm-5.2",
    subagents=[research_subagent],
    context_schema=Context,
)

# Context flows to the researcher subagent and its tools automatically
result = agent.invoke(
    {"messages": [HumanMessage("Look up my recent activity")]},
    context=Context(user_id="user-123", session_id="abc"),
)
```

```python Fireworks
from dataclasses import dataclass

from deepagents import create_deep_agent
from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool

@dataclass
class Context:
    user_id: str
    session_id: str

@tool
def get_user_data(query: str, runtime: ToolRuntime[Context]) -> str:
    """Fetch data for the current user."""
    user_id = runtime.context.user_id
    return f"Data for user {user_id}: {query}"

research_subagent = {
    "name": "researcher",
    "description": "Conducts research for the current user",
    "system_prompt": "You are a research assistant.",
    "tools": [get_user_data],
}

agent = create_deep_agent(
    model="fireworks:accounts/fireworks/models/glm-5p2",
    subagents=[research_subagent],
    context_schema=Context,
)

# Context flows to the researcher subagent and its tools automatically
result = agent.invoke(
    {"messages": [HumanMessage("Look up my recent activity")]},
    context=Context(user_id="user-123", session_id="abc"),
)
```

```python Baseten
from dataclasses import dataclass

from deepagents import create_deep_agent
from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool

@dataclass
class Context:
    user_id: str
    session_id: str

@tool
def get_user_data(query: str, runtime: ToolRuntime[Context]) -> str:
    """Fetch data for the current user."""
    user_id = runtime.context.user_id
    return f"Data for user {user_id}: {query}"

research_subagent = {
    "name": "researcher",
    "description": "Conducts research for the current user",
    "system_prompt": "You are a research assistant.",
    "tools": [get_user_data],
}

agent = create_deep_agent(
    model="baseten:zai-org/GLM-5.2",
    subagents=[research_subagent],
    context_schema=Context,
)

# Context flows to the researcher subagent and its tools automatically
result = agent.invoke(
    {"messages": [HumanMessage("Look up my recent activity")]},
    context=Context(user_id="user-123", session_id="abc"),
)
```

```python Ollama
from dataclasses import dataclass

from deepagents import create_deep_agent
from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool

@dataclass
class Context:
    user_id: str
    session_id: str

@tool
def get_user_data(query: str, runtime: ToolRuntime[Context]) -> str:
    """Fetch data for the current user."""
    user_id = runtime.context.user_id
    return f"Data for user {user_id}: {query}"

research_subagent = {
    "name": "researcher",
    "description": "Conducts research for the current user",
    "system_prompt": "You are a research assistant.",
    "tools": [get_user_data],
}

agent = create_deep_agent(
    model="ollama:north-mini-code-1.0",
    subagents=[research_subagent],
    context_schema=Context,
)

# Context flows to the researcher subagent and its tools automatically
result = agent.invoke(
    {"messages": [HumanMessage("Look up my recent activity")]},
    context=Context(user_id="user-123", session_id="abc"),
)
```

**JavaScript / TypeScript**
Code example: [`code/deepagents/subagents-context-propagation.ts`](../code/deepagents/subagents-context-propagation.ts)

```ts Google
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import type { ToolRuntime } from "@langchain/core/tools";
import { z } from "zod";

const contextSchema = z.object({
  userId: z.string(),
  sessionId: z.string(),
});

const getUserData = tool(
  async (input, runtime: ToolRuntime<unknown, typeof contextSchema>) => {
    const userId = runtime.context?.userId;
    return `Data for user ${userId}: ${input.query}`;
  },
  {
    name: "get_user_data",
    description: "Fetch data for the current user",
    schema: z.object({ query: z.string() }),
  },
);

const researchSubagent = {
  name: "researcher",
  description: "Conducts research for the current user",
  systemPrompt: "You are a research assistant.",
  tools: [getUserData],
};

const agent = createDeepAgent({
  model: "google-genai:gemini-3.6-flash",
  subagents: [researchSubagent],
  contextSchema,
});

// Context flows to the researcher subagent and its tools automatically
const result = await agent.invoke(
  { messages: [new HumanMessage("Look up my recent activity")] },
  { context: { userId: "user-123", sessionId: "abc" } },
);
```

```ts OpenAI
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import type { ToolRuntime } from "@langchain/core/tools";
import { z } from "zod";

const contextSchema = z.object({
  userId: z.string(),
  sessionId: z.string(),
});

const getUserData = tool(
  async (input, runtime: ToolRuntime<unknown, typeof contextSchema>) => {
    const userId = runtime.context?.userId;
    return `Data for user ${userId}: ${input.query}`;
  },
  {
    name: "get_user_data",
    description: "Fetch data for the current user",
    schema: z.object({ query: z.string() }),
  },
);

const researchSubagent = {
  name: "researcher",
  description: "Conducts research for the current user",
  systemPrompt: "You are a research assistant.",
  tools: [getUserData],
};

const agent = createDeepAgent({
  model: "openai:gpt-5.5",
  subagents: [researchSubagent],
  contextSchema,
});

// Context flows to the researcher subagent and its tools automatically
const result = await agent.invoke(
  { messages: [new HumanMessage("Look up my recent activity")] },
  { context: { userId: "user-123", sessionId: "abc" } },
);
```

```ts Anthropic
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import type { ToolRuntime } from "@langchain/core/tools";
import { z } from "zod";

const contextSchema = z.object({
  userId: z.string(),
  sessionId: z.string(),
});

const getUserData = tool(
  async (input, runtime: ToolRuntime<unknown, typeof contextSchema>) => {
    const userId = runtime.context?.userId;
    return `Data for user ${userId}: ${input.query}`;
  },
  {
    name: "get_user_data",
    description: "Fetch data for the current user",
    schema: z.object({ query: z.string() }),
  },
);

const researchSubagent = {
  name: "researcher",
  description: "Conducts research for the current user",
  systemPrompt: "You are a research assistant.",
  tools: [getUserData],
};

const agent = createDeepAgent({
  model: "anthropic:claude-sonnet-4-6",
  subagents: [researchSubagent],
  contextSchema,
});

// Context flows to the researcher subagent and its tools automatically
const result = await agent.invoke(
  { messages: [new HumanMessage("Look up my recent activity")] },
  { context: { userId: "user-123", sessionId: "abc" } },
);
```

```ts OpenRouter
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import type { ToolRuntime } from "@langchain/core/tools";
import { z } from "zod";

const contextSchema = z.object({
  userId: z.string(),
  sessionId: z.string(),
});

const getUserData = tool(
  async (input, runtime: ToolRuntime<unknown, typeof contextSchema>) => {
    const userId = runtime.context?.userId;
    return `Data for user ${userId}: ${input.query}`;
  },
  {
    name: "get_user_data",
    description: "Fetch data for the current user",
    schema: z.object({ query: z.string() }),
  },
);

const researchSubagent = {
  name: "researcher",
  description: "Conducts research for the current user",
  systemPrompt: "You are a research assistant.",
  tools: [getUserData],
};

const agent = createDeepAgent({
  model: "openrouter:openrouter:z-ai/glm-5.2",
  subagents: [researchSubagent],
  contextSchema,
});

// Context flows to the researcher subagent and its tools automatically
const result = await agent.invoke(
  { messages: [new HumanMessage("Look up my recent activity")] },
  { context: { userId: "user-123", sessionId: "abc" } },
);
```

```ts Fireworks
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import type { ToolRuntime } from "@langchain/core/tools";
import { z } from "zod";

const contextSchema = z.object({
  userId: z.string(),
  sessionId: z.string(),
});

const getUserData = tool(
  async (input, runtime: ToolRuntime<unknown, typeof contextSchema>) => {
    const userId = runtime.context?.userId;
    return `Data for user ${userId}: ${input.query}`;
  },
  {
    name: "get_user_data",
    description: "Fetch data for the current user",
    schema: z.object({ query: z.string() }),
  },
);

const researchSubagent = {
  name: "researcher",
  description: "Conducts research for the current user",
  systemPrompt: "You are a research assistant.",
  tools: [getUserData],
};

const agent = createDeepAgent({
  model: "fireworks:accounts/fireworks/models/glm-5p2",
  subagents: [researchSubagent],
  contextSchema,
});

// Context flows to the researcher subagent and its tools automatically
const result = await agent.invoke(
  { messages: [new HumanMessage("Look up my recent activity")] },
  { context: { userId: "user-123", sessionId: "abc" } },
);
```

```ts Baseten
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import type { ToolRuntime } from "@langchain/core/tools";
import { z } from "zod";

const contextSchema = z.object({
  userId: z.string(),
  sessionId: z.string(),
});

const getUserData = tool(
  async (input, runtime: ToolRuntime<unknown, typeof contextSchema>) => {
    const userId = runtime.context?.userId;
    return `Data for user ${userId}: ${input.query}`;
  },
  {
    name: "get_user_data",
    description: "Fetch data for the current user",
    schema: z.object({ query: z.string() }),
  },
);

const researchSubagent = {
  name: "researcher",
  description: "Conducts research for the current user",
  systemPrompt: "You are a research assistant.",
  tools: [getUserData],
};

const agent = createDeepAgent({
  model: "baseten:zai-org/GLM-5.2",
  subagents: [researchSubagent],
  contextSchema,
});

// Context flows to the researcher subagent and its tools automatically
const result = await agent.invoke(
  { messages: [new HumanMessage("Look up my recent activity")] },
  { context: { userId: "user-123", sessionId: "abc" } },
);
```

```ts Ollama
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import type { ToolRuntime } from "@langchain/core/tools";
import { z } from "zod";

const contextSchema = z.object({
  userId: z.string(),
  sessionId: z.string(),
});

const getUserData = tool(
  async (input, runtime: ToolRuntime<unknown, typeof contextSchema>) => {
    const userId = runtime.context?.userId;
    return `Data for user ${userId}: ${input.query}`;
  },
  {
    name: "get_user_data",
    description: "Fetch data for the current user",
    schema: z.object({ query: z.string() }),
  },
);

const researchSubagent = {
  name: "researcher",
  description: "Conducts research for the current user",
  systemPrompt: "You are a research assistant.",
  tools: [getUserData],
};

const agent = createDeepAgent({
  model: "ollama:north-mini-code-1.0",
  subagents: [researchSubagent],
  contextSchema,
});

// Context flows to the researcher subagent and its tools automatically
const result = await agent.invoke(
  { messages: [new HumanMessage("Look up my recent activity")] },
  { context: { userId: "user-123", sessionId: "abc" } },
);
```

### Per-subagent context

All subagents receive the same parent context. To pass configuration that is specific to a particular subagent, use **namespaced keys** (prefix keys with the subagent name, for example `researcher:max_depth`) in a flat `context` mapping, **or** model those settings as separate fields on your context type:

**Python**
Code example: [`code/deepagents/subagents-per-subagent-context.py`](../code/deepagents/subagents-per-subagent-context.py)

```python Google
from dataclasses import dataclass

from deepagents import create_deep_agent
from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool

@dataclass
class Context:
    user_id: str
    researcher_max_depth: int | None = None
    fact_checker_strict_mode: bool | None = None

@tool
def verify_claim(claim: str, runtime: ToolRuntime[Context]) -> str:
    """Verify a factual claim."""
    strict_mode = runtime.context.fact_checker_strict_mode or False
    if strict_mode:
        return strict_verification(claim)
    return basic_verification(claim)

agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    subagents=[
        {
            "name": "fact-checker",
            "description": "Verifies factual claims",
            "system_prompt": "You verify claims carefully.",
            "tools": [verify_claim],
        },
    ],
    context_schema=Context,
)

result = agent.invoke(
    {"messages": [HumanMessage("Research this and verify the claims")]},
    context=Context(
        user_id="user-123",
        researcher_max_depth=3,
        fact_checker_strict_mode=True,
    ),
)
```

```python OpenAI
from dataclasses import dataclass

from deepagents import create_deep_agent
from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool

@dataclass
class Context:
    user_id: str
    researcher_max_depth: int | None = None
    fact_checker_strict_mode: bool | None = None

@tool
def verify_claim(claim: str, runtime: ToolRuntime[Context]) -> str:
    """Verify a factual claim."""
    strict_mode = runtime.context.fact_checker_strict_mode or False
    if strict_mode:
        return strict_verification(claim)
    return basic_verification(claim)

agent = create_deep_agent(
    model="openai:gpt-5.5",
    subagents=[
        {
            "name": "fact-checker",
            "description": "Verifies factual claims",
            "system_prompt": "You verify claims carefully.",
            "tools": [verify_claim],
        },
    ],
    context_schema=Context,
)

result = agent.invoke(
    {"messages": [HumanMessage("Research this and verify the claims")]},
    context=Context(
        user_id="user-123",
        researcher_max_depth=3,
        fact_checker_strict_mode=True,
    ),
)
```

```python Anthropic
from dataclasses import dataclass

from deepagents import create_deep_agent
from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool

@dataclass
class Context:
    user_id: str
    researcher_max_depth: int | None = None
    fact_checker_strict_mode: bool | None = None

@tool
def verify_claim(claim: str, runtime: ToolRuntime[Context]) -> str:
    """Verify a factual claim."""
    strict_mode = runtime.context.fact_checker_strict_mode or False
    if strict_mode:
        return strict_verification(claim)
    return basic_verification(claim)

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    subagents=[
        {
            "name": "fact-checker",
            "description": "Verifies factual claims",
            "system_prompt": "You verify claims carefully.",
            "tools": [verify_claim],
        },
    ],
    context_schema=Context,
)

result = agent.invoke(
    {"messages": [HumanMessage("Research this and verify the claims")]},
    context=Context(
        user_id="user-123",
        researcher_max_depth=3,
        fact_checker_strict_mode=True,
    ),
)
```

```python OpenRouter
from dataclasses import dataclass

from deepagents import create_deep_agent
from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool

@dataclass
class Context:
    user_id: str
    researcher_max_depth: int | None = None
    fact_checker_strict_mode: bool | None = None

@tool
def verify_claim(claim: str, runtime: ToolRuntime[Context]) -> str:
    """Verify a factual claim."""
    strict_mode = runtime.context.fact_checker_strict_mode or False
    if strict_mode:
        return strict_verification(claim)
    return basic_verification(claim)

agent = create_deep_agent(
    model="openrouter:z-ai/glm-5.2",
    subagents=[
        {
            "name": "fact-checker",
            "description": "Verifies factual claims",
            "system_prompt": "You verify claims carefully.",
            "tools": [verify_claim],
        },
    ],
    context_schema=Context,
)

result = agent.invoke(
    {"messages": [HumanMessage("Research this and verify the claims")]},
    context=Context(
        user_id="user-123",
        researcher_max_depth=3,
        fact_checker_strict_mode=True,
    ),
)
```

```python Fireworks
from dataclasses import dataclass

from deepagents import create_deep_agent
from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool

@dataclass
class Context:
    user_id: str
    researcher_max_depth: int | None = None
    fact_checker_strict_mode: bool | None = None

@tool
def verify_claim(claim: str, runtime: ToolRuntime[Context]) -> str:
    """Verify a factual claim."""
    strict_mode = runtime.context.fact_checker_strict_mode or False
    if strict_mode:
        return strict_verification(claim)
    return basic_verification(claim)

agent = create_deep_agent(
    model="fireworks:accounts/fireworks/models/glm-5p2",
    subagents=[
        {
            "name": "fact-checker",
            "description": "Verifies factual claims",
            "system_prompt": "You verify claims carefully.",
            "tools": [verify_claim],
        },
    ],
    context_schema=Context,
)

result = agent.invoke(
    {"messages": [HumanMessage("Research this and verify the claims")]},
    context=Context(
        user_id="user-123",
        researcher_max_depth=3,
        fact_checker_strict_mode=True,
    ),
)
```

```python Baseten
from dataclasses import dataclass

from deepagents import create_deep_agent
from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool

@dataclass
class Context:
    user_id: str
    researcher_max_depth: int | None = None
    fact_checker_strict_mode: bool | None = None

@tool
def verify_claim(claim: str, runtime: ToolRuntime[Context]) -> str:
    """Verify a factual claim."""
    strict_mode = runtime.context.fact_checker_strict_mode or False
    if strict_mode:
        return strict_verification(claim)
    return basic_verification(claim)

agent = create_deep_agent(
    model="baseten:zai-org/GLM-5.2",
    subagents=[
        {
            "name": "fact-checker",
            "description": "Verifies factual claims",
            "system_prompt": "You verify claims carefully.",
            "tools": [verify_claim],
        },
    ],
    context_schema=Context,
)

result = agent.invoke(
    {"messages": [HumanMessage("Research this and verify the claims")]},
    context=Context(
        user_id="user-123",
        researcher_max_depth=3,
        fact_checker_strict_mode=True,
    ),
)
```

```python Ollama
from dataclasses import dataclass

from deepagents import create_deep_agent
from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool

@dataclass
class Context:
    user_id: str
    researcher_max_depth: int | None = None
    fact_checker_strict_mode: bool | None = None

@tool
def verify_claim(claim: str, runtime: ToolRuntime[Context]) -> str:
    """Verify a factual claim."""
    strict_mode = runtime.context.fact_checker_strict_mode or False
    if strict_mode:
        return strict_verification(claim)
    return basic_verification(claim)

agent = create_deep_agent(
    model="ollama:north-mini-code-1.0",
    subagents=[
        {
            "name": "fact-checker",
            "description": "Verifies factual claims",
            "system_prompt": "You verify claims carefully.",
            "tools": [verify_claim],
        },
    ],
    context_schema=Context,
)

result = agent.invoke(
    {"messages": [HumanMessage("Research this and verify the claims")]},
    context=Context(
        user_id="user-123",
        researcher_max_depth=3,
        fact_checker_strict_mode=True,
    ),
)
```

**JavaScript / TypeScript**
Code example: [`code/deepagents/subagents-per-subagent-context.ts`](../code/deepagents/subagents-per-subagent-context.ts)

```ts
import { tool } from "langchain";
import type { ToolRuntime } from "@langchain/core/tools";
import { z } from "zod";

const contextSchema = z.object({
  userId: z.string(),
  researcherMaxDepth: z.number().optional(),
  factCheckerStrictMode: z.boolean().optional(),
});

const verifyClaim = tool(
  async (input, runtime: ToolRuntime<unknown, typeof contextSchema>) => {
    const strictMode = runtime.context?.factCheckerStrictMode ?? false;
    if (strictMode) {
      return strictVerification(input.claim);
    }
    return basicVerification(input.claim);
  },
  {
    name: "verify_claim",
    description: "Verify a factual claim",
    schema: z.object({ claim: z.string() }),
  },
);
```

### Identifying which subagent called a tool

When the same tool is shared between the parent and multiple subagents, you can use the `lc_agent_name` metadata (the same value used in [streaming](#streaming)) to determine which agent initiated the call:

**Python**
Code example: [`code/deepagents/subagents-shared-lookup.py`](../code/deepagents/subagents-shared-lookup.py)

```python

# :snippet-start: subagents-shared-lookup-py
from langchain.tools import ToolRuntime, tool

@tool
def shared_lookup(query: str, runtime: ToolRuntime) -> str:
    """Look up information."""
    agent_name = runtime.config.get("metadata", {}).get("lc_agent_name")
    if agent_name == "fact-checker":
        return strict_lookup(query)
    return general_lookup(query)
```

**JavaScript / TypeScript**
Code example: [`code/deepagents/subagents-shared-lookup.ts`](../code/deepagents/subagents-shared-lookup.ts)

```ts
import { tool } from "langchain";
import type { ToolRuntime } from "@langchain/core/tools";
import { z } from "zod";

const sharedLookup = tool(
  async (input, runtime: ToolRuntime) => {
    const agentName = runtime.config?.metadata?.lc_agent_name;
    if (agentName === "fact-checker") {
      return strictLookup(input.query);
    }
    return generalLookup(input.query);
  },
  {
    name: "shared_lookup",
    description: "Look up information from various sources",
    schema: z.object({ query: z.string() }),
  },
);
```

You can combine both patterns—read agent-specific settings from `runtime.context` and read `lc_agent_name` from `runtime.config` metadata when branching tool behavior.

**Python**
Code example: [`code/deepagents/subagents-flexible-search.py`](../code/deepagents/subagents-flexible-search.py)

```python
from dataclasses import dataclass

from langchain.tools import ToolRuntime, tool

@dataclass
class Context:
    user_id: str
    researcher_max_depth: int | None = None
    fact_checker_strict_mode: bool | None = None

@tool
def flexible_search(query: str, runtime: ToolRuntime[Context]) -> str:
    """Search with agent-specific settings."""
    agent_name = runtime.config.get("metadata", {}).get("lc_agent_name", "unknown")
    ctx = runtime.context
    if agent_name == "researcher":
        max_results = ctx.researcher_max_depth or 5
    else:
        max_results = 5
    include_raw = False

    return perform_search(query, max_results=max_results, include_raw=include_raw)
```

**JavaScript / TypeScript**
Code example: [`code/deepagents/subagents-flexible-search.ts`](../code/deepagents/subagents-flexible-search.ts)

```ts
import { tool } from "langchain";
import type { ToolRuntime } from "@langchain/core/tools";
import { z } from "zod";

const contextSchema = z.object({
  userId: z.string(),
  researcherMaxDepth: z.number().optional(),
  factCheckerStrictMode: z.boolean().optional(),
});

const flexibleSearch = tool(
  async (input, runtime: ToolRuntime<unknown, typeof contextSchema>) => {
    const agentName = runtime.config?.metadata?.lc_agent_name ?? "unknown";
    const ctx = runtime.context;
    const maxResults =
      agentName === "researcher" ? (ctx?.researcherMaxDepth ?? 5) : 5;
    const includeRaw = false;

    return performSearch(input.query, { maxResults, includeRaw });
  },
  {
    name: "flexible_search",
    description: "Search with agent-specific settings",
    schema: z.object({ query: z.string() }),
  },
);
```

## Troubleshooting

### Subagent not being called

**Problem**: Main agent tries to do work itself instead of delegating.

**Solutions**:

1. **Make descriptions more specific:**

**Python**
   Code example: [`code/deepagents/subagents-troubleshooting-description-good.py`](../code/deepagents/subagents-troubleshooting-description-good.py)

```python
# ✅ Good
good_subagent = {
    "name": "research-specialist",
    "description": "Conducts in-depth research on specific topics using web search. Use when you need detailed information that requires multiple searches.",
}
```

**JavaScript / TypeScript**
   Code example: [`code/deepagents/subagents-troubleshooting-description-good.ts`](../code/deepagents/subagents-troubleshooting-description-good.ts)

```ts
// ✅ Good
const goodDescription = {
  name: "research-specialist",
  description:
    "Conducts in-depth research on specific topics using web search. Use when you need detailed information that requires multiple searches.",
};
```

**Python**
   Code example: [`code/deepagents/subagents-troubleshooting-description-bad.py`](../code/deepagents/subagents-troubleshooting-description-bad.py)

```python
# ❌ Bad
bad_subagent = {
    "name": "helper",
    "description": "helps with stuff",
}
```

**JavaScript / TypeScript**
   Code example: [`code/deepagents/subagents-troubleshooting-description-bad.ts`](../code/deepagents/subagents-troubleshooting-description-bad.ts)

```ts
// ❌ Bad
const badDescription = {
  name: "helper",
  description: "helps with stuff",
};
```

2. **Instruct main agent to delegate:**

**Python**
   Code example: [`code/deepagents/subagents-troubleshooting-delegate.py`](../code/deepagents/subagents-troubleshooting-delegate.py)

```python Google
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    system_prompt="""...your instructions...

    IMPORTANT: For complex tasks, delegate to your subagents using the task() tool.
    This keeps your context clean and improves results.""",
    subagents=[
        {
            "name": "research-agent",
            "description": "Conducts research",
            "system_prompt": "You are a researcher.",
        },
    ],
)
```

```python OpenAI
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="openai:gpt-5.5",
    system_prompt="""...your instructions...

    IMPORTANT: For complex tasks, delegate to your subagents using the task() tool.
    This keeps your context clean and improves results.""",
    subagents=[
        {
            "name": "research-agent",
            "description": "Conducts research",
            "system_prompt": "You are a researcher.",
        },
    ],
)
```

```python Anthropic
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="""...your instructions...

    IMPORTANT: For complex tasks, delegate to your subagents using the task() tool.
    This keeps your context clean and improves results.""",
    subagents=[
        {
            "name": "research-agent",
            "description": "Conducts research",
            "system_prompt": "You are a researcher.",
        },
    ],
)
```

```python OpenRouter
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="openrouter:z-ai/glm-5.2",
    system_prompt="""...your instructions...

    IMPORTANT: For complex tasks, delegate to your subagents using the task() tool.
    This keeps your context clean and improves results.""",
    subagents=[
        {
            "name": "research-agent",
            "description": "Conducts research",
            "system_prompt": "You are a researcher.",
        },
    ],
)
```

```python Fireworks
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="fireworks:accounts/fireworks/models/glm-5p2",
    system_prompt="""...your instructions...

    IMPORTANT: For complex tasks, delegate to your subagents using the task() tool.
    This keeps your context clean and improves results.""",
    subagents=[
        {
            "name": "research-agent",
            "description": "Conducts research",
            "system_prompt": "You are a researcher.",
        },
    ],
)
```

```python Baseten
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="baseten:zai-org/GLM-5.2",
    system_prompt="""...your instructions...

    IMPORTANT: For complex tasks, delegate to your subagents using the task() tool.
    This keeps your context clean and improves results.""",
    subagents=[
        {
            "name": "research-agent",
            "description": "Conducts research",
            "system_prompt": "You are a researcher.",
        },
    ],
)
```

```python Ollama
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="ollama:north-mini-code-1.0",
    system_prompt="""...your instructions...

    IMPORTANT: For complex tasks, delegate to your subagents using the task() tool.
    This keeps your context clean and improves results.""",
    subagents=[
        {
            "name": "research-agent",
            "description": "Conducts research",
            "system_prompt": "You are a researcher.",
        },
    ],
)
```

**JavaScript / TypeScript**
   Code example: [`code/deepagents/subagents-troubleshooting-delegate.ts`](../code/deepagents/subagents-troubleshooting-delegate.ts)

```ts
import { createDeepAgent } from "deepagents";

const agent = createDeepAgent({
  systemPrompt: `...your instructions...

  IMPORTANT: For complex tasks, delegate to your subagents using the task() tool.
  This keeps your context clean and improves results.`,
  subagents: [
    {
      name: "research-agent",
      description: "Conducts research",
      systemPrompt: "You are a researcher.",
    },
  ],
});
```

### Context still getting bloated

**Problem**: Context fills up despite using subagents.

**Solutions**:

1. **Instruct subagent to return concise results:**

**Python**
   Code example: [`code/deepagents/subagents-troubleshooting-concise-prompt.py`](../code/deepagents/subagents-troubleshooting-concise-prompt.py)

```python
system_prompt = """...

IMPORTANT: Return only the essential summary.
Do NOT include raw data, intermediate search results, or detailed tool outputs.
Your response should be under 500 words."""
```

**JavaScript / TypeScript**
   Code example: [`code/deepagents/subagents-troubleshooting-concise-prompt.ts`](../code/deepagents/subagents-troubleshooting-concise-prompt.ts)

```ts
const systemPrompt = `...

IMPORTANT: Return only the essential summary.
Do NOT include raw data, intermediate search results, or detailed tool outputs.
Your response should be under 500 words.`;
```

2. **Use filesystem for large data:**

**Python**
   Code example: [`code/deepagents/subagents-troubleshooting-filesystem-prompt.py`](../code/deepagents/subagents-troubleshooting-filesystem-prompt.py)

```python
system_prompt = """When you gather large amounts of data:
1. Save raw data to /data/raw_results.txt
2. Process and analyze the data
3. Return only the analysis summary

This keeps context clean."""
```

**JavaScript / TypeScript**
   Code example: [`code/deepagents/subagents-troubleshooting-filesystem-prompt.ts`](../code/deepagents/subagents-troubleshooting-filesystem-prompt.ts)

```ts
const filesystemPrompt = `When you gather large amounts of data:
1. Save raw data to /data/raw_results.txt
2. Process and analyze the data
3. Return only the analysis summary

This keeps context clean.`;
```

### Wrong subagent being selected

**Problem**: Main agent calls inappropriate subagent for the task.

**Solution**: Differentiate subagents clearly in descriptions:

**Python**
Code example: [`code/deepagents/subagents-troubleshooting-differentiate.py`](../code/deepagents/subagents-troubleshooting-differentiate.py)

```python
subagents = [
    {
        "name": "quick-researcher",
        "description": "For simple, quick research questions that need 1-2 searches. Use when you need basic facts or definitions.",
        "system_prompt": "You are the quick-researcher subagent.",
    },
    {
        "name": "deep-researcher",
        "description": "For complex, in-depth research requiring multiple searches, synthesis, and analysis. Use for comprehensive reports.",
        "system_prompt": "You are the deep-researcher subagent.",
    },
]
```

**JavaScript / TypeScript**
Code example: [`code/deepagents/subagents-troubleshooting-differentiate.ts`](../code/deepagents/subagents-troubleshooting-differentiate.ts)

```ts
const subagents = [
  {
    name: "quick-researcher",
    description:
      "For simple, quick research questions that need 1-2 searches. Use when you need basic facts or definitions.",
    systemPrompt: "You are the quick-researcher subagent.",
  },
  {
    name: "deep-researcher",
    description:
      "For complex, in-depth research requiring multiple searches, synthesis, and analysis. Use for comprehensive reports.",
    systemPrompt: "You are the deep-researcher subagent.",
  },
];
```
