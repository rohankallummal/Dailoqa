import { describe, expect, it } from "vitest";

import { asDocsPath } from "./MessageMarkdown";

/**
 * Repairing citations the model gave a hostname to.
 *
 * Citations are handed to it as site-relative paths, but it periodically writes them absolute
 * against a host that does not exist. Those render as ordinary links — clickable, and landing
 * nowhere. Telling it not to has not held across several attempts, so the renderer takes the
 * path and discards the invented host.
 */

describe("asDocsPath", () => {
  it("recovers the route from a fabricated host", () => {
    // Both seen in real answers.
    expect(asDocsPath("https://docs.dailoqa.com/docs/deepagents/subagents")).toBe(
      "/docs/deepagents/subagents",
    );
    expect(asDocsPath("https://docs.deepagents/docs/langgraph")).toBe("/docs/langgraph");
  });

  it("keeps the section anchor while dropping the host", () => {
    expect(asDocsPath("https://docs.dailoqa/docs/deepagents#streaming")).toBe(
      "/docs/deepagents#streaming",
    );
  });

  it("recovers the route when the host swallowed the /docs segment", () => {
    // Found in an audit: `docs` used as the whole hostname, so the path carries no /docs at all
    // and the path-only repair returned null. It rendered as a dead off-site link.
    expect(asDocsPath("https://docs/langgraph/subgraphs")).toBe("/docs/langgraph/subgraphs");
    expect(asDocsPath("https://docs/deepagents/skills#usage")).toBe("/docs/deepagents/skills#usage");
    // A made-up host whose path starts straight at a real topic.
    expect(asDocsPath("https://docs.dailoqa/deepagents")).toBe("/docs/deepagents");
  });

  it("leaves genuine external links alone", () => {
    expect(asDocsPath("https://example.com/blog/post")).toBeNull();
    expect(asDocsPath("https://github.com/langchain-ai/docs")).toBeNull();
    // A real docs site whose first path segment is not one of our topics. The host-based repair
    // must not swallow this, or a legitimate upstream link becomes an internal 404.
    expect(asDocsPath("https://docs.langchain.com/oss/python/langgraph")).toBeNull();
  });

  it("ignores anything that is not an absolute URL", () => {
    // Relative paths are already correct and must not be round-tripped through URL parsing.
    expect(asDocsPath("/docs/langgraph#stateful")).toBeNull();
    expect(asDocsPath("#section")).toBeNull();
    expect(asDocsPath("")).toBeNull();
  });
});
