---
type: Documentation Page
title: Models
product: langchain
resource: /docs/langchain/models
source: /oss/langchain/models
tags:
  - langchain
  - models
timestamp: 2026-08-13T16:33:17Z
code_examples:
  - ../code/langchain/chat-model-tabs.py
  - ../code/langchain/chat-model-tabs.ts
---

# Models

LLMs are powerful AI tools that can interpret and generate text like humans. They're versatile enough to write content, translate languages, summarize, and answer questions without needing specialized training for each task.

In addition to text generation, many models support:

* [Tool calling](#tool-calling) - calling external tools (like databases queries or API calls) and use results in their responses.
* [Structured output](#structured-output) - where the model's response is constrained to follow a defined format.
* [Multimodality](#multimodal) - process and return data other than text, such as images, audio, and video.
* [Reasoning](#reasoning) - models perform multi-step reasoning to arrive at a conclusion.

Models are the reasoning engine of [agents](../langchain/agents.md). They drive the agent's decision-making process, determining which tools to call, how to interpret results, and when to provide a final answer.

The quality and capabilities of the model you choose directly impact your agent's baseline reliability and performance. Different models excel at different tasks - some are better at following complex instructions, others at structured reasoning, and some support larger context windows for handling more information.

LangChain's standard model interfaces give you access to many different provider integrations, which makes it easy to experiment with and switch between models to find the best fit for your use case.

For provider-specific integration information and capabilities, see the provider's chat model page.

## Basic usage

Models can be utilized in two ways:

1. **With agents** - Models can be dynamically specified when creating an [agent](../langchain/agents.md#model).
2. **Standalone** - Models can be called directly (outside of the agent loop) for tasks like text generation, classification, or extraction without the need for an agent framework.

The same model interface works in both contexts, which gives you the flexibility to start simple and scale up to more complex agent-based workflows as needed.

### Initialize a model

**Python**
The easiest way to get started with a standalone model in LangChain is to use `init_chat_model` to initialize one from a chat model provider of your choice (examples below):

Code example: [`code/langchain/chat-model-tabs.py`](../code/langchain/chat-model-tabs.py)

**OpenAI**

```bash pip
pip install -U "langchain[openai]"
```

```bash uv
uv add "langchain[openai]"
```

```python init_chat_model
import os
from langchain.chat_models import init_chat_model

os.environ["OPENAI_API_KEY"] = "sk-..."

model = init_chat_model("gpt-5.5")
```
```python Model Class
import os
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = "sk-..."

model = ChatOpenAI(model="gpt-5.5")
```

**Anthropic**

```bash pip
pip install -U "langchain[anthropic]"
```

```bash uv
uv add "langchain[anthropic]"
```

```python init_chat_model
import os
from langchain.chat_models import init_chat_model

os.environ["ANTHROPIC_API_KEY"] = "sk-..."

model = init_chat_model("claude-sonnet-4-6")
```
```python Model Class
import os
from langchain_anthropic import ChatAnthropic

os.environ["ANTHROPIC_API_KEY"] = "sk-..."

model = ChatAnthropic(model="claude-sonnet-4-6")
```

**Azure**

```bash pip
pip install -U "langchain[openai]"
```

```bash uv
uv add "langchain[openai]"
```

        

```python init_chat_model
import os
from langchain.chat_models import init_chat_model

os.environ["AZURE_OPENAI_API_KEY"] = "..."
os.environ["AZURE_OPENAI_ENDPOINT"] = "..."
os.environ["OPENAI_API_VERSION"] = "2025-03-01-preview"

model = init_chat_model(
    "azure_openai:gpt-5.5",
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
)
```
```python Model Class
import os
from langchain_openai import AzureChatOpenAI

os.environ["AZURE_OPENAI_API_KEY"] = "..."
os.environ["AZURE_OPENAI_ENDPOINT"] = "..."
os.environ["OPENAI_API_VERSION"] = "2025-03-01-preview"

model = AzureChatOpenAI(
    model="gpt-5.5",
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
)
```

**Google Gemini**

```bash pip
pip install -U "langchain[google-genai]"
```

```bash uv
uv add "langchain[google-genai]"
```

        

```python init_chat_model
import os
from langchain.chat_models import init_chat_model

os.environ["GOOGLE_API_KEY"] = "..."

model = init_chat_model("google_genai:gemini-2.5-flash-lite")
```
```python Model Class
import os
from langchain_google_genai import ChatGoogleGenerativeAI

os.environ["GOOGLE_API_KEY"] = "..."

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
```

**AWS Bedrock**

```bash pip
pip install -U "langchain[aws]"
```

```bash uv
uv add "langchain[aws]"
```

        

```python init_chat_model
from langchain.chat_models import init_chat_model

# Follow the steps here to configure your credentials:
# https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html

model = init_chat_model(
    "us.anthropic.claude-sonnet-4-6",
    model_provider="bedrock_converse",
)
```
```python Model Class
from langchain_aws import ChatBedrock

model = ChatBedrock(model="us.anthropic.claude-sonnet-4-6")
```

**HuggingFace**

```bash pip
pip install -U "langchain[huggingface]"
```

```bash uv
uv add "langchain[huggingface]"
```

        

```python init_chat_model
import os
from langchain.chat_models import init_chat_model

os.environ["HUGGINGFACEHUB_API_TOKEN"] = "hf_..."

model = init_chat_model(
    "microsoft/Phi-3-mini-4k-instruct",
    model_provider="huggingface",
    temperature=0.7,
    max_tokens=1024,
)
```

```python Model Class
import os
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

os.environ["HUGGINGFACEHUB_API_TOKEN"] = "hf_..."

llm = HuggingFaceEndpoint(
    repo_id="microsoft/Phi-3-mini-4k-instruct",
    temperature=0.7,
    max_length=1024,
)
model = ChatHuggingFace(llm=llm)
```

**OpenRouter**

```bash pip
pip install -U "langchain-openrouter"
```

```bash uv
uv add "langchain-openrouter"
```

        

```python init_chat_model
import os
from langchain.chat_models import init_chat_model

os.environ["OPENROUTER_API_KEY"] = "sk-..."

model = init_chat_model(
    "auto",
    model_provider="openrouter",
)
```
```python Model Class
import os
from langchain_openrouter import ChatOpenRouter

os.environ["OPENROUTER_API_KEY"] = "sk-..."

model = ChatOpenRouter(model="auto")
```

```python
response = model.invoke("Why do parrots talk?")
```

See `init_chat_model`[init_chat_model] for more detail, including information on how to pass model [parameters](#parameters).

**JavaScript / TypeScript**
The easiest way to get started with a standalone model in LangChain is to use `initChatModel` to initialize one from a chat model provider of your choice (examples below):

Code example: [`code/langchain/chat-model-tabs.ts`](../code/langchain/chat-model-tabs.ts)

**OpenAI**

```bash npm
npm install @langchain/openai
```
```bash pnpm
pnpm install @langchain/openai
```
```bash yarn
yarn add @langchain/openai
```
```bash bun
bun add @langchain/openai
```

```typescript initChatModel
import { initChatModel } from "langchain";

process.env.OPENAI_API_KEY = "your-api-key";

const model = await initChatModel("gpt-5.5");
```
```typescript Model Class
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({
  model: "gpt-5.5",
  apiKey: "your-api-key"
});
```

**Anthropic**

```bash npm
npm install @langchain/anthropic
```
```bash pnpm
pnpm install @langchain/anthropic
```
```bash yarn
yarn add @langchain/anthropic
```
```bash pnpm
pnpm add @langchain/anthropic
```

```typescript initChatModel
import { initChatModel } from "langchain";

process.env.ANTHROPIC_API_KEY = "your-api-key";

const model = await initChatModel("claude-sonnet-4-6");
```
```typescript Model Class
import { ChatAnthropic } from "@langchain/anthropic";

const model = new ChatAnthropic({
  model: "claude-sonnet-4-6",
  apiKey: "your-api-key"
});
```

**Azure**

```bash npm
npm install @langchain/azure
```
```bash pnpm
pnpm install @langchain/azure
```
```bash yarn
yarn add @langchain/azure
```
```bash bun
bun add @langchain/azure
```

```typescript initChatModel
import { initChatModel } from "langchain";

process.env.AZURE_OPENAI_API_KEY = "your-api-key";
process.env.AZURE_OPENAI_ENDPOINT = "your-endpoint";
process.env.OPENAI_API_VERSION = "your-api-version";

const model = await initChatModel("azure_openai:gpt-5.5");
```
```typescript Model Class
import { AzureChatOpenAI } from "@langchain/openai";

const model = new AzureChatOpenAI({
  model: "gpt-5.5",
  azureOpenAIApiKey: "your-api-key",
  azureOpenAIApiEndpoint: "your-endpoint",
  azureOpenAIApiVersion: "your-api-version"
});
```

**Google Gemini**

```bash npm
npm install @langchain/google-genai
```
```bash pnpm
pnpm install @langchain/google-genai
```
```bash yarn
yarn add @langchain/google-genai
```
```bash bun
bun add @langchain/google-genai
```

```typescript initChatModel
import { initChatModel } from "langchain";

process.env.GOOGLE_API_KEY = "your-api-key";

const model = await initChatModel("google-genai:gemini-2.5-flash-lite");
```
```typescript Model Class
import { ChatGoogleGenerativeAI } from "@langchain/google-genai";

const model = new ChatGoogleGenerativeAI({
  model: "gemini-2.5-flash-lite",
  apiKey: "your-api-key"
});
```

**Bedrock Converse**

```bash npm
npm install @langchain/aws
```
```bash pnpm
pnpm install @langchain/aws
```
```bash yarn
yarn add @langchain/aws
```
```bash bun
bun add @langchain/aws
```

```typescript initChatModel
import { initChatModel } from "langchain";

// Follow the steps here to configure your credentials:
// https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html

const model = await initChatModel("bedrock:gpt-5.5");
```
```typescript Model Class
import { ChatBedrockConverse } from "@langchain/aws";

// Follow the steps here to configure your credentials:
// https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html

const model = new ChatBedrockConverse({
  model: "gpt-5.5",
  region: "us-east-2"
});
```

```typescript
const response = await model.invoke("Why do parrots talk?");
```
See `initChatModel`[initChatModel] for more detail, including information on how to pass model [parameters](#parameters).

### Supported providers and models

LangChain supports all major model providers through dedicated integration packages. Each provider package implements the same standard interface, so you can swap providers without rewriting application logic. New model names work immediately — no LangChain update required — because provider packages pass model names directly to the provider's API.

Browse the full list of supported providers, or see Providers and models for a conceptual overview of how providers, packages, and model names work together in LangChain.

## Parameters

A chat model takes parameters that can be used to configure its behavior. The full set of supported parameters varies by model and provider, but standard ones include:

- **`model`** (string, required)
   The name or identifier of the specific model you want to use with a provider. You can also specify both the model and its provider in a single argument using the '{model_provider}:{model}' format, for example, 'openai:o1'.

**Python**
- **`api_key`** (string)
    The key required for authenticating with the model's provider. This is usually issued when you sign up for access to the model. Often accessed by setting an environment variable.

**JavaScript / TypeScript**
- **`apiKey`** (string)
    The key required for authenticating with the model's provider. This is usually issued when you sign up for access to the model. Often accessed by setting an environment variable.

- **`temperature`** (number)
    Controls the randomness of the model's output. A higher number makes responses more creative; lower ones make them more deterministic.

**Python**
- **`max_tokens`** (number)
    Limits the total number of tokens in the response, effectively controlling how long the output can be.

**JavaScript / TypeScript**
- **`maxTokens`** (number)
    Limits the total number of tokens in the response, effectively controlling how long the output can be.

- **`timeout`** (number)
    The maximum time (in seconds) to wait for a response from the model before canceling the request.

**Python**
- **`max_retries`** (number)
    The maximum number of attempts the system will make to resend a request if it fails due to issues like network timeouts or rate limits. Retries use exponential backoff with jitter. Network errors, rate limits (429), and server errors (5xx) are retried automatically. Client errors such as 401 (unauthorized) or 404 are not retried. For long-running [agent](../deepagents/overview.md) tasks on unreliable networks, consider increasing this to 10–15.

**JavaScript / TypeScript**
- **`maxRetries`** (number)
    The maximum number of attempts the system will make to resend a request if it fails due to issues like network timeouts or rate limits. Retries use exponential backoff with jitter. Network errors, rate limits (429), and server errors (5xx) are retried automatically. Client errors such as 401 (unauthorized) or 404 are not retried. For long-running [agent](../deepagents/overview.md) tasks on unreliable networks, consider increasing this to 10–15.

**Python**
Using `init_chat_model`, pass these parameters as inline `**kwargs`:

```python Initialize using model parameters
model = init_chat_model(
    "claude-sonnet-4-6",
    # Kwargs passed to the model:
    temperature=0.7,
    timeout=30,
    max_tokens=1000,
    max_retries=6,  # Default; increase for unreliable networks
)
```

**JavaScript / TypeScript**
Using `initChatModel`, pass these parameters as inline parameters:

```typescript Initialize using model parameters
const model = await initChatModel(
    "claude-sonnet-4-6",
    { temperature: 0.7, timeout: 30, maxTokens: 1000, maxRetries: 6 }
)
```

### Connection resilience

LangChain chat models automatically retry failed API requests with exponential backoff. By default, models retry up to **6 times** for network errors, rate limits (429), and server errors (5xx). Client errors like 401 (unauthorized) or 404 are not retried.

**Python**
You can adjust `max_retries` and `timeout` when creating a model, then pass that instance to `create_agent`, `create_deep_agent`, or call it standalone:

```python
from langchain.chat_models import init_chat_model

model = init_chat_model(
    "google_genai:gemini-3.6-flash",
    max_retries=10,  # Increase for unreliable networks (default: 6)
    timeout=120,  # Seconds; increase for slow connections
)
```

**JavaScript / TypeScript**
You can adjust `maxRetries` and `timeout` when creating a model, then pass that instance to `createAgent`, `createDeepAgent`, or call it standalone:

```typescript
import { ChatAnthropic } from "@langchain/anthropic";

const model = new ChatAnthropic({
  model: "google_genai:gemini-3.6-flash",
  maxRetries: 10, // Increase for unreliable networks (default: 6)
  timeout: 120_000, // Milliseconds; increase for slow connections
});
```

**Tip**
    For long-running agent graphs on unreliable networks, consider higher `max_retries` (for example 10–15) and a [checkpointer](../langgraph/persistence.md) so that progress is preserved across failures.

**Info**
    Each chat model integration may have additional params used to control provider-specific functionality.

    For example, `ChatOpenAI` has `use_responses_api` to dictate whether to use the OpenAI Responses or Completions API.

    To find all the parameters supported by a given chat model, head to the chat model integrations page.

---

## Invocation

A chat model must be invoked to generate an output. There are three primary invocation methods, each suited to different use cases.

### Invoke

The most straightforward way to call a model is to use `invoke()`[BaseChatModel.invoke] with a single message or a list of messages.

**Python**
```python Single message
response = model.invoke("Why do parrots have colorful feathers?")
print(response)
```

**JavaScript / TypeScript**
```typescript Single message
const response = await model.invoke("Why do parrots have colorful feathers?");
console.log(response);
```

A list of messages can be provided to a chat model to represent conversation history. Each message has a role that models use to indicate who sent the message in the conversation.

See the messages guide for more detail on roles, types, and content.

**Python**
```python Dictionary format
conversation = [
    {"role": "system", "content": "You are a helpful assistant that translates English to French."},
    {"role": "user", "content": "Translate: I love programming."},
    {"role": "assistant", "content": "J'adore la programmation."},
    {"role": "user", "content": "Translate: I love building applications."}
]

response = model.invoke(conversation)
print(response)  # AIMessage("J'adore créer des applications.")
```
```python Message objects
from langchain.messages import HumanMessage, AIMessage, SystemMessage

conversation = [
    SystemMessage("You are a helpful assistant that translates English to French."),
    HumanMessage("Translate: I love programming."),
    AIMessage("J'adore la programmation."),
    HumanMessage("Translate: I love building applications.")
]

response = model.invoke(conversation)
print(response)  # AIMessage("J'adore créer des applications.")
```

**JavaScript / TypeScript**
```typescript Object format
const conversation = [
  { role: "system", content: "You are a helpful assistant that translates English to French." },
  { role: "user", content: "Translate: I love programming." },
  { role: "assistant", content: "J'adore la programmation." },
  { role: "user", content: "Translate: I love building applications." },
];

const response = await model.invoke(conversation);
console.log(response);  // AIMessage("J'adore créer des applications.")
```
```typescript Message objects
import { HumanMessage, AIMessage, SystemMessage } from "langchain";

const conversation = [
  new SystemMessage("You are a helpful assistant that translates English to French."),
  new HumanMessage("Translate: I love programming."),
  new AIMessage("J'adore la programmation."),
  new HumanMessage("Translate: I love building applications."),
];

const response = await model.invoke(conversation);
console.log(response);  // AIMessage("J'adore créer des applications.")
```

**Info**
    If the return type of your invocation is a string, ensure that you are using a chat model as opposed to an LLM. Legacy, text-completion LLMs return strings directly. LangChain chat models are prefixed with "Chat", e.g., @`ChatOpenAI`.

### Stream

Most models can stream their output content while it is being generated. By displaying output progressively, streaming significantly improves user experience, particularly for longer responses.

Calling `stream()`[BaseChatModel.stream] returns an iterator that yields output chunks as they are produced. You can use a loop to process each chunk in real-time:

**Python**

```python Basic text streaming
for chunk in model.stream("Why do parrots have colorful feathers?"):
    print(chunk.text, end="|", flush=True)
```

```python Stream tool calls, reasoning, and other content
for chunk in model.stream("What color is the sky?"):
    for block in chunk.content_blocks:
        if block["type"] == "reasoning" and (reasoning := block.get("reasoning")):
            print(f"Reasoning: {reasoning}")
        elif block["type"] == "tool_call_chunk":
            print(f"Tool call chunk: {block}")
        elif block["type"] == "text":
            print(block["text"])
        else:
            ...
```

**JavaScript / TypeScript**

```typescript Basic text streaming
const stream = await model.stream("Why do parrots have colorful feathers?");
for await (const chunk of stream) {
  console.log(chunk.text)
}
```

```typescript Stream tool calls, reasoning, and other content
const stream = await model.stream("What color is the sky?");
for await (const chunk of stream) {
  for (const block of chunk.contentBlocks) {
    if (block.type === "reasoning") {
      console.log(`Reasoning: ${block.reasoning}`);
    } else if (block.type === "tool_call_chunk") {
      console.log(`Tool call chunk: ${block}`);
    } else if (block.type === "text") {
      console.log(block.text);
    } else {
      ...
    }
  }
}
```

As opposed to [`invoke()`](#invoke), which returns a single `AIMessage`[AIMessage] after the model has finished generating its full response, `stream()` returns multiple `AIMessageChunk`[AIMessageChunk] objects, each containing a portion of the output text. Importantly, each chunk in a stream is designed to be gathered into a full message via summation:

**Python**
```python Construct an AIMessage
full = None  # None | AIMessageChunk
for chunk in model.stream("What color is the sky?"):
    full = chunk if full is None else full + chunk
    print(full.text)

# The
# The sky
# The sky is
# The sky is typically
# The sky is typically blue
# ...

print(full.content_blocks)
# [{"type": "text", "text": "The sky is typically blue..."}]
```

**JavaScript / TypeScript**
```typescript Construct AIMessage
let full: AIMessageChunk | null = null;
for await (const chunk of stream) {
  full = full ? full.concat(chunk) : chunk;
  console.log(full.text);
}

// The
// The sky
// The sky is
// The sky is typically
// The sky is typically blue
// ...

console.log(full.contentBlocks);
// [{"type": "text", "text": "The sky is typically blue..."}]
```

The resulting message can be treated the same as a message that was generated with [`invoke()`](#invoke)—for example, it can be aggregated into a message history and passed back to the model as conversational context.

**Warning**
    Streaming only works if all steps in the program know how to process a stream of chunks. For instance, an application that isn't streaming-capable would be one that needs to store the entire output in memory before it can be processed.

**Advanced streaming topics**
**Streaming events**
**Python**
        LangChain chat models can also stream semantic events using `astream_events()`.

        This simplifies filtering based on event types and other metadata, and will aggregate the full message in the background. See below for an example.

```python
async for event in model.astream_events("Hello"):

    if event["event"] == "on_chat_model_start":
        print(f"Input: {event['data']['input']}")

    elif event["event"] == "on_chat_model_stream":
        print(f"Token: {event['data']['chunk'].text}")

    elif event["event"] == "on_chat_model_end":
        print(f"Full message: {event['data']['output'].text}")

    else:
        pass
```
```txt
Input: Hello
Token: Hi
Token:  there
Token: !
Token:  How
Token:  can
Token:  I
...
Full message: Hi there! How can I help today?
```

**Tip**
            See the `astream_events()`[BaseChatModel.astream_events] reference for event types and other details.

**JavaScript / TypeScript**
        LangChain chat models can also stream semantic events using
        [`streamEvents()`][BaseChatModel.streamEvents].

        This simplifies filtering based on event types and other metadata, and will aggregate the full message in the background. See below for an example.

```typescript
const stream = await model.streamEvents("Hello");
for await (const event of stream) {
    if (event.event === "on_chat_model_start") {
        console.log(`Input: ${event.data.input}`);
    }
    if (event.event === "on_chat_model_stream") {
        console.log(`Token: ${event.data.chunk.text}`);
    }
    if (event.event === "on_chat_model_end") {
        console.log(`Full message: ${event.data.output.text}`);
    }
}
```
```txt
Input: Hello
Token: Hi
Token:  there
Token: !
Token:  How
Token:  can
Token:  I
...
Full message: Hi there! How can I help today?
```

        See the `streamEvents()`[BaseChatModel.streamEvents] reference for event types and other details.

****
        LangChain simplifies streaming from chat models by automatically enabling streaming mode in certain cases, even when you're not explicitly calling the streaming methods. This is particularly useful when you use the non-streaming invoke method but still want to stream the entire application, including intermediate results from the chat model.

        In [LangGraph agents](../langchain/agents.md), for example, you can call `model.invoke()` within nodes, but LangChain will automatically delegate to streaming if running in a streaming mode.

        #### How it works

        When you `invoke()` a chat model, LangChain will automatically switch to an internal streaming mode if it detects that you are trying to stream the overall application. The result of the invocation will be the same as far as the code that was using invoke is concerned; however, while the chat model is being streamed, LangChain will take care of invoking `on_llm_new_token` events in LangChain's callback system.

**Python**
        Callback events allow LangGraph `stream()` and `astream_events()` to surface the chat model's output in real-time.

**JavaScript / TypeScript**
        Callback events allow LangGraph `stream()` and `streamEvents()` to surface the chat model's output in real-time.

### Batch

Batching a collection of independent requests to a model can significantly improve performance and reduce costs, as the processing can be done in parallel:

**Python**
```python Batch
responses = model.batch([
    "Why do parrots have colorful feathers?",
    "How do airplanes fly?",
    "What is quantum computing?"
])
for response in responses:
    print(response)
```

**Note**
    This section describes a chat model method `batch()`[BaseChatModel.batch], which parallelizes model calls client-side.

    It is **distinct** from batch APIs supported by inference providers, such as OpenAI or Anthropic.

By default, `batch()`[BaseChatModel.batch] will only return the final output for the entire batch. If you want to receive the output for each individual input as it finishes generating, you can stream results with `batch_as_completed()`[BaseChatModel.batch_as_completed]:

```python Yield batch responses upon completion
for response in model.batch_as_completed([
    "Why do parrots have colorful feathers?",
    "How do airplanes fly?",
    "What is quantum computing?"
]):
    print(response)
```
**Note**
    When using `batch_as_completed()`[BaseChatModel.batch_as_completed], results may arrive out of order. Each includes the input index for matching to reconstruct the original order as needed.

**Tip**
    When processing a large number of inputs using `batch()`[BaseChatModel.batch] or `batch_as_completed()`[BaseChatModel.batch_as_completed], you may want to control the maximum number of parallel calls. This can be done by setting the `max_concurrency`[RunnableConfig(max_concurrency)] attribute in the `RunnableConfig` dictionary.

```python Batch with max concurrency
model.batch(
    list_of_inputs,
    config={
        'max_concurrency': 5,  # Limit to 5 parallel calls
    }
)
```

    See the `RunnableConfig` reference for a full list of supported attributes.

For more details on batching, see the `reference`[BaseChatModel.batch].

**JavaScript / TypeScript**
```typescript Batch
const responses = await model.batch([
  "Why do parrots have colorful feathers?",
  "How do airplanes fly?",
  "What is quantum computing?",
  "Why do parrots have colorful feathers?",
  "How do airplanes fly?",
  "What is quantum computing?",
]);
for (const response of responses) {
  console.log(response);
}
```

**Tip**
    When processing a large number of inputs using `batch()`, you may want to control the maximum number of parallel calls. This can be done by setting the `maxConcurrency` attribute in the `RunnableConfig` dictionary.

```typescript Batch with max concurrency
model.batch(
  listOfInputs,
  {
    maxConcurrency: 5,  // Limit to 5 parallel calls
  }
)
```

    See the `RunnableConfig` reference for a full list of supported attributes.

For more details on batching, see the `reference`[BaseChatModel.batch].

---

## Tool calling

Models can request to call tools that perform tasks such as fetching data from a database, searching the web, or running code. Tools are pairings of:

1. A schema, including the name of the tool, a description, and/or argument definitions (often a JSON schema)
2. A function or coroutine to execute.

**Note**
    You may hear the term "function calling". We use this interchangeably with "tool calling".

Here's the basic tool calling flow between a user and a model:

**Python**
```mermaid
sequenceDiagram
    participant U as User
    participant M as Model
    participant T as Tools

    U->>M: "What's the weather in SF and NYC?"
    M->>M: Analyze request & decide tools needed

    par Parallel Tool Calls
        M->>T: get_weather("San Francisco")
        M->>T: get_weather("New York")
    end

    par Tool Execution
        T-->>M: SF weather data
        T-->>M: NYC weather data
    end

    M->>M: Process results & generate response
    M->>U: "SF: 72°F sunny, NYC: 68°F cloudy"
```

**JavaScript / TypeScript**
```mermaid
sequenceDiagram
    participant U as User
    participant M as Model
    participant T as Tools

    U->>M: "What's the weather in SF and NYC?"
    M->>M: Analyze request & decide tools needed

    par Parallel Tool Calls
        M->>T: getWeather("San Francisco")
        M->>T: getWeather("New York")
    end

    par Tool Execution
        T-->>M: SF weather data
        T-->>M: NYC weather data
    end

    M->>M: Process results & generate response
    M->>U: "SF: 72°F sunny, NYC: 68°F cloudy"
```

**Python**
To make tools that you have defined available for use by a model, you must bind them using `bind_tools`[BaseChatModel.bind_tools]. In subsequent invocations, the model can choose to call any of the bound tools as needed.

**JavaScript / TypeScript**
To make tools that you have defined available for use by a model, you must bind them using `bindTools`[BaseChatModel.bindTools]. In subsequent invocations, the model can choose to call any of the bound tools as needed.

Some model providers offer built-in tools that can be enabled via model or invocation parameters (e.g. `ChatOpenAI`, `ChatAnthropic`). Check the respective provider reference for details.

**Tip**
    See the tools guide for details and other options for creating tools.

**Python**
```python Binding user tools
from langchain.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get the weather at a location."""
    return f"It's sunny in {location}."

model_with_tools = model.bind_tools([get_weather])  # [!code highlight]

response = model_with_tools.invoke("What's the weather like in Boston?")
for tool_call in response.tool_calls:
    # View tool calls made by the model
    print(f"Tool: {tool_call['name']}")
    print(f"Args: {tool_call['args']}")
```

**JavaScript / TypeScript**
```typescript Binding user tools
import { tool } from "langchain";
import * as z from "zod";
import { ChatOpenAI } from "@langchain/openai";

const getWeather = tool(
  (input) => `It's sunny in ${input.location}.`,
  {
    name: "get_weather",
    description: "Get the weather at a location.",
    schema: z.object({
      location: z.string().describe("The location to get the weather for"),
    }),
  },
);

const model = new ChatOpenAI({ model: "gpt-5.5" });
const modelWithTools = model.bindTools([getWeather]);  // [!code highlight]

const response = await modelWithTools.invoke("What's the weather like in Boston?");
const toolCalls = response.tool_calls || [];
for (const tool_call of toolCalls) {
  // View tool calls made by the model
  console.log(`Tool: ${tool_call.name}`);
  console.log(`Args: ${tool_call.args}`);
}
```

When binding user-defined tools, the model's response includes a **request** to execute a tool. When using a model separately from an [agent](../langchain/agents.md), it is up to you to execute the requested tool and return the result back to the model for use in subsequent reasoning. When using an [agent](../langchain/agents.md), the agent loop will handle the tool execution loop for you.

Below, we show some common ways you can use tool calling.

**Tool execution loop**
        When a model returns tool calls, you need to execute the tools and pass the results back to the model. This creates a conversation loop where the model can use tool results to generate its final response. LangChain includes [agent](../langchain/agents.md) abstractions that handle this orchestration for you.

        Here's a simple example of how to do this:

**Python**

```python Tool execution loop
# Bind (potentially multiple) tools to the model
model_with_tools = model.bind_tools([get_weather])

# Step 1: Model generates tool calls
messages = [{"role": "user", "content": "What's the weather in Boston?"}]
ai_msg = model_with_tools.invoke(messages)
messages.append(ai_msg)

# Step 2: Execute tools and collect results
for tool_call in ai_msg.tool_calls:
    # Execute the tool with the generated arguments
    tool_result = get_weather.invoke(tool_call)
    messages.append(tool_result)

# Step 3: Pass results back to model for final response
final_response = model_with_tools.invoke(messages)
print(final_response.text)
# "The current weather in Boston is 72°F and sunny."
```

**JavaScript / TypeScript**

```typescript Tool execution loop
// Bind (potentially multiple) tools to the model
const modelWithTools = model.bindTools([get_weather])

// Step 1: Model generates tool calls
const messages = [{"role": "user", "content": "What's the weather in Boston?"}]
const ai_msg = await modelWithTools.invoke(messages)
messages.push(ai_msg)

// Step 2: Execute tools and collect results
for (const tool_call of ai_msg.tool_calls) {
    // Execute the tool with the generated arguments
    const tool_result = await get_weather.invoke(tool_call)
    messages.push(tool_result)
}

// Step 3: Pass results back to model for final response
const final_response = await modelWithTools.invoke(messages)
console.log(final_response.text)
// "The current weather in Boston is 72°F and sunny."
```

        Each `ToolMessage` returned by the tool includes a `tool_call_id` that matches the original tool call, helping the model correlate results with requests.

**Forcing tool calls**
        By default, the model has the freedom to choose which bound tool to use based on the user's input. However, you might want to force choosing a tool, ensuring the model uses either a particular tool or **any** tool from a given list:

**Python**

```python Force use of any tool
model_with_tools = model.bind_tools([tool_1], tool_choice="any")
```
```python Force use of specific tools
model_with_tools = model.bind_tools([tool_1], tool_choice="tool_1")
```

**JavaScript / TypeScript**

```typescript Force use of any tool
const modelWithTools = model.bindTools([tool_1], { toolChoice: "any" })
```
```typescript Force use of specific tools
const modelWithTools = model.bindTools([tool_1], { toolChoice: "tool_1" })
```

**Parallel tool calls**
        Many models support calling multiple tools in parallel when appropriate. This allows the model to gather information from different sources simultaneously.

**Python**

```python Parallel tool calls
model_with_tools = model.bind_tools([get_weather])

response = model_with_tools.invoke(
    "What's the weather in Boston and Tokyo?"
)

# The model may generate multiple tool calls
print(response.tool_calls)
# [
#   {'name': 'get_weather', 'args': {'location': 'Boston'}, 'id': 'call_1'},
#   {'name': 'get_weather', 'args': {'location': 'Tokyo'}, 'id': 'call_2'},
# ]

# Execute all tools (can be done in parallel with async)
results = []
for tool_call in response.tool_calls:
    if tool_call['name'] == 'get_weather':
        result = get_weather.invoke(tool_call)
    ...
    results.append(result)
```

**JavaScript / TypeScript**

```typescript Parallel tool calls
const modelWithTools = model.bind_tools([get_weather])

const response = await modelWithTools.invoke(
    "What's the weather in Boston and Tokyo?"
)

// The model may generate multiple tool calls
console.log(response.tool_calls)
// [
//   { name: 'get_weather', args: { location: 'Boston' }, id: 'call_1' },
//   { name: 'get_time', args: { location: 'Tokyo' }, id: 'call_2' }
// ]

// Execute all tools (can be done in parallel with async)
const results = []
for (const tool_call of response.tool_calls || []) {
    if (tool_call.name === 'get_weather') {
        const result = await get_weather.invoke(tool_call)
        results.push(result)
    }
}
```

        The model intelligently determines when parallel execution is appropriate based on the independence of the requested operations.

**Tip**
        Most models supporting tool calling enable parallel tool calls by default. Some (including OpenAI and Anthropic) allow you to disable this feature. To do this, set `parallel_tool_calls=False`:
```python
model.bind_tools([get_weather], parallel_tool_calls=False)
```

**Streaming tool calls**
        When streaming responses, tool calls are progressively built through `ToolCallChunk`. This allows you to see tool calls as they're being generated rather than waiting for the complete response.

**Python**

```python Streaming tool calls
for chunk in model_with_tools.stream(
    "What's the weather in Boston and Tokyo?"
):
    # Tool call chunks arrive progressively
    for tool_chunk in chunk.tool_call_chunks:
        if name := tool_chunk.get("name"):
            print(f"Tool: {name}")
        if id_ := tool_chunk.get("id"):
            print(f"ID: {id_}")
        if args := tool_chunk.get("args"):
            print(f"Args: {args}")

# Output:
# Tool: get_weather
# ID: call_SvMlU1TVIZugrFLckFE2ceRE
# Args: {"lo
# Args: catio
# Args: n": "B
# Args: osto
# Args: n"}
# Tool: get_weather
# ID: call_QMZdy6qInx13oWKE7KhuhOLR
# Args: {"lo
# Args: catio
# Args: n": "T
# Args: okyo
# Args: "}
```

        You can accumulate chunks to build complete tool calls:

```python Accumulate tool calls
gathered = None
for chunk in model_with_tools.stream("What's the weather in Boston?"):
    gathered = chunk if gathered is None else gathered + chunk
    print(gathered.tool_calls)
```

**JavaScript / TypeScript**

```typescript Streaming tool calls
const stream = await modelWithTools.stream(
    "What's the weather in Boston and Tokyo?"
)
for await (const chunk of stream) {
    // Tool call chunks arrive progressively
    if (chunk.tool_call_chunks) {
        for (const tool_chunk of chunk.tool_call_chunks) {
        console.log(`Tool: ${tool_chunk.get('name', '')}`)
        console.log(`Args: ${tool_chunk.get('args', '')}`)
        }
    }
}

// Output:
// Tool: get_weather
// Args:
// Tool:
// Args: {"loc
// Tool:
// Args: ation": "BOS"}
// Tool: get_time
// Args:
// Tool:
// Args: {"timezone": "Tokyo"}
```

        You can accumulate chunks to build complete tool calls:

```typescript Accumulate tool calls
let full: AIMessageChunk | null = null
const stream = await modelWithTools.stream("What's the weather in Boston?")
for await (const chunk of stream) {
    full = full ? full.concat(chunk) : chunk
    console.log(full.contentBlocks)
}
```

---

## Structured output

Models can be requested to provide their response in a format matching a given schema. This is useful for ensuring the output can be easily parsed and used in subsequent processing. LangChain supports multiple schema types and methods for enforcing structured output.

**Tip**
    To learn about structured output, see [Structured output](../langchain/structured-output.md).

**Python**

**Pydantic**
        Pydantic models provide the richest feature set with field validation, descriptions, and nested structures.

```python
from pydantic import BaseModel, Field

class Movie(BaseModel):
    """A movie with details."""
    title: str = Field(description="The title of the movie")
    year: int = Field(description="The year the movie was released")
    director: str = Field(description="The director of the movie")
    rating: float = Field(description="The movie's rating out of 10")

model_with_structure = model.with_structured_output(Movie)
response = model_with_structure.invoke("Provide details about the movie Inception")
print(response)  # Movie(title="Inception", year=2010, director="Christopher Nolan", rating=8.8)
```

**TypedDict**
        Python's `TypedDict` provides a simpler alternative to Pydantic models, ideal when you don't need runtime validation.

```python
from typing_extensions import TypedDict, Annotated

class MovieDict(TypedDict):
    """A movie with details."""
    title: Annotated[str, ..., "The title of the movie"]
    year: Annotated[int, ..., "The year the movie was released"]
    director: Annotated[str, ..., "The director of the movie"]
    rating: Annotated[float, ..., "The movie's rating out of 10"]

model_with_structure = model.with_structured_output(MovieDict)
response = model_with_structure.invoke("Provide details about the movie Inception")
print(response)  # {'title': 'Inception', 'year': 2010, 'director': 'Christopher Nolan', 'rating': 8.8}
```

**JSON Schema**
        Provide a JSON Schema for maximum control and interoperability.

```python
import json

json_schema = {
    "title": "Movie",
    "description": "A movie with details",
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "The title of the movie"
        },
        "year": {
            "type": "integer",
            "description": "The year the movie was released"
        },
        "director": {
            "type": "string",
            "description": "The director of the movie"
        },
        "rating": {
            "type": "number",
            "description": "The movie's rating out of 10"
        }
    },
    "required": ["title", "year", "director", "rating"]
}

model_with_structure = model.with_structured_output(
    json_schema,
    method="json_schema",
)
response = model_with_structure.invoke("Provide details about the movie Inception")
print(response)  # {'title': 'Inception', 'year': 2010, ...}
```

**JavaScript / TypeScript**

**Zod**
        A zod schema is the preferred method of defining an output schema. Note that when a zod schema is provided, the model output will also be validated against the schema using zod's parse methods.

```typescript
import * as z from "zod";

const Movie = z.object({
  title: z.string().describe("The title of the movie"),
  year: z.number().describe("The year the movie was released"),
  director: z.string().describe("The director of the movie"),
  rating: z.number().describe("The movie's rating out of 10"),
});

const modelWithStructure = model.withStructuredOutput(Movie);

const response = await modelWithStructure.invoke("Provide details about the movie Inception");
console.log(response);
// {
//   title: "Inception",
//   year: 2010,
//   director: "Christopher Nolan",
//   rating: 8.8,
// }
```

**JSON Schema**
        For maximum control or interoperability, you can provide a raw JSON Schema.

```typescript
const jsonSchema = {
  "title": "Movie",
  "description": "A movie with details",
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "The title of the movie",
    },
    "year": {
      "type": "integer",
      "description": "The year the movie was released",
    },
    "director": {
      "type": "string",
      "description": "The director of the movie",
    },
    "rating": {
      "type": "number",
      "description": "The movie's rating out of 10",
    },
  },
  "required": ["title", "year", "director", "rating"],
}

const modelWithStructure = model.withStructuredOutput(
  jsonSchema,
  { method: "jsonSchema" },
)

const response = await modelWithStructure.invoke("Provide details about the movie Inception")
console.log(response)  // {'title': 'Inception', 'year': 2010, ...}
```

**Standard Schema**
        Any schema from a library implementing the Standard Schema specification is also supported. Standard Schema objects are validated at runtime via the schema's `~standard.validate()` method.

```typescript
import * as v from "valibot";
import { toStandardJsonSchema } from "@valibot/to-json-schema";

const Movie = toStandardJsonSchema(
  v.object({
    title: v.pipe(v.string(), v.description("The title of the movie")),
    year: v.pipe(v.number(), v.description("The year the movie was released")),
    director: v.pipe(v.string(), v.description("The director of the movie")),
    rating: v.pipe(v.number(), v.description("The movie's rating out of 10")),
  })
);

const modelWithStructure = model.withStructuredOutput(Movie);

const response = await modelWithStructure.invoke("Provide details about the movie Inception");
console.log(response);
// {
//   title: "Inception",
//   year: 2010,
//   director: "Christopher Nolan",
//   rating: 8.8,
// }
```

**Python**
**Note**
    **Key considerations for structured output**

    - **Method parameter**: Some providers support different methods for structured output:
        - `'json_schema'`: Uses dedicated structured output features offered by the provider.
        - `'function_calling'`: Derives structured output by forcing a [tool call](#tool-calling) that follows the given schema.
        - `'json_mode'`: A precursor to `'json_schema'` offered by some providers. Generates valid JSON, but the schema must be described in the prompt.
    - **Include raw**: Set `include_raw=True` to get both the parsed output and the raw AI message.
    - **Validation**: Pydantic models provide automatic validation. `TypedDict` and JSON Schema require manual validation.

    See your provider's integration page for supported methods and configuration options.

**JavaScript / TypeScript**
**Note**
    **Key considerations for structured output:**

    - **Method parameter**: Some providers support different methods (`'jsonSchema'`, `'functionCalling'`, `'jsonMode'`)
    - **Include raw**: Use `includeRaw: true`[BaseChatModel.with_structured_output(include_raw)] to get both the parsed output and the raw `AIMessage`
    - **Validation**: Zod and Standard Schema objects provide automatic validation, while JSON Schema requires manual validation
    - **Standard Schema**: Any schema library implementing the Standard Schema spec is supported and validated at runtime

    See your provider's integration page for supported methods and configuration options.

**Example: Message output alongside parsed structure**

It can be useful to return the raw `AIMessage` object alongside the parsed representation to access response metadata such as [token counts](#token-usage). To do this, set `include_raw=True`[BaseChatModel.with_structured_output(include_raw)] when calling `with_structured_output`[BaseChatModel.with_structured_output]:

**Python**
```python
from pydantic import BaseModel, Field

class Movie(BaseModel):
    """A movie with details."""
    title: str = Field(description="The title of the movie")
    year: int = Field(description="The year the movie was released")
    director: str = Field(description="The director of the movie")
    rating: float = Field(description="The movie's rating out of 10")

model_with_structure = model.with_structured_output(Movie, include_raw=True)  # [!code highlight]
response = model_with_structure.invoke("Provide details about the movie Inception")
response
# {
#     "raw": AIMessage(...),
#     "parsed": Movie(title=..., year=..., ...),
#     "parsing_error": None,
# }
```

**JavaScript / TypeScript**
```typescript
import * as z from "zod";

const Movie = z.object({
  title: z.string().describe("The title of the movie"),
  year: z.number().describe("The year the movie was released"),
  director: z.string().describe("The director of the movie"),
  rating: z.number().describe("The movie's rating out of 10"),
  title: z.string().describe("The title of the movie"),
  year: z.number().describe("The year the movie was released"),
  director: z.string().describe("The director of the movie"),  // [!code highlight]
  rating: z.number().describe("The movie's rating out of 10"),
});

const modelWithStructure = model.withStructuredOutput(Movie, { includeRaw: true });

const response = await modelWithStructure.invoke("Provide details about the movie Inception");
console.log(response);
// {
//   raw: AIMessage { ... },
//   parsed: { title: "Inception", ... }
// }
```

**Example: Nested structures**
    Schemas can be nested:
**Python**

```python Pydantic BaseModel
from pydantic import BaseModel, Field

class Actor(BaseModel):
    name: str
    role: str

class MovieDetails(BaseModel):
    title: str
    year: int
    cast: list[Actor]
    genres: list[str]
    budget: float | None = Field(None, description="Budget in millions USD")

model_with_structure = model.with_structured_output(MovieDetails)
```

```python TypedDict
from typing_extensions import Annotated, TypedDict

class Actor(TypedDict):
    name: str
    role: str

class MovieDetails(TypedDict):
    title: str
    year: int
    cast: list[Actor]
    genres: list[str]
    budget: Annotated[float | None, ..., "Budget in millions USD"]

model_with_structure = model.with_structured_output(MovieDetails)
```

**JavaScript / TypeScript**
```typescript
import * as z from "zod";

const Actor = z.object({
  name: z.string(),
  role: z.string(),
});

const MovieDetails = z.object({
  title: z.string(),
  year: z.number(),
  cast: z.array(Actor),
  genres: z.array(z.string()),
  budget: z.number().nullable().describe("Budget in millions USD"),
});

const modelWithStructure = model.withStructuredOutput(MovieDetails);
```

---

## Advanced topics

### Model profiles

**Info**
    Model profiles require `langchain>=1.1`.

**Python**
LangChain chat models can expose a dictionary of supported features and capabilities through a `profile` attribute:

```python
model.profile
# {
#   "max_input_tokens": 400000,
#   "image_inputs": True,
#   "reasoning_output": True,
#   "tool_calling": True,
#   ...
# }
```

Refer to the full set of fields in the API reference.

Much of the model profile data is powered by the models.dev project, an open source initiative that provides model capability data. These data are augmented with additional fields for purposes of use with LangChain. These augmentations are kept aligned with the upstream project as it evolves.

Model profile data allow applications to work around model capabilities dynamically. For example:

1. [Summarization middleware](../langchain/middleware.md#summarization) can trigger summarization based on a model's context window size.
2. [Structured output](../langchain/structured-output.md) strategies in `create_agent` can be inferred automatically (e.g., by checking support for native structured output features).
3. Model inputs can be gated based on supported [modalities](#multimodal) and maximum input tokens.
4. Deep Agents Code filters the interactive model switcher to models whose profiles report `tool_calling` support and text I/O, and displays context window sizes and capability flags in the selector detail view.

**Updating or overwriting profile data**
    Model profile data can be changed if it is missing, stale, or incorrect.

    **Option 1 (quick fix)**

    You can instantiate a chat model with any valid profile:

```python
custom_profile = {
    "max_input_tokens": 100_000,
    "tool_calling": True,
    "structured_output": True,
    # ...
}
model = init_chat_model("...", profile=custom_profile)
```

    The `profile` is also a regular `dict` and can be updated in place. If the model instance is shared, consider using `model_copy` to avoid mutating shared state.

```python
new_profile = model.profile | {"key": "value"}
model.model_copy(update={"profile": new_profile})
```

    **Option 2 (fix data upstream)**

    The primary source for the data is the models.dev project. This data is merged with additional fields and overrides in LangChain integration packages and are shipped with those packages.

    Model profile data can be updated through the following process:

    1. (If needed) update the source data at models.dev through a pull request to its repository on GitHub.
    2. (If needed) update additional fields and overrides in `langchain_<package>/data/profile_augmentations.toml` through a pull request to the LangChain integration package`.
    3. Use the `langchain-model-profiles` CLI tool to pull the latest data from models.dev, merge in the augmentations and update the profile data:

```bash pip
pip install -U langchain-model-profiles
```

```bash uv
uv add langchain-model-profiles
```

```bash
langchain-profiles refresh --provider <provider> --data-dir <data_dir>
```

    This command:
    - Downloads the latest data for `<provider>` from models.dev
    - Merges augmentations from `profile_augmentations.toml` in `<data_dir>`
    - Writes merged profiles to `profiles.py` in `<data_dir>`

    For example: from `libs/partners/anthropic` in the LangChain monorepo:

```bash
uv run --with langchain-model-profiles --provider anthropic --data-dir langchain_anthropic/data
```

**JavaScript / TypeScript**
LangChain chat models can expose a dictionary of supported features and capabilities through a `profile` property:

```typescript
model.profile;
// {
//   maxInputTokens: 400000,
//   imageInputs: true,
//   reasoningOutput: true,
//   toolCalling: true,
//   ...
// }
```

Refer to the full set of fields in the API reference.

Much of the model profile data is powered by the models.dev project, an open source initiative that provides model capability data. This data is augmented with additional fields for purposes of use with LangChain. These augmentations are kept aligned with the upstream project as it evolves.

Model profile data allow applications to work around model capabilities dynamically. For example:

1. [Summarization middleware](../langchain/middleware.md#summarization) can trigger summarization based on a model's context window size.
2. [Structured output](../langchain/structured-output.md) strategies in `createAgent` can be inferred automatically (e.g., by checking support for native structured output features).
3. Model inputs can be gated based on supported [modalities](#multimodal) and maximum input tokens.
4. Deep Agents Code filters the interactive model switcher to models whose profiles report `tool_calling` support and text I/O, and displays context window sizes and capability flags in the selector detail view.

**Modify profile data**
    Model profile data can be changed if it is missing, stale, or incorrect.

    **Option 1 (quick fix)**

    You can instantiate a chat model with any valid profile:

```typescript
const customProfile = {
maxInputTokens: 100_000,
toolCalling: true,
structuredOutput: true,
// ...
};
const model = initChatModel("...", { profile: customProfile });
```

    **Option 2 (fix data upstream)**

    The primary source for the data is the models.dev project. These data are merged with additional fields and overrides in LangChain integration packages and are shipped with those packages.

    Model profile data can be updated through the following process:

    1. (If needed) update the source data at models.dev through a pull request to its repository on GitHub.
    2. (If needed) update additional fields and overrides in `langchain-<package>/profiles.toml` through a pull request to the LangChain integration package.

**Warning**
    Model profiles are a beta feature. The format of a profile is subject to change.

### Multimodal

Certain models can process and return non-textual data such as images, audio, and video. You can pass non-textual data to a model by providing content blocks.

**Tip**
    All LangChain chat models with underlying multimodal capabilities support:

    1. Data in the cross-provider standard format (see our messages guide)
    2. OpenAI chat completions format
    3. Any format that is native to that specific provider (e.g., Anthropic models accept Anthropic native format)

See the multimodal section of the messages guide for details.

Some models can return multimodal data as part of their response. If invoked to do so, the resulting `AIMessage` will have content blocks with multimodal types.

**Python**
```python Multimodal output
response = model.invoke("Create a picture of a cat")
print(response.content_blocks)
# [
#     {"type": "text", "text": "Here's a picture of a cat"},
#     {"type": "image", "base64": "...", "mime_type": "image/jpeg"},
# ]
```

**JavaScript / TypeScript**
```typescript Multimodal output
const response = await model.invoke("Create a picture of a cat");
console.log(response.contentBlocks);
// [
//   { type: "text", text: "Here's a picture of a cat" },
//   { type: "image", data: "...", mimeType: "image/jpeg" },
// ]
```

See the integrations page for details on specific providers.

### Reasoning

Many models are capable of performing multi-step reasoning to arrive at a conclusion. This involves breaking down complex problems into smaller, more manageable steps.

**If supported by the underlying model,** you can surface this reasoning process to better understand how the model arrived at its final answer.

**Python**

```python Stream reasoning output
for chunk in model.stream("Why do parrots have colorful feathers?"):
    reasoning_steps = [r for r in chunk.content_blocks if r["type"] == "reasoning"]
    print(reasoning_steps if reasoning_steps else chunk.text)
```

```python Complete reasoning output
response = model.invoke("Why do parrots have colorful feathers?")
reasoning_steps = [b for b in response.content_blocks if b["type"] == "reasoning"]
print(" ".join(step["reasoning"] for step in reasoning_steps))
```

**JavaScript / TypeScript**

```typescript Stream reasoning output
const stream = model.stream("Why do parrots have colorful feathers?");
for await (const chunk of stream) {
    const reasoningSteps = chunk.contentBlocks.filter(b => b.type === "reasoning");
    console.log(reasoningSteps.length > 0 ? reasoningSteps : chunk.text);
}
```

```typescript Complete reasoning output
const response = await model.invoke("Why do parrots have colorful feathers?");
const reasoningSteps = response.contentBlocks.filter(b => b.type === "reasoning");
console.log(reasoningSteps.map(step => step.reasoning).join(" "));
```

Depending on the model, you can sometimes specify the level of effort it should put into reasoning. Similarly, you can request that the model turn off reasoning entirely. This may take the form of categorical "tiers" of reasoning (e.g., `'low'` or `'high'`) or integer token budgets.

**Python**
**Note**
    `reasoning_effort` as a standard parameter requires `langchain-core>=1.5.2`, plus the corresponding partner package version: `langchain-anthropic>=1.5.3`, `langchain-openai>=1.4.1`, `langchain-fireworks>=1.5.2`, `langchain-xai>=1.3.0`, `langchain-google-genai>=4.3.1`, or `langchain-aws>=1.6.5`.

`ChatOpenAI`, `ChatAnthropic`, `ChatFireworks`, `ChatXAI`, `ChatGoogleGenerativeAI`, and `ChatBedrockConverse` support a standard `reasoning_effort` parameter. Like `temperature`, it can be set at model construction or per invocation, and each provider translates it into its own API format:

```python
from langchain_anthropic import ChatAnthropic

model = ChatAnthropic(model="claude-sonnet-4-6")
response = model.invoke(
    "Why do parrots have colorful feathers?",
    reasoning_effort="high",
)
```

Supported effort levels and the provider's documented default vary by model. Check a model's [profile](#model-profiles) for the levels it supports and its default:

```python
model.profile["reasoning_effort_levels"]  # e.g. ['low', 'medium', 'high']
model.profile["reasoning_effort_default"]  # e.g. 'high'
```

Some providers also accept a native alias for `reasoning_effort` (for example, `ChatAnthropic` accepts `effort` and `ChatGoogleGenerativeAI` accepts `thinking_level`). See the chat model integrations page for provider-specific detail.

For details, see the integrations page or reference for your respective chat model.

### Local models

LangChain supports running models locally on your own hardware. This is useful for scenarios where either data privacy is critical, you want to invoke a custom model, or when you want to avoid the costs incurred when using a cloud-based model.

Ollama is one of the easiest ways to run chat and embedding models locally.

### Prompt caching

Many providers offer prompt caching features to reduce latency and cost on repeat processing of the same tokens. You can engage caching at three levels:

- **Implicit provider caching:** providers automatically pass on cost savings if a request hits a cache, with no configuration required. Examples: OpenAI and Gemini.
- **Provider-level explicit controls:** providers let you manually indicate cache points for greater control or to guarantee cost savings. These mirror the underlying provider/API behavior. Examples:
    - `ChatOpenAI` (via `prompt_cache_key`)
    - Anthropic content-block `cache_control`
    - Gemini.
**Python**
    - AWS Bedrock `cachePoint` blocks
- **LangChain middleware:** for agents, middleware lets LangChain optimize caching of stable system prompt and tool content. Examples:
    - Anthropic's `AnthropicPromptCachingMiddleware`
    - AWS Bedrock's `BedrockPromptCachingMiddleware`

**Warning**
    Prompt caching is often only engaged above a minimum input token threshold. See provider pages for details.

Cache usage will be reflected in the usage metadata of the model response.

### Server-side tool use

Some providers support server-side [tool-calling](#tool-calling) loops: models can interact with web search, code interpreters, and other tools and analyze the results in a single conversational turn.

If a model invokes a tool server-side, the content of the response message will include content representing the invocation and result of the tool. Accessing the content blocks of the response will return the server-side tool calls and results in a provider-agnostic format:

**Python**
```python Invoke with server-side tool use
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-5.4-mini")

tool = {"type": "web_search"}
model_with_tools = model.bind_tools([tool])

response = model_with_tools.invoke("What was a positive news story from today?")
print(response.content_blocks)
```
```python Result expandable
[
    {
        "type": "server_tool_call",
        "name": "web_search",
        "args": {
            "query": "positive news stories today",
            "type": "search"
        },
        "id": "ws_abc123"
    },
    {
        "type": "server_tool_result",
        "tool_call_id": "ws_abc123",
        "status": "success"
    },
    {
        "type": "text",
        "text": "Here are some positive news stories from today...",
        "annotations": [
            {
                "end_index": 410,
                "start_index": 337,
                "title": "article title",
                "type": "citation",
                "url": "..."
            }
        ]
    }
]
```

**JavaScript / TypeScript**
```typescript
import { initChatModel } from "langchain";

const model = await initChatModel("gpt-5.4-mini");
const modelWithTools = model.bindTools([{ type: "web_search" }])

const message = await modelWithTools.invoke("What was a positive news story from today?");
console.log(message.contentBlocks);
```

This represents a single conversational turn; there are no associated ToolMessage objects that need to be passed in as in client-side [tool-calling](#tool-calling).

See the integration page for your given provider for available tools and usage details.

**Python**
### Rate limiting

Many chat model providers impose a limit on the number of invocations that can be made in a given time period. If you hit a rate limit, you will typically receive a rate limit error response from the provider, and will need to wait before making more requests.

To help manage rate limits, chat model integrations accept a `rate_limiter` parameter that can be provided during initialization to control the rate at which requests are made.

**Initialize and use a rate limiter**
    LangChain in comes with (an optional) built-in `InMemoryRateLimiter`. This limiter is thread safe and can be shared by multiple threads in the same process.

```python Define a rate limiter
from langchain.rate_limiters import InMemoryRateLimiter

rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.1,  # 1 request every 10s
    check_every_n_seconds=0.1,  # Check every 100ms whether allowed to make a request
    max_bucket_size=10,  # Controls the maximum burst size.
)

model = init_chat_model(
    model="gpt-5.5",
    model_provider="openai",
    rate_limiter=rate_limiter  # [!code highlight]
)
```

**Warning**
        The provided rate limiter can only limit the number of requests per unit time. It will not help if you need to also limit based on the size of the requests.

### Base URL and proxy settings

You can configure a custom base URL for providers that implement the OpenAI Chat Completions API.

**Warning**
    `model_provider="openai"` (or direct `ChatOpenAI` usage) targets the official OpenAI API specification. Provider-specific fields from routers and proxies may not be extracted or preserved.

    For OpenRouter and LiteLLM, prefer the dedicated integrations:
    - OpenRouter via `ChatOpenRouter` (`langchain-openrouter`)
    - LiteLLM via `ChatLiteLLM` / `ChatLiteLLMRouter` (`langchain-litellm`)

**Custom base URL**
**Python**
    Many model providers offer OpenAI-compatible APIs (e.g., Together AI, vLLM). You can use `init_chat_model` with these providers by specifying the appropriate `base_url` parameter:

```python
model = init_chat_model(
    model="MODEL_NAME",
    model_provider="openai",
    base_url="BASE_URL",
    api_key="YOUR_API_KEY",
)
```

**JavaScript / TypeScript**
    Many model providers offer OpenAI-compatible APIs (e.g., Together AI, vLLM). You can use `initChatModel` with these providers by specifying the appropriate `base_url` parameter:

```python
model = initChatModel(
    "MODEL_NAME",
    {
        modelProvider: "openai",
        baseUrl: "BASE_URL",
        apiKey: "YOUR_API_KEY",
    }
)
```

**Note**
        When using direct chat model class instantiation, the parameter name may vary by provider. Check the respective reference for details.

**Python**
**HTTP proxy configuration**
    For deployments requiring HTTP proxies, some model integrations support proxy configuration:

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="gpt-5.5",
    openai_proxy="http://proxy.example.com:8080"
)
```

**Note**
    Proxy support varies by integration. Check the specific model provider's reference for proxy configuration options.

### Log probabilities

Certain models can be configured to return token-level log probabilities representing the likelihood of a given token by setting the `logprobs` parameter when initializing the model:

**Python**
```python
model = init_chat_model(
    model="gpt-5.5",
    model_provider="openai"
).bind(logprobs=True)

response = model.invoke("Why do parrots talk?")
print(response.response_metadata["logprobs"])
```

**JavaScript / TypeScript**
```typescript
const model = new ChatOpenAI({
    model: "gpt-5.5",
    logprobs: true,
});

const responseMessage = await model.invoke("Why do parrots talk?");

responseMessage.response_metadata.logprobs.content.slice(0, 5);
```

### Token usage

A number of model providers return token usage information as part of the invocation response. When available, this information will be included on the `AIMessage` objects produced by the corresponding model. For more details, see the messages guide.

**Python**
**Note**
    Some provider APIs, notably OpenAI and Azure OpenAI chat completions, require users opt-in to receiving token usage data in streaming contexts. See the streaming usage metadata section of the integration guide for details.

**Python**
You can track aggregate token counts across models in an application using either a callback or context manager, as shown below:

**Callback handler**
```python
from langchain.chat_models import init_chat_model
from langchain_core.callbacks import UsageMetadataCallbackHandler

model_1 = init_chat_model(model="gpt-5.4-mini")
model_2 = init_chat_model(model="claude-haiku-4-5-20251001")

callback = UsageMetadataCallbackHandler()
result_1 = model_1.invoke("Hello", config={"callbacks": [callback]})
result_2 = model_2.invoke("Hello", config={"callbacks": [callback]})
print(callback.usage_metadata)
```
```python
{
    'gpt-5.4-mini': {
        'input_tokens': 8,
        'output_tokens': 10,
        'total_tokens': 18,
        'input_token_details': {'audio': 0, 'cache_read': 0},
        'output_token_details': {'audio': 0, 'reasoning': 0}
    },
    'claude-haiku-4-5-20251001': {
        'input_tokens': 8,
        'output_tokens': 21,
        'total_tokens': 29,
        'input_token_details': {'cache_read': 0, 'cache_creation': 0}
    }
}
```

**Context manager**
```python
from langchain.chat_models import init_chat_model
from langchain_core.callbacks import get_usage_metadata_callback

model_1 = init_chat_model(model="gpt-5.4-mini")
model_2 = init_chat_model(model="claude-haiku-4-5-20251001")

with get_usage_metadata_callback() as cb:
    model_1.invoke("Hello")
    model_2.invoke("Hello")
    print(cb.usage_metadata)
```
```python
{
    'gpt-5.4-mini': {
        'input_tokens': 8,
        'output_tokens': 10,
        'total_tokens': 18,
        'input_token_details': {'audio': 0, 'cache_read': 0},
        'output_token_details': {'audio': 0, 'reasoning': 0}
    },
    'claude-haiku-4-5-20251001': {
        'input_tokens': 8,
        'output_tokens': 21,
        'total_tokens': 29,
        'input_token_details': {'cache_read': 0, 'cache_creation': 0}
    }
}
```

### Invocation config

**Python**
When invoking a model, you can pass additional configuration through the `config` parameter using a `RunnableConfig` dictionary. This provides run-time control over execution behavior, callbacks, and metadata tracking.

**JavaScript / TypeScript**
When invoking a model, you can pass additional configuration through the `config` parameter using a `RunnableConfig` object. This provides run-time control over execution behavior, callbacks, and metadata tracking.

Common configuration options include:

**Python**
```python Invocation with config
response = model.invoke(
    "Tell me a joke",
    config={
        "run_name": "joke_generation",      # Custom name for this run
        "tags": ["humor", "demo"],          # Tags for categorization
        "metadata": {"user_id": "123"},     # Custom metadata
        "callbacks": [my_callback_handler], # Callback handlers
    }
)
```

**JavaScript / TypeScript**
```typescript Invocation with config
const response = await model.invoke(
    "Tell me a joke",
    {
        runName: "joke_generation",      // Custom name for this run
        tags: ["humor", "demo"],          // Tags for categorization
        metadata: {"user_id": "123"},     // Custom metadata
        callbacks: [my_callback_handler], // Callback handlers
    }
)
```

These configuration values are particularly useful when:
- Debugging with LangSmith tracing
- Implementing custom logging or monitoring
- Controlling resource usage in production
- Tracking invocations across complex pipelines

**Python**
**Key configuration attributes**
- **`run_name`** (string)
        Identifies this specific invocation in logs and traces. Not inherited by sub-calls.
    

- **`tags`** (string[])
        Labels inherited by all sub-calls for filtering and organization in debugging tools.
    

- **`metadata`** (object)
        Custom key-value pairs for tracking additional context, inherited by all sub-calls.
    

- **`max_concurrency`** (number)
        Controls the maximum number of parallel calls when using `batch()`[BaseChatModel.batch] or `batch_as_completed()`[BaseChatModel.batch_as_completed].
    

- **`callbacks`** (array)
        Handlers for monitoring and responding to events during execution.
    

- **`recursion_limit`** (number)
        Maximum recursion depth for chains to prevent infinite loops in complex pipelines.
    

**JavaScript / TypeScript**
**Key configuration attributes**
- **`runName`** (string)
        Identifies this specific invocation in logs and traces. Not inherited by sub-calls.
    

- **`tags`** (string[])
        Labels inherited by all sub-calls for filtering and organization in debugging tools.
    

- **`metadata`** (object)
        Custom key-value pairs for tracking additional context, inherited by all sub-calls.
    

- **`maxConcurrency`** (number)
        Controls the maximum number of parallel calls when using `batch()`.
    

- **`callbacks`** (CallbackHandler[])
        Handlers for monitoring and responding to events during execution.
    

- **`recursion_limit`** (number)
        Maximum recursion depth for chains to prevent infinite loops in complex pipelines.
    

**Tip**
    See full `RunnableConfig` reference for all supported attributes.

**Python**
### Configurable models

You can also create a runtime-configurable model by specifying `configurable_fields`[BaseChatModel.configurable_fields]. If you don't specify a model value, then `'model'` and `'model_provider'` will be configurable by default.

```python
from langchain.chat_models import init_chat_model

configurable_model = init_chat_model(temperature=0)

configurable_model.invoke(
    "what's your name",
    config={"configurable": {"model": "gpt-5-nano"}},  # Run with GPT-5-Nano
)
configurable_model.invoke(
    "what's your name",
    config={"configurable": {"model": "claude-sonnet-4-6"}},  # Run with Claude
)
```

**Configurable model with default values**
    We can create a configurable model with default model values, specify which parameters are configurable, and add prefixes to configurable params:

```python
first_model = init_chat_model(
        model="gpt-5.4-mini",
        temperature=0,
        configurable_fields=("model", "model_provider", "temperature", "max_tokens"),
        config_prefix="first",  # Useful when you have a chain with multiple models
)

first_model.invoke("what's your name")
```

```python
first_model.invoke(
    "what's your name",
    config={
        "configurable": {
            "first_model": "claude-sonnet-4-6",
            "first_temperature": 0.5,
            "first_max_tokens": 100,
        }
    },
)
```

    See the `init_chat_model` reference for more details on `configurable_fields` and `config_prefix`.

**Using a configurable model declaratively**
    We can call declarative operations like `bind_tools`, `with_structured_output`, `with_configurable`, etc. on a configurable model and chain a configurable model in the same way that we would a regularly instantiated chat model object.

```python
from pydantic import BaseModel, Field

class GetWeather(BaseModel):
    """Get the current weather in a given location"""

        location: str = Field(description="The city and state, e.g. San Francisco, CA")

class GetPopulation(BaseModel):
    """Get the current population in a given location"""

        location: str = Field(description="The city and state, e.g. San Francisco, CA")

model = init_chat_model(temperature=0)
model_with_tools = model.bind_tools([GetWeather, GetPopulation])

model_with_tools.invoke(
    "what's bigger in 2024 LA or NYC", config={"configurable": {"model": "gpt-5.4-mini"}}
).tool_calls
```
```
[
    {
        'name': 'GetPopulation',
        'args': {'location': 'Los Angeles, CA'},
        'id': 'call_Ga9m8FAArIyEjItHmztPYA22',
        'type': 'tool_call'
    },
    {
        'name': 'GetPopulation',
        'args': {'location': 'New York, NY'},
        'id': 'call_jh2dEvBaAHRaw5JUDthOs7rt',
        'type': 'tool_call'
    }
]
```
```python
model_with_tools.invoke(
    "what's bigger in 2024 LA or NYC",
    config={"configurable": {"model": "claude-sonnet-4-6"}},
).tool_calls
```
```
[
    {
        'name': 'GetPopulation',
        'args': {'location': 'Los Angeles, CA'},
        'id': 'toolu_01JMufPf4F4t2zLj7miFeqXp',
        'type': 'tool_call'
    },
    {
        'name': 'GetPopulation',
        'args': {'location': 'New York City, NY'},
        'id': 'toolu_01RQBHcE8kEEbYTuuS8WqY1u',
        'type': 'tool_call'
    }
]
```

### Dynamic model selection

Dynamic models are selected at runtime based on the current state and context. This enables sophisticated routing logic and cost optimization.

**Python**

To use a dynamic model, create middleware using the `@wrap_model_call` decorator that modifies the model in the request:

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse

basic_model = ChatOpenAI(model="gpt-5.4-mini")
advanced_model = ChatOpenAI(model="gpt-5.5")

@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:
    """Choose model based on conversation complexity."""
    message_count = len(request.state["messages"])

    if message_count > 10:
        # Use an advanced model for longer conversations
        model = advanced_model
    else:
        model = basic_model

    return handler(request.override(model=model))

agent = create_agent(
    model=basic_model,  # Default model
    tools=tools,
    middleware=[dynamic_model_selection]
)
```

**Warning**
Pre-bound models (models with `bind_tools`[BaseChatModel.bind_tools] already called) are not supported when using structured output. If you need dynamic model selection with structured output, ensure the models passed to the middleware are not pre-bound.

**JavaScript / TypeScript**

To use a dynamic model, create middleware with `wrapModelCall` that modifies the model in the request:

```ts
import { ChatOpenAI } from "@langchain/openai";
import { createAgent, createMiddleware } from "langchain";

const basicModel = new ChatOpenAI({ model: "gpt-5.4-mini" });
const advancedModel = new ChatOpenAI({ model: "gpt-5.5" });

const dynamicModelSelection = createMiddleware({
  name: "DynamicModelSelection",
  wrapModelCall: (request, handler) => {
    // Choose model based on conversation complexity
    const messageCount = request.messages.length;

    return handler({
        ...request,
        model: messageCount > 10 ? advancedModel : basicModel,
    });
  },
});

const agent = createAgent({
  model: "gpt-5.4-mini", // Base model (used when messageCount ≤ 10)
  tools,
  middleware: [dynamicModelSelection],
});
```

For more details on middleware and advanced patterns, see the middleware documentation.

**Tip**
For model configuration details, see [Models](../langchain/models.md). For dynamic model selection patterns, see Dynamic model in middleware.
