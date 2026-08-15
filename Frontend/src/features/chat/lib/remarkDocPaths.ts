import { findAndReplace } from "mdast-util-find-and-replace";
import type { Root } from "mdast";

/**
 * Turns bare `/docs/...` paths in an answer into real links.
 *
 * The agent cites its sources as `[Doc 1] deep-agents/Subagents - ... (/docs/deepagents/subagents)`
 * — a path in parentheses, not Markdown link syntax. CommonMark leaves that as text, and
 * `remark-gfm`'s autolinker only covers `http://`, `www.` and email, so without this the route is
 * on screen but dead. Verified against the parser rather than assumed.
 *
 * Doing it as a remark plugin rather than a regex over the raw string is what makes it safe:
 * `findAndReplace` walks text nodes only, so a path inside a fenced sample or inline code is left
 * alone, and it skips the inside of existing links so an explicit `[label](/docs/x)` is not
 * double-wrapped.
 *
 * A trailing slash is kept in the href rather than trimmed. Next 308-redirects `/docs/langgraph/`
 * to `/docs/langgraph`, so the link still lands, and rewriting what the model emitted would hide
 * the drift that `test_a_cited_route_is_byte_identical_to_the_manifest` exists to catch.
 */

// A docs route: /docs, optionally followed by segments. Trailing punctuation is excluded so a
// path ending a sentence — "...see /docs/langgraph." — does not swallow the full stop.
const DOC_PATH = /\/docs(?:\/[a-z0-9-]+)*\/?/gi;

export function remarkDocPaths() {
  return (tree: Root) => {
    findAndReplace(tree, [
      [
        DOC_PATH,
        (match: string) => ({
          type: "link",
          url: match,
          children: [{ type: "text", value: match }],
        }),
      ],
    ]);
  };
}
