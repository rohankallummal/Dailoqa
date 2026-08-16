---
type: Documentation Page
title: Prebuilt middleware
description: Prebuilt middleware for common agent use cases
product: langchain
resource: /docs/langchain/prebuilt-middleware
source: /oss/langchain/middleware/built-in
tags:
  - langchain
  - middleware
timestamp: 2026-08-13T13:42:01Z
code_examples:
  - ../code/langchain/rubric-configure.py
---

# Prebuilt middleware

LangChain and [Deep Agents](../deepagents/overview.md) provide prebuilt middleware for common use cases. Each middleware is production-ready and configurable for your specific needs.

## Provider-agnostic middleware

The following middleware work with any LLM provider:

**Python**

| Middleware | Description |
|------------|-------------|
| [Summarization](#summarization) | Automatically summarize conversation history when approaching token limits. |
| [Human-in-the-loop](#human-in-the-loop) | Pause execution for human approval of tool calls. |
| [Model call limit](#model-call-limit) | Limit the number of model calls to prevent excessive costs. |
| [Tool call limit](#tool-call-limit) | Control tool execution by limiting call counts. |
| [Model fallback](#model-fallback) | Automatically fallback to alternative models when primary fails. |
| [PII detection](#pii-detection) | Detect and handle Personally Identifiable Information (PII). |
| [To-do list](#to-do-list) | Equip agents with task planning and tracking capabilities. |
| [LLM tool selector](#llm-tool-selector) | Use an LLM to select relevant tools before calling main model. |
| [Tool error](#tool-error) | Catch tool execution exceptions and convert them to error messages for the model. |
| [Tool retry](#tool-retry) | Automatically retry failed tool calls with exponential backoff. |
| [Model retry](#model-retry) | Automatically retry failed model calls with exponential backoff. |
| [LLM tool emulator](#llm-tool-emulator) | Emulate tool execution using an LLM for testing purposes. |
| [Context editing](#context-editing) | Manage conversation context by trimming or clearing tool uses. |
| [Provider tool search](#provider-tool-search) | Defer tools behind providers' server-side tool search, surfacing them on demand. |
| [Shell tool](#shell-tool) | Expose a persistent shell session to agents for command execution. |
| [File search](#file-search) | Provide Glob and Grep search tools over filesystem files. |
| [Filesystem](#filesystem-middleware) | Provide agents with a filesystem for storing context and long-term memories. |
| [Subagent](#subagent) | Add the ability to spawn subagents. |
| [Rubric grading (Beta)](#rubric-grading) | Apply LLM-as-a-judge grading so agents self-evaluate and iterate until a rubric is satisfied. |

**JavaScript / TypeScript**

| Middleware | Description |
|------------|-------------|
| [Summarization](#summarization) | Automatically summarize conversation history when approaching token limits. |
| [Human-in-the-loop](#human-in-the-loop) | Pause execution for human approval of tool calls. |
| [Model call limit](#model-call-limit) | Limit the number of model calls to prevent excessive costs. |
| [Tool call limit](#tool-call-limit) | Control tool execution by limiting call counts. |
| [Model fallback](#model-fallback) | Automatically fallback to alternative models when primary fails. |
| [PII detection](#pii-detection) | Detect and handle Personally Identifiable Information (PII). |
| [To-do list](#to-do-list) | Equip agents with task planning and tracking capabilities. |
| [LLM tool selector](#llm-tool-selector) | Use an LLM to select relevant tools before calling main model. |
| [Tool retry](#tool-retry) | Automatically retry failed tool calls with exponential backoff. |
| [Model retry](#model-retry) | Automatically retry failed model calls with exponential backoff. |
| [LLM tool emulator](#llm-tool-emulator) | Emulate tool execution using an LLM for testing purposes. |
| [Context editing](#context-editing) | Manage conversation context by trimming or clearing tool uses. |
| [Provider tool search](#provider-tool-search) | Defer tools behind providers' server-side tool search, surfacing them on demand. |
| [Filesystem](#filesystem-middleware) | Provide agents with a filesystem for storing context and long-term memories. |
| [Subagent middleware](#subagent) | Add the ability to spawn subagents. |

### Summarization

Automatically summarize conversation history when approaching token limits, preserving recent messages while compressing older context. Summarization is useful for the following:
- Long-running conversations that exceed context windows.
- Multi-turn dialogues with extensive history.
- Applications where preserving full conversation context matters.

**Note**
    Summarization is text-oriented context compression. It does not resize, downsample, or otherwise compress image/audio/video payloads. Recent messages retained by `keep` still include their original multimodal blocks, while older multimodal messages that are summarized are represented only by the generated text summary. For image-heavy applications, store media in a filesystem or object store and pass URLs or file references through message history.

**Python**
**API reference:** `SummarizationMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[your_weather_tool, your_calculator_tool],
    middleware=[
        SummarizationMiddleware(
            model="gpt-5.4-mini",
            trigger=("tokens", 4000),
            keep=("messages", 20),
        ),
    ],
)
```

**JavaScript / TypeScript**
```typescript
import { createAgent, summarizationMiddleware } from "langchain";

const agent = createAgent({
  model: "gpt-5.5",
  tools: [weatherTool, calculatorTool],
  middleware: [
    summarizationMiddleware({
      model: "gpt-5.4-mini",
      trigger: { tokens: 4000 },
      keep: { messages: 20 },
    }),
  ],
});
```

**Configuration options**

**Python**

**Tip**
    The `fraction` conditions for `trigger` and `keep` (shown below) rely on a chat model's [profile data](../langchain/models.md#model-profiles) if using `langchain>=1.1`. If data are not available, use another condition or specify manually:

```python
from langchain.chat_models import init_chat_model

custom_profile = {
    "max_input_tokens": 100_000,
    # ...
}
model = init_chat_model("gpt-5.5", profile=custom_profile)
```

- **`model`** (string | BaseChatModel, required)
    Model for generating summaries. Can be a model identifier string (e.g., `'openai:gpt-5.4-mini'`) or a `BaseChatModel` instance. See `init_chat_model`[init_chat_model(model)] for more information.

- **`trigger`** (ContextSize | TriggerClause | list[ContextSize | TriggerClause] | None)
    Condition(s) for triggering summarization. Can be:

    - A single `ContextSize` tuple (the specified threshold must be met)
    - A single `TriggerClause` dict (all specified thresholds must be met - AND logic)
    - A list mixing either form (any item must be met - OR logic)

    Supported thresholds are:

    - `fraction` (float): Fraction of model's context size (0-1)
    - `tokens` (int): Absolute token count
    - `messages` (int): Message count

    A `ContextSize` tuple expresses exactly one threshold. A `TriggerClause` dict can include one or more thresholds, e.g. `{"tokens": 4000, "messages": 10}`, and all thresholds in the dict must be met (AND).

    Each `TriggerClause` dict must specify at least one threshold. If `trigger` is not provided, summarization will not trigger automatically.

    See the API reference for `ContextSize` and `TriggerClause` for more information.

- **`keep`** (ContextSize)
    How much context to preserve after summarization. Specify exactly one of:

    - `fraction` (float): Fraction of model's context size to keep (0-1)
    - `tokens` (int): Absolute token count to keep
    - `messages` (int): Number of recent messages to keep

    See the API reference for `ContextSize` for more information.

- **`token_counter`** (function)
    Custom token counting function. Defaults to character-based counting.

- **`summary_prompt`** (string)
    Custom prompt template for summarization. Uses built-in template if not specified. The template should include `{messages}` placeholder where conversation history will be inserted.

- **`trim_tokens_to_summarize`** (number)
    Maximum number of tokens to include when generating the summary. Messages will be trimmed to fit this limit before summarization.

- **`summary_prefix`** (string)
    **Deprecated:** Use `summary_prompt` to provide the full prompt instead.

- **`max_tokens_before_summary`** (number)
    **Deprecated:** Use `trigger: ("tokens", value)` instead. Token threshold for triggering summarization.

- **`messages_to_keep`** (number)
    **Deprecated:** Use `keep: ("messages", value)` instead. Recent messages to preserve.

**JavaScript / TypeScript**
**Tip**
    The `fraction` conditions for `trigger` and `keep` (shown below) rely on a chat model's [profile data](../langchain/models.md#model-profiles) if using `langchain@1.1.0`. If data are not available, use another condition or specify manually:
```typescript
const customProfile: ModelProfile = {
    maxInputTokens: 100_000,
    // ...
}
model = await initChatModel("...", {
    profile: customProfile,
});
```

- **`model`** (string | BaseChatModel, required)
    Model for generating summaries. Can be a model identifier string (e.g., `'openai:gpt-5.4-mini'`) or a `BaseChatModel` instance.

- **`trigger`** (object | object[])
    Conditions for triggering summarization. Can be:

    - A single condition object (all properties must be met - AND logic)
    - An array of condition objects (any condition must be met - OR logic)

    Each condition can include:
    - `fraction` (number): Fraction of model's context size (0-1)
    - `tokens` (number): Absolute token count
    - `messages` (number): Message count

    At least one property must be specified per condition. If not provided, summarization will not trigger automatically.

- **`keep`** (object)
    How much context to preserve after summarization. Specify exactly one of:

    - `fraction` (number): Fraction of model's context size to keep (0-1)
    - `tokens` (number): Absolute token count to keep
    - `messages` (number): Number of recent messages to keep

- **`tokenCounter`** (function)
    Custom token counting function. Defaults to character-based counting.

- **`summaryPrompt`** (string)
    Custom prompt template for summarization. Uses built-in template if not specified. The template should include `{messages}` placeholder where conversation history will be inserted.

- **`trimTokensToSummarize`** (number)
    Maximum number of tokens to include when generating the summary. Messages will be trimmed to fit this limit before summarization.

- **`summaryPrefix`** (string)
    Prefix to add to the summary message. If not provided, a default prefix is used.

- **`maxTokensBeforeSummary`** (number)
    **Deprecated:** Use `trigger: { tokens: value }` instead. Token threshold for triggering summarization.

- **`messagesToKeep`** (number)
    **Deprecated:** Use `keep: { messages: value }` instead. Recent messages to preserve.

**Full example**

The summarization middleware monitors message token counts and automatically summarizes older messages when thresholds are reached.

**Trigger conditions** control when summarization runs:
- A single threshold triggers when that threshold is met
- A trigger clause with multiple thresholds triggers only when all thresholds are met (AND logic)
- A list of trigger conditions triggers when any item is met (OR logic)
- Each threshold can use `fraction` (of model's context size), `tokens` (absolute count), or `messages` (message count)

**Keep condition** control how much context to preserve (specify exactly one):
- `fraction` - Fraction of model's context size to keep
- `tokens` - Absolute token count to keep
- `messages` - Number of recent messages to keep

**Python**
```python
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

# Single condition: trigger if tokens >= 4000
agent = create_agent(
    model="gpt-5.5",
    tools=[your_weather_tool, your_calculator_tool],
    middleware=[
        SummarizationMiddleware(
            model="gpt-5.4-mini",
            trigger=("tokens", 4000),
            keep=("messages", 20),
        ),
    ],
)

# Multiple conditions: trigger if number of tokens >= 3000 OR messages >= 6
agent2 = create_agent(
    model="gpt-5.5",
    tools=[your_weather_tool, your_calculator_tool],
    middleware=[
        SummarizationMiddleware(
            model="gpt-5.4-mini",
            trigger=[
                ("tokens", 3000),
                ("messages", 6),
            ],
            keep=("messages", 20),
        ),
    ],
)

# AND logic: trigger only when tokens >= 4000 AND messages >= 10
agent3 = create_agent(
    model="gpt-5.5",
    tools=[your_weather_tool, your_calculator_tool],
    middleware=[
        SummarizationMiddleware(
            model="gpt-5.4-mini",
            trigger={"tokens": 4000, "messages": 10},
            keep=("messages", 20),
        ),
    ],
)

# Combine AND and OR: trigger if (tokens >= 5000 AND messages >= 3)
# OR (tokens >= 3000 AND messages >= 6)
agent4 = create_agent(
    model="gpt-5.5",
    tools=[your_weather_tool, your_calculator_tool],
    middleware=[
        SummarizationMiddleware(
            model="gpt-5.4-mini",
            trigger=[
                {"tokens": 5000, "messages": 3},
                {"tokens": 3000, "messages": 6},
            ],
            keep=("messages", 20),
        ),
    ],
)

# Using fractional limits
agent5 = create_agent(
    model="gpt-5.5",
    tools=[your_weather_tool, your_calculator_tool],
    middleware=[
        SummarizationMiddleware(
            model="gpt-5.4-mini",
            trigger=("fraction", 0.8),
            keep=("fraction", 0.3),
        ),
    ],
)
```

**JavaScript / TypeScript**
```typescript
import { createAgent, summarizationMiddleware } from "langchain";

// Single condition
const agent = createAgent({
  model: "gpt-5.5",
  tools: [weatherTool, calculatorTool],
  middleware: [
    summarizationMiddleware({
      model: "gpt-5.4-mini",
      trigger: { tokens: 4000, messages: 10 },
      keep: { messages: 20 },
    }),
  ],
});

// Multiple conditions
const agent2 = createAgent({
  model: "gpt-5.5",
  tools: [weatherTool, calculatorTool],
  middleware: [
    summarizationMiddleware({
      model: "gpt-5.4-mini",
      trigger: [
        { tokens: 3000, messages: 6 },
      ],
      keep: { messages: 20 },
    }),
  ],
});

// Using fractional limits
const agent3 = createAgent({
  model: "gpt-5.5",
  tools: [weatherTool, calculatorTool],
  middleware: [
    summarizationMiddleware({
      model: "gpt-5.4-mini",
      trigger: { fraction: 0.8 },
      keep: { fraction: 0.3 },
    }),
  ],
});
```

### Human-in-the-loop

Pause agent execution for human approval, editing, or rejection of tool calls before they execute. Human-in-the-loop is useful for the following:

- High-stakes operations requiring human approval (e.g. database writes, financial transactions).
- Compliance workflows where human oversight is mandatory.
- Long-running conversations where human feedback guides the agent.

**Python**
**API reference:** `HumanInTheLoopMiddleware`

**Warning**
    Human-in-the-loop middleware requires a [checkpointer](../langgraph/checkpoints.md#checkpoints) to maintain state across interruptions.

**Python**
```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver

def your_read_email_tool(email_id: str) -> str:
    """Mock function to read an email by its ID."""
    return f"Email content for ID: {email_id}"

def your_send_email_tool(recipient: str, subject: str, body: str) -> str:
    """Mock function to send an email."""
    return f"Email sent to {recipient} with subject '{subject}'"

agent = create_agent(
    model="gpt-5.5",
    tools=[your_read_email_tool, your_send_email_tool],
    checkpointer=InMemorySaver(),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "your_send_email_tool": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                },
                "your_read_email_tool": False,
            }
        ),
    ],
)
```

**JavaScript / TypeScript**
```typescript
import { createAgent, humanInTheLoopMiddleware } from "langchain";

function readEmailTool(emailId: string): string {
  /** Mock function to read an email by its ID. */
  return `Email content for ID: ${emailId}`;
}

function sendEmailTool(recipient: string, subject: string, body: string): string {
  /** Mock function to send an email. */
  return `Email sent to ${recipient} with subject '${subject}'`;
}

const agent = createAgent({
  model: "gpt-5.5",
  tools: [readEmailTool, sendEmailTool],
  middleware: [
    humanInTheLoopMiddleware({
      interruptOn: {
        sendEmailTool: {
          allowedDecisions: ["approve", "edit", "reject"],
        },
        readEmailTool: false,
      }
    })
  ]
});
```

**Tip**
    For complete examples, configuration options, and integration patterns, see the Human-in-the-loop documentation.

### Model call limit

Limit the number of model calls to prevent infinite loops or excessive costs. Model call limit is useful for the following:

- Preventing runaway agents from making too many API calls.
- Enforcing cost controls on production deployments.
- Testing agent behavior within specific call budgets.

**Python**
**API reference:** `ModelCallLimitMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model="gpt-5.5",
    checkpointer=InMemorySaver(),  # Required for thread limiting
    tools=[],
    middleware=[
        ModelCallLimitMiddleware(
            thread_limit=10,
            run_limit=5,
            exit_behavior="end",
        ),
    ],
)
```

**JavaScript / TypeScript**
```typescript
import { createAgent, modelCallLimitMiddleware } from "langchain";
import { MemorySaver } from "@langchain/langgraph";

const agent = createAgent({
  model: "gpt-5.5",
  checkpointer: new MemorySaver(), // Required for thread limiting
  tools: [],
  middleware: [
    modelCallLimitMiddleware({
      threadLimit: 10,
      runLimit: 5,
      exitBehavior: "end",
    }),
  ],
});
```

**Configuration options**

**Python**
- **`thread_limit`** (number)
    Maximum model calls across all runs in a thread. Defaults to no limit.

- **`run_limit`** (number)
    Maximum model calls per single invocation. Defaults to no limit.

- **`exit_behavior`** (string)
    Behavior when limit is reached. Options: `'end'` (graceful termination) or `'error'` (raise exception)

**JavaScript / TypeScript**
- **`threadLimit`** (number)
    Maximum model calls across all runs in a thread. Defaults to no limit.

- **`runLimit`** (number)
    Maximum model calls per single invocation. Defaults to no limit.

- **`exitBehavior`** (string)
    Behavior when limit is reached. Options: `'end'` (graceful termination) or `'error'` (throw exception)

### Tool call limit

Control agent execution by limiting the number of tool calls, either globally across all tools or for specific tools. Tool call limits are useful for the following:

- Preventing excessive calls to expensive external APIs.
- Limiting web searches or database queries.
- Enforcing rate limits on specific tool usage.
- Protecting against runaway agent loops.

**Python**
**API reference:** `ToolCallLimitMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[search_tool, database_tool],
    middleware=[
        # Global limit
        ToolCallLimitMiddleware(thread_limit=20, run_limit=10),
        # Tool-specific limit
        ToolCallLimitMiddleware(
            tool_name="search",
            thread_limit=5,
            run_limit=3,
        ),
    ],
)
```

**JavaScript / TypeScript**
```typescript
import { createAgent, toolCallLimitMiddleware } from "langchain";

const agent = createAgent({
  model: "gpt-5.5",
  tools: [searchTool, databaseTool],
  middleware: [
    toolCallLimitMiddleware({ threadLimit: 20, runLimit: 10 }),
    toolCallLimitMiddleware({
      toolName: "search",
      threadLimit: 5,
      runLimit: 3,
    }),
  ],
});
```

**Configuration options**

**Python**
- **`tool_name`** (string)
    Name of specific tool to limit. If not provided, limits apply to **all tools globally**.

- **`thread_limit`** (number)
    Maximum tool calls across all runs in a thread (conversation). Persists across multiple invocations with the same thread ID. Requires a checkpointer to maintain state. `None` means no thread limit.

- **`run_limit`** (number)
    Maximum tool calls per single invocation (one user message → response cycle). Resets with each new user message. `None` means no run limit.

    **Note:** At least one of `thread_limit` or `run_limit` must be specified.

- **`exit_behavior`** (string)
    Behavior when limit is reached:

    - `'continue'` (default) - Block exceeded tool calls with error messages, let other tools and the model continue. The model decides when to end based on the error messages.
    - `'error'` - Raise a `ToolCallLimitExceededError` exception, stopping execution immediately
    - `'end'` - Stop execution immediately with a `ToolMessage` and AI message for the exceeded tool call. Only works when limiting a single tool; raises `NotImplementedError` if other tools have pending calls.

**JavaScript / TypeScript**
- **`toolName`** (string)
    Name of specific tool to limit. If not provided, limits apply to **all tools globally**.

- **`threadLimit`** (number)
    Maximum tool calls across all runs in a thread (conversation). Persists across multiple invocations with the same thread ID. Requires a checkpointer to maintain state. `undefined` means no thread limit.

- **`runLimit`** (number)
    Maximum tool calls per single invocation (one user message → response cycle). Resets with each new user message. `undefined` means no run limit.

    **Note:** At least one of `threadLimit` or `runLimit` must be specified.

- **`exitBehavior`** (string)
    Behavior when limit is reached:

    - `'continue'` (default) - Block exceeded tool calls with error messages, let other tools and the model continue. The model decides when to end based on the error messages.
    - `'error'` - Throw a `ToolCallLimitExceededError` exception, stopping execution immediately
    - `'end'` - Stop execution immediately with a ToolMessage and AI message for the exceeded tool call. Only works when limiting a single tool; throws error if other tools have pending calls.

**Full example**

Specify limits with:
- **Thread limit** - Max calls across all runs in a conversation (requires checkpointer)
- **Run limit** - Max calls per single invocation (resets each turn)

Exit behaviors:
- `'continue'` (default) - Block exceeded calls with error messages, agent continues
- `'error'` - Raise exception immediately
- `'end'` - Stop with ToolMessage + AI message (single-tool scenarios only)

**Python**
```python
from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware

global_limiter = ToolCallLimitMiddleware(thread_limit=20, run_limit=10)
search_limiter = ToolCallLimitMiddleware(tool_name="search", thread_limit=5, run_limit=3)
database_limiter = ToolCallLimitMiddleware(tool_name="query_database", thread_limit=10)
strict_limiter = ToolCallLimitMiddleware(tool_name="scrape_webpage", run_limit=2, exit_behavior="error")

agent = create_agent(
    model="gpt-5.5",
    tools=[search_tool, database_tool, scraper_tool],
    middleware=[global_limiter, search_limiter, database_limiter, strict_limiter],
)
```

**JavaScript / TypeScript**
```typescript
import { createAgent, toolCallLimitMiddleware } from "langchain";

const globalLimiter = toolCallLimitMiddleware({ threadLimit: 20, runLimit: 10 });
const searchLimiter = toolCallLimitMiddleware({ toolName: "search", threadLimit: 5, runLimit: 3 });
const databaseLimiter = toolCallLimitMiddleware({ toolName: "query_database", threadLimit: 10 });
const strictLimiter = toolCallLimitMiddleware({ toolName: "scrape_webpage", runLimit: 2, exitBehavior: "error" });

const agent = createAgent({
  model: "gpt-5.5",
  tools: [searchTool, databaseTool, scraperTool],
  middleware: [globalLimiter, searchLimiter, databaseLimiter, strictLimiter],
});
```

### Model fallback

Automatically fallback to alternative models when the primary model fails. Model fallback is useful for the following:

- Building resilient agents that handle model outages.
- Cost optimization by falling back to cheaper models.
- Provider redundancy across OpenAI, Anthropic, etc.

**Python**
**API reference:** `ModelFallbackMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[],
    middleware=[
        ModelFallbackMiddleware(
            "gpt-5.4-mini",
            "claude-3-5-sonnet-20241022",
        ),
    ],
)
```

**JavaScript / TypeScript**
```typescript
import { createAgent, modelFallbackMiddleware } from "langchain";

const agent = createAgent({
  model: "gpt-5.5",
  tools: [],
  middleware: [
    modelFallbackMiddleware(
      "gpt-5.4-mini",
      "claude-3-5-sonnet-20241022"
    ),
  ],
});
```

**Configuration options**

**Python**
- **`first_model`** (string | BaseChatModel, required)
    First fallback model to try when the primary model fails. Can be a model identifier string (e.g., `'openai:gpt-5.4-mini'`) or a `BaseChatModel` instance.

- **`*additional_models`** (string | BaseChatModel)
    Additional fallback models to try in order if previous models fail

**JavaScript / TypeScript**
The middleware accepts a variable number of string arguments representing fallback models in order:

- **`...models`** (string[], required)
  One or more fallback model strings to try in order when the primary model fails

```typescript
modelFallbackMiddleware(
  "first-fallback-model",
  "second-fallback-model",
  // ... more models
)
```

### PII detection

Detect and handle Personally Identifiable Information (PII) in conversations using configurable strategies. PII detection is useful for the following:

- Healthcare and financial applications with compliance requirements.
- Customer service agents that need to sanitize logs.
- Any application handling sensitive user data.

**Python**
**Note**
With `apply_to_output=True`, `PIIMiddleware` also redacts streamed wire output—text deltas, tool-call args, tool outputs, and state snapshots—via a registered stream transformer. Requires `langchain>=1.3.2`. See Register transformers on middleware.

**API reference:** `PIIMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[],
    middleware=[
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
    ],
)
```

**JavaScript / TypeScript**
```typescript
import { createAgent, piiMiddleware } from "langchain";

const agent = createAgent({
  model: "gpt-5.5",
  tools: [],
  middleware: [
    piiMiddleware("email", { strategy: "redact", applyToInput: true }),
    piiMiddleware("credit_card", { strategy: "mask", applyToInput: true }),
  ],
});
```

#### Custom PII types

You can create custom PII types by providing a `detector` parameter. This allows you to detect patterns specific to your use case beyond the built-in types.

**Three ways to create custom detectors:**

1. **Regex pattern string** - Simple pattern matching
**JavaScript / TypeScript**
1. **RegExp object** - More control over regex flags

1. **Custom function** - Complex detection logic with validation

**Python**
```python
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
import re

# Method 1: Regex pattern string
agent1 = create_agent(
    model="gpt-5.5",
    tools=[],
    middleware=[
        PIIMiddleware(
            "api_key",
            detector=r"sk-[a-zA-Z0-9]{32}",
            strategy="block",
        ),
    ],
)

# Method 2: Compiled regex pattern
agent2 = create_agent(
    model="gpt-5.5",
    tools=[],
    middleware=[
        PIIMiddleware(
            "phone_number",
            detector=re.compile(r"\+?\d{1,3}[\s.-]?\d{3,4}[\s.-]?\d{4}"),
            strategy="mask",
        ),
    ],
)

# Method 3: Custom detector function
def detect_ssn(content: str) -> list[dict[str, str | int]]:
    """Detect SSN with validation.

    Returns a list of dictionaries with 'text', 'start', and 'end' keys.
    """
    import re
    matches = []
    pattern = r"\d{3}-\d{2}-\d{4}"
    for match in re.finditer(pattern, content):
        ssn = match.group(0)
        # Validate: first 3 digits shouldn't be 000, 666, or 900-999
        first_three = int(ssn[:3])
        if first_three not in [0, 666] and not (900 <= first_three <= 999):
            matches.append({
                "text": ssn,
                "start": match.start(),
                "end": match.end(),
            })
    return matches

agent3 = create_agent(
    model="gpt-5.5",
    tools=[],
    middleware=[
        PIIMiddleware(
            "ssn",
            detector=detect_ssn,
            strategy="hash",
        ),
    ],
)
```

**JavaScript / TypeScript**
```typescript
import { createAgent, piiMiddleware, type PIIMatch } from "langchain";

// Method 1: Regex pattern string
const agent1 = createAgent({
  model: "gpt-5.5",
  tools: [],
  middleware: [
    piiMiddleware("api_key", {
      detector: "sk-[a-zA-Z0-9]{32}",
      strategy: "block",
    }),
  ],
});

// Method 2: RegExp object
const agent2 = createAgent({
  model: "gpt-5.5",
  tools: [],
  middleware: [
    piiMiddleware("phone_number", {
      detector: /\+?\d{1,3}[\s.-]?\d{3,4}[\s.-]?\d{4}/,
      strategy: "mask",
    }),
  ],
});

// Method 3: Custom detector function
function detectSSN(content: string): PIIMatch[] {
  const matches: PIIMatch[] = [];
  const pattern = /\d{3}-\d{2}-\d{4}/g;
  let match: RegExpExecArray | null;

  while ((match = pattern.exec(content)) !== null) {
    const ssn = match[0];
    // Validate: first 3 digits shouldn't be 000, 666, or 900-999
    const firstThree = parseInt(ssn.substring(0, 3), 10);
    if (firstThree !== 0 && firstThree !== 666 && !(firstThree >= 900 && firstThree <= 999)) {
      matches.push({
        text: ssn,
        start: match.index ?? 0,
        end: (match.index ?? 0) + ssn.length,
      });
    }
  }
  return matches;
}

const agent3 = createAgent({
  model: "gpt-5.5",
  tools: [],
  middleware: [
    piiMiddleware("ssn", {
      detector: detectSSN,
      strategy: "hash",
    }),
  ],
});
```

**Custom detector function signature:**

The detector function must accept a string (content) and return matches:

**Python**
Returns a list of dictionaries with `text`, `start`, and `end` keys:
```python
def detector(content: str) -> list[dict[str, str | int]]:
    return [
        {"text": "matched_text", "start": 0, "end": 12},
        # ... more matches
    ]
```

**JavaScript / TypeScript**
Returns an array of `PIIMatch` objects:
```typescript
interface PIIMatch {
  text: string;    // The matched text
  start: number;   // Start index in content
  end: number;      // End index in content
}

function detector(content: string): PIIMatch[] {
  return [
    { text: "matched_text", start: 0, end: 12 },
    // ... more matches
  ];
}
```

**Tip**
    For custom detectors:

    - Use regex strings for simple patterns
    - Use RegExp objects when you need flags (e.g., case-insensitive matching)
    - Use custom functions when you need validation logic beyond pattern matching
    - Custom functions give you full control over detection logic and can implement complex validation rules

**Configuration options**

**Python**
- **`pii_type`** (string, required)
    Type of PII to detect. Can be a built-in type (`email`, `credit_card`, `ip`, `mac_address`, `url`) or a custom type name.

- **`strategy`** (string)
    How to handle detected PII. Options:

    - `'block'` - Raise exception when detected
    - `'redact'` - Replace with `[REDACTED_{PII_TYPE}]`
    - `'mask'` - Partially mask (e.g., `****-****-****-1234`)
    - `'hash'` - Replace with deterministic hash

- **`detector`** (function | regex)
    Custom detector function or regex pattern. If not provided, uses built-in detector for the PII type.

- **`apply_to_input`** (boolean)
    Check user messages before model call

- **`apply_to_output`** (boolean)
    Check AI messages after model call. With `langchain>=1.3.2`, also redacts streamed wire output (text deltas, tool-call args, tool outputs, state snapshots) via a registered stream transformer. See event streaming.

- **`apply_to_tool_results`** (boolean)
    Check tool result messages after execution

**JavaScript / TypeScript**
- **`piiType`** (string, required)
    Type of PII to detect. Can be a built-in type (`email`, `credit_card`, `ip`, `mac_address`, `url`) or a custom type name.

- **`strategy`** (string)
    How to handle detected PII. Options:

    - `'block'` - Throw error when detected
    - `'redact'` - Replace with `[REDACTED_TYPE]`
    - `'mask'` - Partially mask (e.g., `****-****-****-1234`)
    - `'hash'` - Replace with deterministic hash (e.g., `<email_hash:a1b2c3d4>`)

- **`detector`** (RegExp | string | function)
    Custom detector. Can be:

    - `RegExp` - Regex pattern for matching
    - `string` - Regex pattern string (e.g., `"sk-[a-zA-Z0-9]{32}"`)
    - `function` - Custom detector function `(content: string) => PIIMatch[]`

    If not provided, uses built-in detector for the PII type.

- **`applyToInput`** (boolean)
    Check user messages before model call

- **`applyToOutput`** (boolean)
    Check AI messages after model call

- **`applyToToolResults`** (boolean)
    Check tool result messages after execution

### To-do list

Equip agents with task planning and tracking capabilities for complex multi-step tasks. To-do lists are useful for the following:

- Complex multi-step tasks requiring coordination across multiple tools.
- Long-running operations where progress visibility is important.

**Note**
    This middleware automatically provides agents with a `write_todos` tool and system prompts to guide effective task planning.

**Python**
**API reference:** `TodoListMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[read_file, write_file, run_tests],
    middleware=[TodoListMiddleware()],
)
```

**JavaScript / TypeScript**
```typescript
import { createAgent, todoListMiddleware } from "langchain";

const agent = createAgent({
  model: "gpt-5.5",
  tools: [readFile, writeFile, runTests],
  middleware: [todoListMiddleware()],
});
```

**Configuration options**

**Python**
- **`system_prompt`** (string)
    Custom system prompt for guiding todo usage. Uses built-in prompt if not specified.

- **`tool_description`** (string)
    Custom description for the `write_todos` tool. Uses built-in description if not specified.

**JavaScript / TypeScript**
No configuration options available (uses defaults).

### LLM tool selector

Use an LLM to intelligently select relevant tools before calling the main model. LLM tool selectors are useful for the following:

- Agents with many tools (10+) where most aren't relevant per query.
- Reducing token usage by filtering irrelevant tools.
- Improving model focus and accuracy.

This middleware uses structured output to ask an LLM which tools are most relevant for the current query. The structured output schema defines the available tool names and descriptions. Model providers often add this structured output information to the system prompt behind the scenes.

**Python**
**API reference:** `LLMToolSelectorMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolSelectorMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[tool1, tool2, tool3, tool4, tool5, ...],
    middleware=[
        LLMToolSelectorMiddleware(
            model="gpt-5.4-mini",
            max_tools=3,
            always_include=["search"],
        ),
    ],
)
```

**JavaScript / TypeScript**
```typescript
import { createAgent, llmToolSelectorMiddleware } from "langchain";

const agent = createAgent({
  model: "gpt-5.5",
  tools: [tool1, tool2, tool3, tool4, tool5, ...],
  middleware: [
    llmToolSelectorMiddleware({
      model: "gpt-5.4-mini",
      maxTools: 3,
      alwaysInclude: ["search"],
    }),
  ],
});
```

**Configuration options**

**Python**
- **`model`** (string | BaseChatModel)
    Model for tool selection. Can be a model identifier string (e.g., `'openai:gpt-5.4-mini'`) or a `BaseChatModel` instance. See `init_chat_model`[init_chat_model(model)] for more information.

    Defaults to the agent's main model.

- **`system_prompt`** (string)
    Instructions for the selection model. Uses built-in prompt if not specified.

- **`max_tools`** (number)
    Maximum number of tools to select. If the model selects more, only the first max_tools will be used. No limit if not specified.

- **`always_include`** (list[string])
    Tool names to always include regardless of selection. These do not count against the max_tools limit.

**JavaScript / TypeScript**
- **`model`** (string | BaseChatModel)
    Model for tool selection. Can be a model identifier string (e.g., `'openai:gpt-5.4-mini'`) or a `BaseChatModel` instance. Defaults to the agent's main model.

- **`systemPrompt`** (string)
    Instructions for the selection model. Uses built-in prompt if not specified.

- **`maxTools`** (number)
    Maximum number of tools to select. If the model selects more, only the first maxTools will be used. No limit if not specified.

- **`alwaysInclude`** (string[])
    Tool names to always include regardless of selection. These do not count against the maxTools limit.

### Tool error

**Python**

Catch exceptions raised during tool execution and convert them into error `ToolMessage`s that the model can see and recover from, instead of halting the agent run. Tool error is useful for the following:

- Letting the model retry a failed tool call with corrected arguments.
- Surfacing controlled, sanitized error messages instead of raw exception details.
- Preventing unexpected tool exceptions from crashing the agent.

**Note**
Tool error middleware does not automatically retry failed calls. For retries, compose with [Tool retry](#tool-retry) middleware placed *inner* (earlier in the `middleware` list) and configured with `on_failure="error"` so that exceptions reach the tool error middleware. See the [full example](#tool-error-full-example) below.

**API reference:** `ToolErrorMiddleware`

**Note**
`ToolErrorMiddleware` requires `langchain>=1.3.14`.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ToolErrorMiddleware

def on_error(exc: Exception, request: ToolCallRequest) -> str | None:
    if isinstance(exc, ValueError):
        return f"`{request.tool_call['name']}` failed with {type(exc).__name__}."
    # propagate everything else

agent = create_agent(
    model="gpt-5.5",
    tools=[your_tools],
    middleware=[ToolErrorMiddleware(on_error)],
)
```

**Configuration options**

- **`on_error`** (Callable[[Exception, ToolCallRequest], str | list[ContentBlock] | None])
    Sync handler called for each exception raised by tool execution. Return content (a `str` or list of content blocks) to convert the exception into a `ToolMessage(status="error")`. Return `None` or omit a return statement to let the exception propagate. Used on the sync path and, unless `aon_error` is given, on the async path.

- **`aon_error`** (Callable[[Exception, ToolCallRequest], Awaitable[str | list[ContentBlock] | None]])
    Optional async handler, used on the async execution path. Falls back to `on_error` when not provided.

- **`tools`** (list[BaseTool | str])
    Optional list of tools or tool names to apply error handling to. If `None`, applies to all tools.

**Tool error full example**

The `on_error` handler receives the exception and the `ToolCallRequest` (which includes the tool call dict with name, args, and call ID). Return `None` for exceptions you do not want to handle, and they will propagate normally.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ToolErrorMiddleware, ToolRetryMiddleware

def on_error(exc: Exception, request: ToolCallRequest) -> str | None:
    # Surface ValueError to the model so it can correct the input
    if isinstance(exc, ValueError):
        return f"`{request.tool_call['name']}` failed: {type(exc).__name__}. Fix the input and retry."
    # Let all other exceptions propagate (halts the run)
    return None

# Async-only usage
async def aon_error(exc: Exception, request: ToolCallRequest) -> str | None:
    if isinstance(exc, ConnectionError):
        return f"Tool `{request.tool_call['name']}` encountered a connection error."
    return None

agent = create_agent(
    model="gpt-5.5",
    tools=[search_tool, database_tool],
    middleware=[
        # Place retry inner so exceptions reach ToolErrorMiddleware after retries are exhausted
        ToolRetryMiddleware(max_retries=3, on_failure="error"),
        ToolErrorMiddleware(on_error=on_error, tools=["search_tool"]),
    ],
)

# Async-only: pass aon_error alone (do not pass on_error)
async_agent = create_agent(
    model="gpt-5.5",
    tools=[api_tool],
    middleware=[ToolErrorMiddleware(aon_error=aon_error)],
)
```

**Note**
Prefer returning content that names the exception type over the raw exception message, which may carry sensitive or internal detail. The `on_error` handler controls disclosure: the raw exception message is never sent to the model unless you choose to include it.

### Tool retry

Automatically retry failed tool calls with configurable exponential backoff. Tool retry is useful for the following:

- Handling transient failures in external API calls.
- Improving reliability of network-dependent tools.
- Building resilient agents that gracefully handle temporary errors.

**Python**
**API reference:** `ToolRetryMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ToolRetryMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[search_tool, database_tool],
    middleware=[
        ToolRetryMiddleware(
            max_retries=3,
            backoff_factor=2.0,
            initial_delay=1.0,
        ),
    ],
)
```

**JavaScript / TypeScript**
**API reference:** `toolRetryMiddleware`

```typescript
import { createAgent, toolRetryMiddleware } from "langchain";

const agent = createAgent({
  model: "gpt-5.5",
  tools: [searchTool, databaseTool],
  middleware: [
    toolRetryMiddleware({
      maxRetries: 3,
      backoffFactor: 2.0,
      initialDelayMs: 1000,
    }),
  ],
});
```

**Configuration options**

**Python**
- **`max_retries`** (number)
    Maximum number of retry attempts after the initial call (3 total attempts with default)

- **`tools`** (list[BaseTool | str])
    Optional list of tools or tool names to apply retry logic to. If `None`, applies to all tools.

- **`retry_on`** (tuple[type[Exception], ...] | callable)
    Either a tuple of exception types to retry on, or a callable that takes an exception and returns `True` if it should be retried. By default, all exceptions are retried. Exceptions that do not match propagate immediately and are not handled by `on_failure`.

- **`on_failure`** (string | callable)
    Behavior when all retries are exhausted. Options:
    - `'continue'` (default) - Return a `ToolMessage` with error details, allowing the LLM to handle the failure
    - `'error'` - Re-raise the exception, stopping agent execution
    - Custom callable - Function that takes the exception and returns a string for the `ToolMessage` content

    **Deprecated values:** `'return_message'` (use `'continue'` instead) and `'raise'` (use `'error'` instead).

- **`backoff_factor`** (number)
    Multiplier for exponential backoff. Each retry waits `initial_delay * (backoff_factor ** retry_number)` seconds. Set to `0.0` for constant delay.

- **`initial_delay`** (number)
    Initial delay in seconds before first retry

- **`max_delay`** (number)
    Maximum delay in seconds between retries (caps exponential backoff growth)

- **`jitter`** (boolean)
    Whether to add random jitter (`±25%`) to delay to avoid thundering herd

**JavaScript / TypeScript**
- **`maxRetries`** (number)
    Maximum number of retry attempts after the initial call (3 total attempts with default). Must be >= 0.

- **`tools`** ((ClientTool | ServerTool | string)[])
    Optional array of tools or tool names to apply retry logic to. Can be a list of `BaseTool` instances or tool name strings. If `undefined`, applies to all tools.

 boolean) | (new (...args: any[]) => Error)[]" default="() => true">
    Either an array of error constructors to retry on, or a function that takes an error and returns `true` if it should be retried. Default is to retry on all errors.

 string)" default="continue">
    Behavior when all retries are exhausted. Options:
    - `'continue'` (default) - Return a `ToolMessage` with error details, allowing the LLM to handle the failure and potentially recover
    - `'error'` - Re-raise the exception, stopping agent execution
    - Custom function - Function that takes the exception and returns a string for the `ToolMessage` content, allowing custom error formatting

    **Deprecated values:** `'raise'` (use `'error'` instead) and `'return_message'` (use `'continue'` instead). These deprecated values still work but will show a warning.

- **`backoffFactor`** (number)
    Multiplier for exponential backoff. Each retry waits `initialDelayMs * (backoffFactor ** retryNumber)` milliseconds. Set to `0.0` for constant delay. Must be >= 0.

- **`initialDelayMs`** (number)
    Initial delay in milliseconds before first retry. Must be >= 0.

- **`maxDelayMs`** (number)
    Maximum delay in milliseconds between retries (caps exponential backoff growth). Must be >= 0.

- **`jitter`** (boolean)
    Whether to add random jitter (`±25%`) to delay to avoid thundering herd

**Full example**

The middleware automatically retries failed tool calls with exponential backoff.

**Python**
**Key configuration:**
- `max_retries` - Number of retry attempts (default: 2)
- `backoff_factor` - Multiplier for exponential backoff (default: 2.0)
- `initial_delay` - Starting delay in seconds (default: 1.0)
- `max_delay` - Cap on delay growth (default: 60.0)
- `jitter` - Add random variation (default: True)

**Failure handling:**
- `on_failure='continue'` (default) - Return error message
- `on_failure='error'` - Re-raise exception
- Custom function - Function returning error message

**JavaScript / TypeScript**
**Key configuration:**
- `maxRetries` - Number of retry attempts (default: 2)
- `backoffFactor` - Multiplier for exponential backoff (default: 2.0)
- `initialDelayMs` - Starting delay in milliseconds (default: 1000ms)
- `maxDelayMs` - Cap on delay growth (default: 60000ms)
- `jitter` - Add random variation (default: true)

**Failure handling:**
- `onFailure: "continue"` (default) - Return error message
- `onFailure: "error"` - Re-raise exception
- Custom function - Function returning error message

**Python**
```python
from langchain.agents import create_agent
from langchain.agents.middleware import ToolRetryMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[search_tool, database_tool, api_tool],
    middleware=[
        ToolRetryMiddleware(
            max_retries=3,
            backoff_factor=2.0,
            initial_delay=1.0,
            max_delay=60.0,
            jitter=True,
            tools=["api_tool"],
            retry_on=(ConnectionError, TimeoutError),
            on_failure="continue",
        ),
    ],
)
```

**JavaScript / TypeScript**
```typescript
import { createAgent, toolRetryMiddleware } from "langchain";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

// Basic usage with default settings (2 retries, exponential backoff)
const agent = createAgent({
  model: "gpt-5.5",
  tools: [searchTool, databaseTool],
  middleware: [toolRetryMiddleware()],
});

// Retry specific exceptions only
const retry = toolRetryMiddleware({
  maxRetries: 4,
  retryOn: [TimeoutError, NetworkError],
  backoffFactor: 1.5,
});

// Custom exception filtering
function shouldRetry(error: Error): boolean {
  // Only retry on 5xx errors
  if (error.name === "HTTPError" && "statusCode" in error) {
    const statusCode = (error as any).statusCode;
    return 500 <= statusCode && statusCode < 600;
  }
  return false;
}

const retryWithFilter = toolRetryMiddleware({
  maxRetries: 3,
  retryOn: shouldRetry,
});

// Apply to specific tools with custom error handling
const formatError = (error: Error) =>
  "Database temporarily unavailable. Please try again later.";

const retrySpecificTools = toolRetryMiddleware({
  maxRetries: 4,
  tools: ["search_database"],
  onFailure: formatError,
});

// Apply to specific tools using BaseTool instances
const searchDatabase = tool(
  async ({ query }) => {
    // Search implementation
    return results;
  },
  {
    name: "search_database",
    description: "Search the database",
    schema: z.object({ query: z.string() }),
  }
);

const retryWithToolInstance = toolRetryMiddleware({
  maxRetries: 4,
  tools: [searchDatabase], // Pass BaseTool instance
});

// Constant backoff (no exponential growth)
const constantBackoff = toolRetryMiddleware({
  maxRetries: 5,
  backoffFactor: 0.0, // No exponential growth
  initialDelayMs: 2000, // Always wait 2 seconds
});

// Raise exception on failure
const strictRetry = toolRetryMiddleware({
  maxRetries: 2,
  onFailure: "error", // Re-raise exception instead of returning message
});
```

### Model retry

Automatically retry failed model calls with configurable exponential backoff. Model retry is useful for the following:

- Handling transient failures in model API calls.
- Improving reliability of network-dependent model requests.
- Building resilient agents that gracefully handle temporary model errors.

**Python**
**API reference:** `ModelRetryMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRetryMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[search_tool, database_tool],
    middleware=[
        ModelRetryMiddleware(
            max_retries=3,
            backoff_factor=2.0,
            initial_delay=1.0,
        ),
    ],
)
```

**JavaScript / TypeScript**
**API reference:** `modelRetryMiddleware`

```typescript
import { createAgent, modelRetryMiddleware } from "langchain";

const agent = createAgent({
  model: "gpt-5.5",
  tools: [searchTool, databaseTool],
  middleware: [
    modelRetryMiddleware({
      maxRetries: 3,
      backoffFactor: 2.0,
      initialDelayMs: 1000,
    }),
  ],
});
```

**Configuration options**

**Python**
- **`max_retries`** (number)
    Maximum number of retry attempts after the initial call (3 total attempts with default)

- **`retry_on`** (tuple[type[Exception], ...] | callable)
    Either a tuple of exception types to retry on, or a callable that takes an exception and returns `True` if it should be retried.

- **`on_failure`** (string | callable)
    Behavior when all retries are exhausted. Options:
    - `'continue'` (default) - Return an `AIMessage` with error details, allowing the agent to potentially handle the failure gracefully
    - `'error'` - Re-raise the exception (stops agent execution)
    - Custom callable - Function that takes the exception and returns a string for the `AIMessage` content

- **`backoff_factor`** (number)
    Multiplier for exponential backoff. Each retry waits `initial_delay * (backoff_factor ** retry_number)` seconds. Set to `0.0` for constant delay.

- **`initial_delay`** (number)
    Initial delay in seconds before first retry

- **`max_delay`** (number)
    Maximum delay in seconds between retries (caps exponential backoff growth)

- **`jitter`** (boolean)
    Whether to add random jitter (`±25%`) to delay to avoid thundering herd

**JavaScript / TypeScript**
- **`maxRetries`** (number)
    Maximum number of retry attempts after the initial call (3 total attempts with default). Must be >= 0.

 boolean) | (new (...args: any[]) => Error)[]" default="() => true">
    Either an array of error constructors to retry on, or a function that takes an error and returns `true` if it should be retried. Default is to retry on all errors.

 string)" default="continue">
    Behavior when all retries are exhausted. Options:
    - `'continue'` (default) - Return an `AIMessage` with error details, allowing the agent to potentially handle the failure gracefully
    - `'error'` - Re-raise the exception, stopping agent execution
    - Custom function - Function that takes the exception and returns a string for the `AIMessage` content, allowing custom error formatting

- **`backoffFactor`** (number)
    Multiplier for exponential backoff. Each retry waits `initialDelayMs * (backoffFactor ** retryNumber)` milliseconds. Set to `0.0` for constant delay. Must be >= 0.

- **`initialDelayMs`** (number)
    Initial delay in milliseconds before first retry. Must be >= 0.

- **`maxDelayMs`** (number)
    Maximum delay in milliseconds between retries (caps exponential backoff growth). Must be >= 0.

- **`jitter`** (boolean)
    Whether to add random jitter (`±25%`) to delay to avoid thundering herd

**Full example**

The middleware automatically retries failed model calls with exponential backoff.

**Python**
```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRetryMiddleware

# Basic usage with default settings (2 retries, exponential backoff)
agent = create_agent(
    model="gpt-5.5",
    tools=[search_tool],
    middleware=[ModelRetryMiddleware()],
)

# Custom exception filtering
class TimeoutError(Exception):
    """Custom exception for timeout errors."""
    pass

class ConnectionError(Exception):
    """Custom exception for connection errors."""
    pass

# Retry specific exceptions only
retry = ModelRetryMiddleware(
    max_retries=4,
    retry_on=(TimeoutError, ConnectionError),
    backoff_factor=1.5,
)

def should_retry(error: Exception) -> bool:
    # Only retry on rate limit errors
    if isinstance(error, TimeoutError):
        return True
    # Or check for specific HTTP status codes
    if hasattr(error, "status_code"):
        return error.status_code in (429, 503)
    return False

retry_with_filter = ModelRetryMiddleware(
    max_retries=3,
    retry_on=should_retry,
)

# Return error message instead of raising
retry_continue = ModelRetryMiddleware(
    max_retries=4,
    on_failure="continue",  # Return AIMessage with error instead of raising
)

# Custom error message formatting
def format_error(error: Exception) -> str:
    return f"Model call failed: {error}. Please try again later."

retry_with_formatter = ModelRetryMiddleware(
    max_retries=4,
    on_failure=format_error,
)

# Constant backoff (no exponential growth)
constant_backoff = ModelRetryMiddleware(
    max_retries=5,
    backoff_factor=0.0,  # No exponential growth
    initial_delay=2.0,  # Always wait 2 seconds
)

# Raise exception on failure
strict_retry = ModelRetryMiddleware(
    max_retries=2,
    on_failure="error",  # Re-raise exception instead of returning message
)
```

**JavaScript / TypeScript**
```typescript
import { createAgent, modelRetryMiddleware } from "langchain";

// Basic usage with default settings (2 retries, exponential backoff)
const agent = createAgent({
  model: "gpt-5.5",
  tools: [searchTool],
  middleware: [modelRetryMiddleware()],
});

class TimeoutError extends Error {
    // ...
}
class NetworkError extends Error {
    // ...
}

// Retry specific exceptions only
const retry = modelRetryMiddleware({
  maxRetries: 4,
  retryOn: [TimeoutError, NetworkError],
  backoffFactor: 1.5,
});

// Custom exception filtering
function shouldRetry(error: Error): boolean {
  // Only retry on rate limit errors
  if (error.name === "RateLimitError") {
    return true;
  }
  // Or check for specific HTTP status codes
  if (error.name === "HTTPError" && "statusCode" in error) {
    const statusCode = (error as any).statusCode;
    return statusCode === 429 || statusCode === 503;
  }
  return false;
}

const retryWithFilter = modelRetryMiddleware({
  maxRetries: 3,
  retryOn: shouldRetry,
});

// Return error message instead of raising
const retryContinue = modelRetryMiddleware({
  maxRetries: 4,
  onFailure: "continue", // Return AIMessage with error instead of throwing
});

// Custom error message formatting
const formatError = (error: Error) =>
  `Model call failed: ${error.message}. Please try again later.`;

const retryWithFormatter = modelRetryMiddleware({
  maxRetries: 4,
  onFailure: formatError,
});

// Constant backoff (no exponential growth)
const constantBackoff = modelRetryMiddleware({
  maxRetries: 5,
  backoffFactor: 0.0, // No exponential growth
  initialDelayMs: 2000, // Always wait 2 seconds
});

// Raise exception on failure
const strictRetry = modelRetryMiddleware({
  maxRetries: 2,
  onFailure: "error", // Re-raise exception instead of returning message
});
```

### LLM tool emulator

Emulate tool execution using an LLM for testing purposes, replacing actual tool calls with AI-generated responses. LLM tool emulators are useful for the following:

- Testing agent behavior without executing real tools.
- Developing agents when external tools are unavailable or expensive.
- Prototyping agent workflows before implementing actual tools.

**Python**
**API reference:** `LLMToolEmulator`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolEmulator

agent = create_agent(
    model="gpt-5.5",
    tools=[get_weather, search_database, send_email],
    middleware=[
        LLMToolEmulator(),  # Emulate all tools
    ],
)
```

**JavaScript / TypeScript**
```typescript
import { createAgent, toolEmulatorMiddleware } from "langchain";

const agent = createAgent({
  model: "gpt-5.5",
  tools: [getWeather, searchDatabase, sendEmail],
  middleware: [
    toolEmulatorMiddleware(), // Emulate all tools
  ],
});
```

**Configuration options**

**Python**
- **`tools`** (list[str | BaseTool])
    List of tool names (str) or BaseTool instances to emulate. If `None` (default), ALL tools will be emulated. If empty list `[]`, no tools will be emulated. If array with tool names/instances, only those tools will be emulated.

- **`model`** (string | BaseChatModel)
    Model to use for generating emulated tool responses. Can be a model identifier string (e.g., `'google_genai:gemini-3.6-flash'`) or a `BaseChatModel` instance. Defaults to the agent's model if not specified. See `init_chat_model`[init_chat_model(model)] for more information.

**JavaScript / TypeScript**
- **`tools`** ((string | ClientTool | ServerTool)[])
    List of tool names (string) or tool instances to emulate. If `undefined` (default), ALL tools will be emulated. If empty array `[]`, no tools will be emulated. If array with tool names/instances, only those tools will be emulated.

- **`model`** (string | BaseChatModel)
    Model to use for generating emulated tool responses. Can be a model identifier string (e.g., `'google_genai:gemini-3.6-flash'`) or a `BaseChatModel` instance. Defaults to the agent's model if not specified.

**Full example**

The middleware uses an LLM to generate plausible responses for tool calls instead of executing the actual tools.

**Python**
```python
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolEmulator
from langchain.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    return f"Weather in {location}"

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    return "Email sent"

# Emulate all tools (default behavior)
agent = create_agent(
    model="gpt-5.5",
    tools=[get_weather, send_email],
    middleware=[LLMToolEmulator()],
)

# Emulate specific tools only
agent2 = create_agent(
    model="gpt-5.5",
    tools=[get_weather, send_email],
    middleware=[LLMToolEmulator(tools=["get_weather"])],
)

# Use custom model for emulation
agent4 = create_agent(
    model="gpt-5.5",
    tools=[get_weather, send_email],
    middleware=[LLMToolEmulator(model="claude-sonnet-4-6")],
)
```

**JavaScript / TypeScript**
```typescript
import { createAgent, toolEmulatorMiddleware, tool } from "langchain";
import * as z from "zod";

const getWeather = tool(
  async ({ location }) => `Weather in ${location}`,
  {
    name: "get_weather",
    description: "Get the current weather for a location",
    schema: z.object({ location: z.string() }),
  }
);

const sendEmail = tool(
  async ({ to, subject, body }) => "Email sent",
  {
    name: "send_email",
    description: "Send an email",
    schema: z.object({
      to: z.string(),
      subject: z.string(),
      body: z.string(),
    }),
  }
);

// Emulate all tools (default behavior)
const agent = createAgent({
  model: "gpt-5.5",
  tools: [getWeather, sendEmail],
  middleware: [toolEmulatorMiddleware()],
});

// Emulate specific tools by name
const agent2 = createAgent({
  model: "gpt-5.5",
  tools: [getWeather, sendEmail],
  middleware: [
    toolEmulatorMiddleware({
      tools: ["get_weather"],
    }),
  ],
});

// Emulate specific tools by passing tool instances
const agent3 = createAgent({
  model: "gpt-5.5",
  tools: [getWeather, sendEmail],
  middleware: [
    toolEmulatorMiddleware({
      tools: [getWeather],
    }),
  ],
});

// Use custom model for emulation
const agent5 = createAgent({
  model: "gpt-5.5",
  tools: [getWeather, sendEmail],
  middleware: [
    toolEmulatorMiddleware({
      model: "claude-sonnet-4-6",
    }),
  ],
});
```

### Context editing

Manage conversation context by clearing older tool call outputs when token limits are reached, while preserving recent results. This helps keep context windows manageable in long conversations with many tool calls. Context editing is useful for the following:

- Long conversations with many tool calls that exceed token limits
- Reducing token costs by removing older tool outputs that are no longer relevant
- Maintaining only the most recent N tool results in context

**Python**
**API reference:** `ContextEditingMiddleware`, `ClearToolUsesEdit`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ContextEditingMiddleware, ClearToolUsesEdit

agent = create_agent(
    model="gpt-5.5",
    tools=[],
    middleware=[
        ContextEditingMiddleware(
            edits=[
                ClearToolUsesEdit(
                    trigger=100000,
                    keep=3,
                ),
            ],
        ),
    ],
)
```

**JavaScript / TypeScript**
```typescript
import { createAgent, contextEditingMiddleware, ClearToolUsesEdit } from "langchain";

const agent = createAgent({
  model: "gpt-5.5",
  tools: [],
  middleware: [
    contextEditingMiddleware({
      edits: [
        new ClearToolUsesEdit({
          triggerTokens: 100000,
          keep: 3,
        }),
      ],
    }),
  ],
});
```

**Configuration options**

**Python**
- **`edits`** (list[ContextEdit])
    List of `ContextEdit` strategies to apply

- **`token_count_method`** (string)
    Token counting method. Options: `'approximate'` or `'model'`

**`ClearToolUsesEdit` options:**

- **`trigger`** (number)
    Token count that triggers the edit. When the conversation exceeds this token count, older tool outputs will be cleared.

- **`clear_at_least`** (number)
    Minimum number of tokens to reclaim when the edit runs. If set to 0, clears as much as needed.

- **`keep`** (number)
    Number of most recent tool results that must be preserved. These will never be cleared.

- **`clear_tool_inputs`** (boolean)
    Whether to clear the originating tool call parameters on the AI message. When `True`, tool call arguments are replaced with empty objects.

- **`exclude_tools`** (list[string])
    List of tool names to exclude from clearing. These tools will never have their outputs cleared.

- **`placeholder`** (string)
    Placeholder text inserted for cleared tool outputs. This replaces the original tool message content.

**JavaScript / TypeScript**
- **`edits`** (ContextEdit[])
    Array of `ContextEdit` strategies to apply

**`ClearToolUsesEdit` options:**

- **`triggerTokens`** (number)
    Token count that triggers the edit. When the conversation exceeds this token count, older tool outputs will be cleared.

- **`clearAtLeast`** (number)
    Minimum number of tokens to reclaim when the edit runs. If set to 0, clears as much as needed.

- **`keep`** (number)
    Number of most recent tool results that must be preserved. These will never be cleared.

- **`clearToolInputs`** (boolean)
    Whether to clear the originating tool call parameters on the AI message. When `true`, tool call arguments are replaced with empty objects.

- **`excludeTools`** (string[])
    List of tool names to exclude from clearing. These tools will never have their outputs cleared.

- **`placeholder`** (string)
    Placeholder text inserted for cleared tool outputs. This replaces the original tool message content.

**Full example**

The middleware applies context editing strategies when token limits are reached. The most common strategy is `ClearToolUsesEdit`, which clears older tool results while preserving recent ones.

**How it works:**
1. Monitor token count in conversation
2. When threshold is reached, clear older tool outputs
3. Keep most recent N tool results
4. Optionally preserve tool call arguments for context

**Python**
```python
from langchain.agents import create_agent
from langchain.agents.middleware import ContextEditingMiddleware, ClearToolUsesEdit

agent = create_agent(
    model="gpt-5.5",
    tools=[search_tool, your_calculator_tool, database_tool],
    middleware=[
        ContextEditingMiddleware(
            edits=[
                ClearToolUsesEdit(
                    trigger=2000,
                    keep=3,
                    clear_tool_inputs=False,
                    exclude_tools=[],
                    placeholder="[cleared]",
                ),
            ],
        ),
    ],
)
```

**JavaScript / TypeScript**
```typescript
import { createAgent, contextEditingMiddleware, ClearToolUsesEdit } from "langchain";

const agent = createAgent({
  model: "gpt-5.5",
  tools: [searchTool, calculatorTool, databaseTool],
  middleware: [
    contextEditingMiddleware({
      edits: [
        new ClearToolUsesEdit({
          triggerTokens: 2000,
          keep: 3,
          clearToolInputs: false,
          excludeTools: [],
          placeholder: "[cleared]",
        }),
      ],
    }),
  ],
});
```

**Python**
### Provider tool search

Defer selected tools behind model providers' server-side tool search, so the model discovers them on demand instead of receiving every tool schema up front. Provider tool search is useful for:

- Reducing context bloat when using many tools.
- Improving tool selection accuracy by surfacing only relevant tools.

**Note**
    Requires a model with server-side tool search support: Anthropic (Claude Sonnet 4+/Opus 4+/Haiku 4.5+) or OpenAI (gpt-5.5+). Other providers raise a `ValueError`.

**API reference:** `ProviderToolSearchMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ProviderToolSearchMiddleware

agent = create_agent(
    model="anthropic:claude-opus-4-8",
    tools=[get_weather, lookup_order],
    middleware=[
        ProviderToolSearchMiddleware(searchable_tools=["lookup_order"]),
    ],
)
```

**Configuration options**

- **`searchable_tools`** (list[str | BaseTool])
    Tools to defer behind the provider's tool search, given by name or instance. Deferred tools are withheld from the model until its search surfaces them. Tools constructed with `extras={"defer_loading": True}` are deferred regardless of this option; if `searchable_tools` is omitted, only those pre-marked tools are deferred.

**Full example**

The middleware opts-in all tools included in `searchable_tools` for deferral and search. A tool can also opt into deferral at construction time by setting `extras={"defer_loading": True}`.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ProviderToolSearchMiddleware
from langchain.tools import tool

# Marked `defer_loading` at construction, so it's deferred on its own —
# no need to list it in `searchable_tools`.
@tool(extras={"defer_loading": True})
def send_email(to: str) -> str:
    """Send an email."""
    return "sent"

agent = create_agent(
    model="anthropic:claude-opus-4-8",
    tools=[send_email],
    middleware=[ProviderToolSearchMiddleware()],
)
```

**JavaScript / TypeScript**
### Provider tool search

Defer selected tools behind model providers' server-side tool search, so the model discovers them on demand instead of receiving every tool schema up front. Provider tool search is useful for:

- Reducing context bloat when using many tools.
- Improving tool selection accuracy by surfacing only relevant tools.

**Note**
    Requires a model with server-side tool search support: Anthropic (Claude Sonnet 4+/Opus 4+/Haiku 4.5+) or OpenAI (gpt-5.5+). Other providers throw an error.

**API reference:** `providerToolSearchMiddleware`

```typescript
import { createAgent, providerToolSearchMiddleware } from "langchain";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const getWeather = tool(async () => "Sunny, 22C", {
  name: "get_weather",
  description: "Get the current weather for a city",
  schema: z.object({ city: z.string() }),
});

const lookupOrderStatus = tool(async () => "OUT_FOR_DELIVERY", {
  name: "lookup_order_status",
  description: "Look up the current delivery status of a customer order by ID",
  schema: z.object({ orderId: z.string() }),
});

const nicheTools = [lookupOrderStatus];

const agent = createAgent({
  model: "anthropic:claude-opus-4-8",
  tools: [getWeather, ...nicheTools],
  middleware: [
    providerToolSearchMiddleware({ searchableTools: nicheTools }),
  ],
});
```

**Configuration options**

- **`searchableTools`** ((string | StructuredToolInterface)[])
    Tools to defer behind the provider's tool search, given by name or instance. Deferred tools are withheld from the model until its search surfaces them. Tools constructed with `extras.defer_loading: true` are deferred regardless of this option; if `searchableTools` is omitted, only those pre-marked tools are deferred.

**Full example**

The middleware opts-in all tools included in the `searchableTools` for deferral and search. A tool can also opt into deferral at construction time by setting `extras.defer_loading: true`

```typescript
import { createAgent, providerToolSearchMiddleware } from "langchain";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

// Marked `defer_loading` at construction, so it's deferred on its own —
// no need to list it in `searchableTools`.
const sendEmail = tool(async () => "sent", {
  name: "send_email",
  description: "Send an email",
  schema: z.object({ to: z.string() }),
  extras: { defer_loading: true },
});

const agent = createAgent({
  model: "anthropic:claude-opus-4-8",
  tools: [sendEmail],
  middleware: [providerToolSearchMiddleware()],
});
```

**Python**
### Shell tool

Expose a persistent shell session to agents for command execution. Shell tool middleware is useful for the following:

- Agents that need to execute system commands
- Development and deployment automation tasks
- Testing and validation workflows
- File system operations and script execution

**Warning**
    **Security consideration**: Use appropriate execution policies (`HostExecutionPolicy`, `DockerExecutionPolicy`, or `CodexSandboxExecutionPolicy`) to match your deployment's security requirements.

**Note**
    **Limitation**: Persistent shell sessions do not currently work with interrupts (human-in-the-loop). We anticipate adding support for this in the future.

**API reference:** `ShellToolMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import (
    ShellToolMiddleware,
    HostExecutionPolicy,
)

agent = create_agent(
    model="gpt-5.5",
    tools=[search_tool],
    middleware=[
        ShellToolMiddleware(
            workspace_root="/workspace",
            execution_policy=HostExecutionPolicy(),
        ),
    ],
)
```

**Configuration options**

- **`workspace_root`** (str | Path | None)
    Base directory for the shell session. If omitted, a temporary directory is created when the agent starts and removed when it ends.

- **`startup_commands`** (tuple[str, ...] | list[str] | str | None)
    Optional commands executed sequentially after the session starts

- **`shutdown_commands`** (tuple[str, ...] | list[str] | str | None)
    Optional commands executed before the session shuts down

- **`execution_policy`** (BaseExecutionPolicy | None)
    Execution policy controlling timeouts, output limits, and resource configuration. Options:

    - `HostExecutionPolicy` - Full host access (default); best for trusted environments where the agent already runs inside a container or VM
    - `DockerExecutionPolicy` - Launches a separate Docker container for each agent run, providing harder isolation
    - `CodexSandboxExecutionPolicy` - Reuses the Codex CLI sandbox for additional syscall/filesystem restrictions

- **`redaction_rules`** (tuple[RedactionRule, ...] | list[RedactionRule] | None)
    Optional redaction rules to sanitize command output before returning it to the model.
**Warning**
    Redaction rules are applied post execution and do not prevent exfiltration of secrets or sensitive data when using `HostExecutionPolicy`.

- **`tool_description`** (str | None)
    Optional override for the registered shell tool description

- **`shell_command`** (Sequence[str] | str | None)
    Optional shell executable (string) or argument sequence used to launch the persistent session. Defaults to `/bin/bash`.

- **`env`** (Mapping[str, Any] | None)
    Optional environment variables to supply to the shell session. Values are coerced to strings before command execution.

**Full example**

The middleware provides a single persistent shell session that agents can use to execute commands sequentially.

**Execution policies:**
- `HostExecutionPolicy` (default) - Native execution with full host access
- `DockerExecutionPolicy` - Isolated Docker container execution
- `CodexSandboxExecutionPolicy` - Sandboxed execution via Codex CLI

```python
from langchain.agents import create_agent
from langchain.agents.middleware import (
    ShellToolMiddleware,
    HostExecutionPolicy,
    DockerExecutionPolicy,
    RedactionRule,
)

# Basic shell tool with host execution
agent = create_agent(
    model="gpt-5.5",
    tools=[search_tool],
    middleware=[
        ShellToolMiddleware(
            workspace_root="/workspace",
            execution_policy=HostExecutionPolicy(),
        ),
    ],
)

# Docker isolation with startup commands
agent_docker = create_agent(
    model="gpt-5.5",
    tools=[],
    middleware=[
        ShellToolMiddleware(
            workspace_root="/workspace",
            startup_commands=["pip install requests", "export PYTHONPATH=/workspace"],
            execution_policy=DockerExecutionPolicy(
                image="python:3.11-slim",
                command_timeout=60.0,
            ),
        ),
    ],
)

# With output redaction (applied post execution)
agent_redacted = create_agent(
    model="gpt-5.5",
    tools=[],
    middleware=[
        ShellToolMiddleware(
            workspace_root="/workspace",
            redaction_rules=[
                RedactionRule(pii_type="api_key", detector=r"sk-[a-zA-Z0-9]{32}"),
            ],
        ),
    ],
)
```

### File search

Provide Glob and Grep search tools over a filesystem. File search middleware is useful for the following:

- Code exploration and analysis
- Finding files by name patterns
- Searching code content with regex
- Large codebases where file discovery is needed

**API reference:** `FilesystemFileSearchMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import FilesystemFileSearchMiddleware

agent = create_agent(
    model="gpt-5.5",
    tools=[],
    middleware=[
        FilesystemFileSearchMiddleware(
            root_path="/workspace",
            use_ripgrep=True,
        ),
    ],
)
```

**Configuration options**

- **`root_path`** (str, required)
    Root directory to search. All file operations are relative to this path.

- **`use_ripgrep`** (bool)
    Whether to use ripgrep for search. Falls back to Python regex if ripgrep is unavailable.

- **`max_file_size_mb`** (int)
    Maximum file size to search in MB. Files larger than this are skipped.

**Full example**

The middleware adds two search tools to agents:

**Glob tool** - Fast file pattern matching:
- Supports patterns like `**/*.py`, `src/**/*.ts`
- Returns matching file paths sorted by modification time

**Grep tool** - Content search with regex:
- Full regex syntax support
- Filter by file patterns with `include` parameter
- Three output modes: `files_with_matches`, `content`, `count`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import FilesystemFileSearchMiddleware
from langchain.messages import HumanMessage

agent = create_agent(
    model="gpt-5.5",
    tools=[],
    middleware=[
        FilesystemFileSearchMiddleware(
            root_path="/workspace",
            use_ripgrep=True,
            max_file_size_mb=10,
        ),
    ],
)

# Agent can now use glob_search and grep_search tools
result = agent.invoke({
    "messages": [HumanMessage("Find all Python files containing 'async def'")]
})

# The agent will use:
# 1. glob_search(pattern="**/*.py") to find Python files
# 2. grep_search(pattern="async def", include="*.py") to find async functions
```

### Filesystem middleware

Context engineering is a main challenge in building effective agents. This is particularly difficult when using tools that return variable-length results (for example, `web_search` and RAG), as long tool results can quickly fill your context window.

`FilesystemMiddleware` from [Deep Agents](../deepagents/overview.md) provides four tools for interacting with both short-term and long-term memory:

- `ls`: List the files in the filesystem
- `read_file`: Read an entire file or a certain number of lines from a file
- `write_file`: Write a new file to the filesystem
- `edit_file`: Edit an existing file in the filesystem

**Python**
```python
from langchain.agents import create_agent
from deepagents.middleware.filesystem import FilesystemMiddleware

# FilesystemMiddleware is included by default in create_deep_agent
# You can customize it if building a custom agent
agent = create_agent(
    model="claude-sonnet-4-6",
    middleware=[
        FilesystemMiddleware(
            backend=None,  # Optional: custom backend (defaults to StateBackend)
            system_prompt="Write to the filesystem when...",  # Optional custom addition to the system prompt
            custom_tool_descriptions={
                "ls": "Use the ls tool when...",
                "read_file": "Use the read_file tool to..."
            },  # Optional: Custom descriptions for filesystem tools
            tools=["read_file", "ls", "glob", "grep"],  # Optional: Allowlist restricting which filesystem tools are exposed
        ),
    ],
)
```

**JavaScript / TypeScript**
```typescript
import { createAgent } from "langchain";
import { createFilesystemMiddleware } from "deepagents";

// FilesystemMiddleware is included by default in createDeepAgent
// You can customize it if building a custom agent
const agent = createAgent({
  model: "claude-sonnet-4-6",
  middleware: [
    createFilesystemMiddleware({
      backend: undefined,  // Optional: custom backend (defaults to StateBackend)
      systemPrompt: "Write to the filesystem when...",  // Optional custom system prompt override
      customToolDescriptions: {
        ls: "Use the ls tool when...",
        read_file: "Use the read_file tool to...",
      },  // Optional: Custom descriptions for filesystem tools
    }),
  ],
});
```

#### Short-term vs. long-term filesystem

By default, these tools write to a local "filesystem" in your graph state. To enable persistent storage across threads, configure a `CompositeBackend` that routes specific paths (like `/memories/`) to a `StoreBackend`.

**Python**
```python
from langchain.agents import create_agent
from deepagents.middleware import FilesystemMiddleware
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

agent = create_agent(
    model="claude-sonnet-4-6",
    store=store,
    middleware=[
        FilesystemMiddleware(
            backend=CompositeBackend(
                default=StateBackend(),
                routes={"/memories/": StoreBackend()}
            ),
            custom_tool_descriptions={
                "ls": "Use the ls tool when...",
                "read_file": "Use the read_file tool to..."
            }  # Optional: Custom descriptions for filesystem tools
        ),
    ],
)
```

**JavaScript / TypeScript**
```typescript
import { createAgent } from "langchain";
import { createFilesystemMiddleware, CompositeBackend, StateBackend, StoreBackend } from "deepagents";
import { InMemoryStore } from "@langchain/langgraph-checkpoint";

const store = new InMemoryStore();

const agent = createAgent({
  model: "claude-sonnet-4-6",
  store,
  middleware: [
    createFilesystemMiddleware({
      backend: new CompositeBackend(
        new StateBackend(),
        { "/memories/": new StoreBackend() }
      ),
      systemPrompt: "Write to the filesystem when...", // Optional custom system prompt override
      customToolDescriptions: {
        ls: "Use the ls tool when...",
        read_file: "Use the read_file tool to...",
      }, // Optional: Custom descriptions for filesystem tools
    }),
  ],
});
```

When you configure a `CompositeBackend` with a `StoreBackend` for `/memories/`, any files prefixed with **/memories/** are saved to persistent storage and survive across different threads. Files without this prefix remain in ephemeral state storage.

### Subagent

Handing off tasks to subagents isolates context, keeping the main (supervisor) agent's context window clean while still going deep on a task.

The subagents middleware from [Deep Agents](../deepagents/overview.md) allows you to supply subagents through a `task` tool.

**Python**
```python
from langchain.tools import tool
from langchain.agents import create_agent
from deepagents.middleware.subagents import SubAgentMiddleware

@tool
def get_weather(city: str) -> str:
    """Get the weather in a city."""
    return f"The weather in {city} is sunny."

agent = create_agent(
    model="claude-sonnet-4-6",
    middleware=[
        SubAgentMiddleware(
            default_model="claude-sonnet-4-6",
            default_tools=[],
            subagents=[
                {
                    "name": "weather",
                    "description": "This subagent can get weather in cities.",
                    "system_prompt": "Use the get_weather tool to get the weather in a city.",
                    "tools": [get_weather],
                    "model": "gpt-5.5",
                    "middleware": [],
                }
            ],
        )
    ],
)
```

**JavaScript / TypeScript**
```typescript
import { tool } from "langchain";
import { createAgent } from "langchain";
import { createSubAgentMiddleware } from "deepagents";
import { z } from "zod";

const getWeather = tool(
  async ({ city }: { city: string }) => {
    return `The weather in ${city} is sunny.`;
  },
  {
    name: "get_weather",
    description: "Get the weather in a city.",
    schema: z.object({
      city: z.string(),
    }),
  },
);

const agent = createAgent({
  model: "claude-sonnet-4-6",
  middleware: [
    createSubAgentMiddleware({
      defaultModel: "claude-sonnet-4-6",
      defaultTools: [],
      subagents: [
        {
          name: "weather",
          description: "This subagent can get weather in cities.",
          systemPrompt: "Use the get_weather tool to get the weather in a city.",
          tools: [getWeather],
          model: "gpt-5.5",
          middleware: [],
        },
      ],
    }),
  ],
});
```

A subagent is defined with a **name**, **description**, **system prompt**, and **tools**. You can also provide a subagent with a custom **model**, or with additional **middleware**. This can be particularly useful when you want to give the subagent an additional state key to share with the main agent.

For more complex use cases, you can also provide your own prebuilt LangGraph graph as a subagent.

**Python**
```python
from langchain.agents import create_agent
from deepagents.middleware.subagents import SubAgentMiddleware
from deepagents import CompiledSubAgent
from langgraph.graph import StateGraph

# Create a custom LangGraph graph
def create_weather_graph():
    workflow = StateGraph(...)
    # Build your custom graph
    return workflow.compile()

weather_graph = create_weather_graph()

# Wrap it in a CompiledSubAgent
weather_subagent = CompiledSubAgent(
    name="weather",
    description="This subagent can get weather in cities.",
    runnable=weather_graph
)

agent = create_agent(
    model="claude-sonnet-4-6",
    middleware=[
        SubAgentMiddleware(
            default_model="claude-sonnet-4-6",
            default_tools=[],
            subagents=[weather_subagent],
        )
    ],
)
```

**JavaScript / TypeScript**
```typescript
import { tool, createAgent } from "langchain";
import { createSubAgentMiddleware, type SubAgent } from "deepagents";
import { z } from "zod";

const getWeather = tool(
  async ({ city }: { city: string }) => {
    return `The weather in ${city} is sunny.`;
  },
  {
    name: "get_weather",
    description: "Get the weather in a city.",
    schema: z.object({
      city: z.string(),
    }),
  },
);

const weatherSubagent: SubAgent = {
  name: "weather",
  description: "This subagent can get weather in cities.",
  systemPrompt: "Use the get_weather tool to get the weather in a city.",
  tools: [getWeather],
  model: "gpt-5.5",
  middleware: [],
};

const agent = createAgent({
  model: "claude-sonnet-4-6",
  middleware: [
    createSubAgentMiddleware({
      defaultModel: "claude-sonnet-4-6",
      defaultTools: [],
      subagents: [weatherSubagent],
    }),
  ],
});
```

In addition to any user-defined subagents, the main agent has access to a `general-purpose` subagent at all times. This subagent has the same instructions as the main agent and all the tools it has access to. The primary purpose of the `general-purpose` subagent is context isolation—the main agent can delegate a complex task to this subagent and get a concise answer back without bloat from intermediate tool calls.

**Python**
### Rubric grading

**Note**
`RubricMiddleware` requires `deepagents>=0.6.5`. It is in **beta**; the API may change in the future.

Some tasks have a clear definition of "done" that an agent cannot reliably hit on the first try. `RubricMiddleware` lets you declare _what done looks like_ as a rubric and have the agent self-evaluate and iterate until the rubric is satisfied or a maximum iteration cap is hit.

**API reference:** `RubricMiddleware`

Code example: [`code/langchain/rubric-configure.py`](../code/langchain/rubric-configure.py)

```python Google
from deepagents import RubricMiddleware, create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    middleware=[
        RubricMiddleware(
            model="anthropic:claude-haiku-4-5",
            max_iterations=3,
        ),
    ],
    checkpointer=InMemorySaver(),
)
```

```python OpenAI
from deepagents import RubricMiddleware, create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_deep_agent(
    model="openai:gpt-5.5",
    middleware=[
        RubricMiddleware(
            model="anthropic:claude-haiku-4-5",
            max_iterations=3,
        ),
    ],
    checkpointer=InMemorySaver(),
)
```

```python Anthropic
from deepagents import RubricMiddleware, create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    middleware=[
        RubricMiddleware(
            model="anthropic:claude-haiku-4-5",
            max_iterations=3,
        ),
    ],
    checkpointer=InMemorySaver(),
)
```

```python OpenRouter
from deepagents import RubricMiddleware, create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_deep_agent(
    model="openrouter:z-ai/glm-5.2",
    middleware=[
        RubricMiddleware(
            model="anthropic:claude-haiku-4-5",
            max_iterations=3,
        ),
    ],
    checkpointer=InMemorySaver(),
)
```

```python Fireworks
from deepagents import RubricMiddleware, create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_deep_agent(
    model="fireworks:accounts/fireworks/models/glm-5p2",
    middleware=[
        RubricMiddleware(
            model="anthropic:claude-haiku-4-5",
            max_iterations=3,
        ),
    ],
    checkpointer=InMemorySaver(),
)
```

```python Baseten
from deepagents import RubricMiddleware, create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_deep_agent(
    model="baseten:zai-org/GLM-5.2",
    middleware=[
        RubricMiddleware(
            model="anthropic:claude-haiku-4-5",
            max_iterations=3,
        ),
    ],
    checkpointer=InMemorySaver(),
)
```

```python Ollama
from deepagents import RubricMiddleware, create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_deep_agent(
    model="ollama:north-mini-code-1.0",
    middleware=[
        RubricMiddleware(
            model="anthropic:claude-haiku-4-5",
            max_iterations=3,
        ),
    ],
    checkpointer=InMemorySaver(),
)
```
