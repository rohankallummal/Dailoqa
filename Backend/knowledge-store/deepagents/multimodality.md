---
type: Documentation Page
title: Multimodal inputs and outputs
description: Use images, audio, video, and documents with Deep Agents when your model supports multimodal inputs and tool results
product: deepagents
resource: /docs/deepagents/multimodality
source: /oss/deepagents/multimodal
tags:
  - deepagents
  - multimodality
timestamp: 2026-08-11T15:35:33Z
code_examples:
  - ../code/deepagents/multimodal-user-input.py
  - ../code/deepagents/multimodal-user-input.ts
  - ../code/deepagents/multimodal-capture-screenshot.py
  - ../code/deepagents/multimodal-capture-screenshot.ts
  - ../code/deepagents/multimodal-summarization.py
  - ../code/deepagents/multimodal-summarization.ts
---

# Multimodal inputs and outputs

Deep Agents supports multimodal workflows when you use a Large Language Model that accepts multimodal inputs and tool results or returns multimodal outputs. You can attach images and other media to user messages, read non-text files with the built-in `read_file` tool, and return multimodal content from custom tools.

Built-in context compression is primarily text-oriented. Plan multimodal workloads accordingly: store large media in a backend and pass references when possible.

## Multimodal user input

Pass multimodal content in the `messages` you send to the agent, using the same standard content blocks as LangChain chat models:

**Python**

Code example: [`code/deepagents/multimodal-user-input.py`](../code/deepagents/multimodal-user-input.py)

```python
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "What is in this screenshot?"},
            {"type": "image", "url": "https://example.com/screenshot.png"},
        ],
    }],
})
```

**JavaScript / TypeScript**

Code example: [`code/deepagents/multimodal-user-input.ts`](../code/deepagents/multimodal-user-input.ts)

```ts
const result = await agent.invoke({
  messages: [
    {
      role: "user",
      content: [
        { type: "text", text: "What is in this screenshot?" },
        { type: "image", url: "https://example.com/screenshot.png" },
      ],
    },
  ],
});
```

For block types, provider-specific requirements, and additional examples (PDF, audio, video), see Multimodal messages.

## Built-in `read_file` tool

The harness `read_file` tool returns standard content blocks for supported multimodal files instead of plain text. The agent can inspect images, documents, and media stored in its [filesystem](../deepagents/overview.md#virtual-filesystem-access) when the selected model supports the corresponding modality. Check the provider's documentation for your model's supported MIME types.

**Supported multimodal file extensions**

| Type | Extensions |
| ---- | ---------- |
| Image | `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.heic`, `.heif` |
| Video | `.mp4`, `.mpeg`, `.mov`, `.avi`, `.flv`, `.mpg`, `.webm`, `.wmv`, `.3gpp` |
| Audio | `.wav`, `.mp3`, `.aiff`, `.aac`, `.ogg`, `.flac` |
| File | `.pdf`, `.ppt`, `.pptx` |

## Custom tool outputs

[Custom tools](../deepagents/tools.md#custom-tools) can contain multimodal files, such as images:

**Python**

Code example: [`code/deepagents/multimodal-capture-screenshot.py`](../code/deepagents/multimodal-capture-screenshot.py)

```python
from langchain.tools import tool

@tool
def capture_screenshot() -> list[dict]:
    """Capture a screenshot of the current page."""
    return [
        {"type": "text", "text": "Screenshot of the current page:"},
        {"type": "image", "url": "https://example.com/page.png"},
    ]
```

**JavaScript / TypeScript**

Code example: [`code/deepagents/multimodal-capture-screenshot.ts`](../code/deepagents/multimodal-capture-screenshot.ts)

```ts
import { tool } from "langchain";
import { z } from "zod";

const captureScreenshot = tool(
  async () => [
    { type: "text", text: "Screenshot of the current page:" },
    { type: "image", url: "https://example.com/page.png" },
  ],
  {
    name: "capture_screenshot",
    description: "Capture a screenshot of the current page.",
    schema: z.object({}),
  },
);
```

The return value is converted to a `ToolMessage` the model reads on the next turn. Access the normalized representation with `content_blocks` on the resulting message. For return-type options, serialization behavior, and MCP examples, see Tool return values and Multimodal tool content.

**Tip**
When a tool produces images or other large binary data, save the artifact to a backend and return a concise text description plus a path or URL. This keeps message history smaller and works better with context compression.

## Context compression and multimodal content

Built-in offloading and summarization are optimized for text and message history:

- **Offloading** measures text tokens only. Non-text blocks (including images) are preserved in replacement messages rather than compressed. A message that contains only an image is not offloaded based on image size alone.
- **Summarization** compacts older messages into a text-only summary. Image, audio, video, and file blocks in that range are not carried forward—the model only sees what the summarizer writes about them. Recent messages below the keep threshold stay unchanged.

    When summarization runs, media blocks in older turns drop out of the active context:

**Python**

    Code example: [`code/deepagents/multimodal-summarization.py`](../code/deepagents/multimodal-summarization.py)

```python
# Before — model receives image blocks in older turns
[
    HumanMessage(
        content=[
            {"type": "text", "text": "What trends do you see in this chart?"},
            {"type": "image", "base64": IMG, "mime_type": "image/png"},
        ]
    ),
    ToolMessage(
        content=[
            {"type": "text", "text": "Updated chart:"},
            {"type": "image", "base64": IMG, "mime_type": "image/png"},
        ],
        tool_call_id="call_chart_1",
    ),
    AIMessage(content="Revenue rose in Q3 based on the chart trend."),
    HumanMessage(content="Reply with one sentence summarizing our analysis."),
]

# After — those turns collapse to text; image blocks are gone
{"content": (
    "User asked about trends in a chart screenshot. "
    "Tool returned an updated chart. Agent identified Q3 revenue growth."
)}
```

**JavaScript / TypeScript**

    Code example: [`code/deepagents/multimodal-summarization.ts`](../code/deepagents/multimodal-summarization.ts)

```ts
// Before — model receives image blocks in older turns
void {
  role: "user",
  content: [
    { type: "text", text: "What trends do you see in this chart?" },
    { type: "image", url: "https://example.com/chart.png" },
  ],
};
void {
  role: "tool",
  content: [
    { type: "text", text: "Updated chart:" },
    { type: "image", url: "https://example.com/chart-v2.png" },
  ],
};

// After — those turns collapse to text; image blocks are gone
void {
  content:
    "User asked about trends in a chart screenshot. " +
    "Tool returned an updated chart. Agent identified Q3 revenue growth.",
};
```

    The original conversation is still written to the filesystem as text. See Summarization for triggers, keep thresholds, and the full flow.

For multimodal-heavy workloads:

- Store images, screenshots, and charts in a filesystem backend or external object store, then pass file paths or URLs through messages.
- Prefer references over base64-encoded image blocks in long-running conversations.
- Use [subagents](../deepagents/subagents.md) for image-heavy inspection so the main agent receives a compact text result.
- Tune summarization thresholds or provide a custom token counter when your provider charges many tokens for images.

See Context compression for offloading thresholds, summarization triggers, and customization options.
