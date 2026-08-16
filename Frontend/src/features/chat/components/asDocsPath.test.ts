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

  it("leaves genuine external links alone", () => {
    expect(asDocsPath("https://example.com/blog/post")).toBeNull();
    expect(asDocsPath("https://github.com/langchain-ai/docs")).toBeNull();
  });

  it("ignores anything that is not an absolute URL", () => {
    // Relative paths are already correct and must not be round-tripped through URL parsing.
    expect(asDocsPath("/docs/langgraph#stateful")).toBeNull();
    expect(asDocsPath("#section")).toBeNull();
    expect(asDocsPath("")).toBeNull();
  });
});
