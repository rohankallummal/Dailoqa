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

const components: Components = {
  a({ href, children, ...props }) {
    const target = href ?? "";

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
