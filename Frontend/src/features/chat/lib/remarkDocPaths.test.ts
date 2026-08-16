import remarkGfm from "remark-gfm";
import remarkParse from "remark-parse";
import { unified } from "unified";
import { describe, expect, it } from "vitest";

import { remarkDocPaths } from "./remarkDocPaths";

/**
 * Turning the bare `/docs/...` paths in a citation into links.
 *
 * The agent writes its sources as text in parentheses, not Markdown link syntax, and
 * `remark-gfm` only autolinks `http://`, `www.` and email — so without this plugin a citation
 * is on screen but dead.
 */

function hrefs(markdown: string): string[] {
  const processor = unified().use(remarkParse).use(remarkGfm).use(remarkDocPaths);
  const tree = processor.runSync(unified().use(remarkParse).use(remarkGfm).parse(markdown));
  const found: string[] = [];
  const walk = (node: { type?: string; url?: string; children?: unknown[] }) => {
    if (node.type === "link" && node.url) found.push(node.url);
    (node.children ?? []).forEach((child) => walk(child as typeof node));
  };
  walk(tree as never);
  return found;
}

describe("remarkDocPaths", () => {
  it("keeps the #section, which is the whole point of the citation", () => {
    // The regression: the pattern stopped before the "#", so the link was built from the page
    // and the fragment was left behind as text. Every citation opened the top of a page
    // instead of the passage it quoted, while the backend had emitted the anchor correctly.
    expect(hrefs("see (/docs/langgraph/subgraphs#call-a-subgraph-inside-a-node)")).toEqual([
      "/docs/langgraph/subgraphs#call-a-subgraph-inside-a-node",
    ]);
  });

  it("links a page that has no section", () => {
    expect(hrefs("see (/docs/langgraph)")).toEqual(["/docs/langgraph"]);
  });

  it("does not swallow a full stop ending the sentence", () => {
    expect(hrefs("read /docs/langgraph#stateful.")).toEqual(["/docs/langgraph#stateful"]);
  });

  it("leaves paths inside inline code alone", () => {
    expect(hrefs("write `/docs/not-a-link#x` in your config")).toEqual([]);
  });

  it("leaves paths inside a fenced block alone", () => {
    expect(hrefs("```bash\ncurl http://localhost:3000/docs/langgraph\n```")).toEqual([]);
  });

  it("does not double-wrap a link the model wrote itself", () => {
    expect(hrefs("[the skills page](/docs/deepagents/skills#how-skills-work)")).toEqual([
      "/docs/deepagents/skills#how-skills-work",
    ]);
  });

  it("links every citation in a Sources legend", () => {
    expect(
      hrefs(
        "Sources:\n" +
          "[Doc 1] a (/docs/deepagents/subagents#using-compiledsubagent)\n" +
          "[Doc 2] b (/docs/langchain/agents#invocation)",
      ),
    ).toEqual([
      "/docs/deepagents/subagents#using-compiledsubagent",
      "/docs/langchain/agents#invocation",
    ]);
  });
});
