"use client";

import Link from "next/link";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";

import { remarkDocPaths } from "../lib/remarkDocPaths";

/**
 * Renders one assistant message.
 *
 * The agent answers in Markdown — headings, lists, fenced code and a `Sources:` legend — so
 * rendering the raw string left `###` and `**` on screen and, more importantly, left every
 * documentation citation as dead text the reader could not open.
 *
 * `rehype-raw` is deliberately absent. Without it react-markdown escapes embedded HTML rather
 * than executing it, which is what keeps model-authored content safe to render; adding it would
 * turn an answer into a script injection vector, so the omission is load-bearing rather than an
 * oversight.
 */

const isInternal = (href: string) => href.startsWith("/");
const isAnchor = (href: string) => href.startsWith("#");

/** The topic segments a documentation route can start with, per docs-corpus/manifest.json. */
const DOC_TOPICS = new Set(["deepagents", "langchain", "langgraph"]);

/**
 * Recover a documentation route from a link the model gave a hostname to.
 *
 * Citations are handed to the model as site-relative paths, but it periodically writes them as
 * absolute URLs against a host that does not exist — "https://docs.dailoqa.com/docs/deepagents
 * /subagents", "https://docs.deepagents/subagents#using-compiledsubagent". Those render as
 * ordinary links: they look clickable and land nowhere.
 *
 * Instructing it not to has not held, so the path is taken over the host whenever the link is
 * recognisably a documentation one. A genuine external link whose path starts with `/docs` would
 * be internalised by this, which is the deliberate trade: the assistant answers only from this
 * product's documentation, so such a link is far more likely to be a fabricated host than a real
 * destination — and an internal link that 404s is easier to notice than one that leaves the app.
 *
 * **Two shapes, because the host can swallow the `/docs` segment.** Alongside the usual
 * "…/docs/langgraph/subgraphs", an audit turned up `https://docs/langgraph/subgraphs` — the word
 * `docs` used as the entire hostname, leaving a path with no `/docs` on it at all. That one is
 * not repairable by path alone and rendered as a dead off-site link, so the host is inspected
 * too. Kept deliberately narrow: a bare `docs` cannot be a real public host (no dot), and a
 * `docs.*` host only qualifies when the path's first segment is a real documentation topic — so
 * a genuine link like `https://docs.langchain.com/oss/python/...` is left alone.
 */
export function asDocsPath(href: string): string | null {
  try {
    const url = new URL(href);
    if (url.pathname.startsWith("/docs")) {
      return `${url.pathname}${url.hash}`;
    }
    const hostParts = url.hostname.split(".");
    const hostIsBareDocs = url.hostname === "docs";
    const hostLooksLikeDocs = hostIsBareDocs || url.hostname.startsWith("docs.");
    const firstSegment = url.pathname.split("/")[1] ?? "";
    if (hostLooksLikeDocs && (hostIsBareDocs || DOC_TOPICS.has(firstSegment))) {
      return `/docs${url.pathname}${url.hash}`;
    }
    // The host swallowed the topic as well: "https://docs.langgraph/checkpoints#base-contract",
    // whose real route is /docs/langgraph/checkpoints. Requiring exactly two host labels is what
    // keeps this off real sites -- "docs.langchain.com" has three, so it is never rewritten,
    // while ".langgraph" is not a TLD that can exist.
    if (hostParts.length === 2 && hostParts[0] === "docs" && DOC_TOPICS.has(hostParts[1])) {
      return `/docs/${hostParts[1]}${url.pathname}${url.hash}`;
    }
    return null;
  } catch {
    return null;
  }
}

const components: Components = {
  a({ href, children, ...props }) {
    // A fabricated host on a /docs link is repaired before anything else looks at it.
    const target = asDocsPath(href ?? "") ?? href ?? "";

    // Documentation citations point at /docs/... . Next's Link keeps those client-side, so
    // following a citation does not reload the app and lose the conversation.
    if (isInternal(target)) {
      return (
        <Link href={target} className="text-accent underline underline-offset-2">
          {children}
        </Link>
      );
    }

    // Same-page anchors: a plain <a>, since Link would treat them as a route.
    if (isAnchor(target)) {
      return (
        <a href={target} className="text-accent underline underline-offset-2">
          {children}
        </a>
      );
    }

    // Anything else is off-site. noreferrer alongside noopener so the destination cannot see
    // where the user came from, and a new tab so the conversation is never navigated away from.
    return (
      <a
        {...props}
        href={target}
        target="_blank"
        rel="noopener noreferrer"
        className="text-accent underline underline-offset-2"
      >
        {children}
      </a>
    );
  },
  // Tailwind's preflight strips list markers and heading sizes, so the few elements an answer
  // actually uses are restyled here rather than pulling in a typography plugin for one panel.
  h1: ({ children }) => <h2 className="mt-3 mb-1 text-sm font-semibold first:mt-0">{children}</h2>,
  h2: ({ children }) => <h3 className="mt-3 mb-1 text-sm font-semibold first:mt-0">{children}</h3>,
  h3: ({ children }) => <h4 className="mt-3 mb-1 text-sm font-semibold first:mt-0">{children}</h4>,
  ul: ({ children }) => <ul className="my-1 list-disc space-y-0.5 pl-5">{children}</ul>,
  ol: ({ children }) => <ol className="my-1 list-decimal space-y-0.5 pl-5">{children}</ol>,
  p: ({ children }) => <p className="my-1 first:mt-0 last:mb-0">{children}</p>,
  code: ({ className, children }) =>
    className?.startsWith("language-") ? (
      <code className={`${className} block`}>{children}</code>
    ) : (
      <code className="rounded bg-hover px-1 py-0.5 text-[0.85em]">{children}</code>
    ),
  pre: ({ children }) => (
    <pre className="my-2 overflow-x-auto rounded-lg bg-hover p-2.5 text-[0.85em]">{children}</pre>
  ),
  table: ({ children }) => (
    <div className="my-2 overflow-x-auto">
      <table className="w-full border-collapse text-left">{children}</table>
    </div>
  ),
  th: ({ children }) => <th className="border border-line px-2 py-1 font-semibold">{children}</th>,
  td: ({ children }) => <td className="border border-line px-2 py-1 align-top">{children}</td>,
};

export function MessageMarkdown({ content }: { content: string }) {
  return (
    <div className="[&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
      <ReactMarkdown remarkPlugins={[remarkGfm, remarkDocPaths]} components={components}>
        {content}
      </ReactMarkdown>
    </div>
  );
}
