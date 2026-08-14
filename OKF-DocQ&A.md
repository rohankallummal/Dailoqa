# Implement Documentation-Based Q&A

We are introducing a new capability/skill to the agent:

* **Capability:** Documentation-Based Q&A
* **Skill name:** `DocQA`

## 1. Understand the OKF approach

Before making any implementation changes, read and understand the Open Knowledge Format approach described in this Google Cloud article:

`https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing?utm_source=chatgpt.com`

Use the principles described in the article to guide how we structure and prepare the documentation knowledge store.

Do not blindly copy the article's implementation. Adapt the approach to our existing project architecture and requirements.

## 2. Create the knowledge store

```text

Knowledge-store/
├── langgraph/
│   ├── index.md
│   ├── overview.md
│   ├── persistence.md
│   ├── checkpoints.md
│   ├── stores.md
│   ├── interrupts.md
│   └── subgraphs.md
│
├── langchain/
│   ├── index.md
│   ├── overview.md
│   ├── middleware.md
│   ├── agents.md
│   ├── models.md
│   ├── guardrails.md
│   └── structured-output.md
│
├── deepagents/
│   ├── index.md
│   ├── overview.md
│   ├── subagents.md
│   ├── skills.md
│   ├── sandboxes.md
│   ├── multimodality.md
│   └── tools.md
│
└── code/
    ├── langgraph/
    │   ├── *.py
    │   └── *.ts
    ├── langchain/
    │   ├── *.py
    │   └── *.ts
    └── deepagents/
        ├── *.py
        └── *.ts

```

**Use your discretion to determine where the knowledge store should live within the existing project.**

## 3. Prepare the documentation

We should not modify the original source files directly.

Instead:

* Identify the .mdx documentation files.
* Copy the required MDX files and their Associated code files into the new knowledge-store structure.
* Convert the copied files from .mdx to standard Markdown (.md).
* Perform all cleanup and transformation only on the copied versions.

During this conversion:

- Remove MDX-specific components that are not supported or necessary in standard Markdown.
- Remove or appropriately handle MDX-specific assets that are no longer needed.
- Preserve the actual documentation content, structure, headings, code examples, and important metadata wherever applicable.
- Do not unnecessarily modify the meaning or content of the documentation.
- Identify any references between documentation pages and ensure they remain valid after conversion.
- Identify all standalone code-snippet/source files used by the documentation.
- Link each code-snippet file to the appropriate documentation page so the knowledge store maintains the relationship between documentation and its corresponding code examples.

Important: The original documentation must remain unchanged. The knowledge store should contain the copied and converted versions.

### Documentation-code relationships

The knowledge store should preserve the relationship between documentation and its relevant code examples.


## 4. Implement the DocQA capability

After preparing the knowledge store, integrate it with the chat agent as a new skill called `DocQA`.

Workflow of the agent after receiving the skill:

- Determine whether the user's question is related to the documentation covered by the DocQA knowledge store.
- If it is documentation-related, search/retrieve the relevant content from the DocQA knowledge store.
- Read and interpret the retrieved documentation and any associated code examples.
- Formulate the answer using only the retrieved documentation and code as the source of truth.
- If the question is related to the documented products but the knowledge store does not contain enough information, clearly tell the user that the available documentation does not cover the question. Do not fill the gap using pretrained knowledge.
- If the question is not covered by the documentation at all, do not attempt to answer it. Clearly indicate that the question falls outside the scope of the available documentation.
- After answering the question, the agent must provide hyperlinks to the specific sections of the documentation webpage that support the answer. These links should point directly to the relevant content or section(s) used to formulate the response, serving as evidence for the answer.


### Critical requirement

The agent must **not rely on its pretrained/general knowledge when answering documentation questions**.
The goal is to ensure that answers are grounded in **our provided documentation**, not the model's memory of LangGraph, LangChain, DeepAgents, or related technologies.

## 6. Work with the existing architecture

Before implementing anything:

* Inspect the existing chat-agent architecture.
* Understand how current skills are structured.
* Follow the existing patterns for skill registration, routing, tools, retrieval, and agent execution.
* Reuse existing infrastructure where appropriate instead of introducing a parallel architecture.
* Keep the implementation scoped to the new `DocQA` capability.

Do not make broad unrelated refactors.

## Expected outcome

At the end of this work, the project should have a functioning **`DocQA` skill** backed by a structured **OKF-style knowledge store** containing our LangGraph, LangChain, and DeepAgents documentation and their associated code examples.

The key principle is:

> **For documentation questions, the provided knowledge store is the source of truth, not the model's pretrained knowledge.**
