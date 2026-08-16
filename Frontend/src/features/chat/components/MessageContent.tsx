"use client";

import { memo, useMemo } from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import rehypeSanitize, { defaultSchema } from "rehype-sanitize";
import { balanceCodeFences } from "../lib/markdown";
import { InsideCodeBlock, MessageCodeBlock, useInsideCodeBlock } from "./MessageCodeBlock";

const components: Components = {
  pre: ({ node, children }) => <MessageCodeBlock node={node}>{children}</MessageCodeBlock>,
  code: ({ children, className }) => (
    <InlineOrBlockCode className={className}>{children}</InlineOrBlockCode>
  ),
  a: ({ children, href }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-accent underline underline-offset-2 hover:no-underline"
    >
      {children}
    </a>
  ),
  table: ({ children }) => (
    <div className="my-3 overflow-x-auto">
      <table className="w-full border-collapse text-[13px]">{children}</table>
    </div>
  ),
  th: ({ children }) => (
    <th className="border border-line bg-hover px-2 py-1 text-left font-semibold">{children}</th>
  ),
  td: ({ children }) => <td className="border border-line px-2 py-1 align-top">{children}</td>,
  h1: ({ children }) => <h2 className="mt-4 mb-2 text-[19px] font-semibold">{children}</h2>,
  h2: ({ children }) => <h2 className="mt-4 mb-2 text-[18px] font-semibold">{children}</h2>,
  h3: ({ children }) => <h3 className="mt-3 mb-1.5 text-[15px] font-semibold">{children}</h3>,
  h4: ({ children }) => <h4 className="mt-3 mb-1.5 text-[14px] font-semibold">{children}</h4>,
  p: ({ children }) => <p className="my-2">{children}</p>,
  ul: ({ children }) => <ul className="my-2 list-disc space-y-1 pl-5">{children}</ul>,
  ol: ({ children }) => <ol className="my-2 list-decimal space-y-1 pl-5">{children}</ol>,
  li: ({ children }) => <li className="pl-0.5">{children}</li>,
  blockquote: ({ children }) => (
    <blockquote className="my-2 border-l-2 border-line pl-3 text-ink-soft">{children}</blockquote>
  ),
  hr: () => <hr className="my-3 border-line" />,
  input: ({ checked, type }) =>
    type === "checkbox" ? (
      <input type="checkbox" checked={checked} disabled className="mr-1.5 align-middle" />
    ) : null,
};

function InlineOrBlockCode({
  children,
  className,
}: {
  children?: React.ReactNode;
  className?: string;
}) {
  if (useInsideCodeBlock()) return <code className={className}>{children}</code>;
  return (
    <code className="rounded bg-hover px-1 py-0.5 font-mono text-[12.5px] text-ink">{children}</code>
  );
}

export const MessageContent = memo(function MessageContent({ content }: { content: string }) {
  const prepared = useMemo(() => balanceCodeFences(content), [content]);
  const rendered = useMemo(
    () => (
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[[rehypeSanitize, defaultSchema], rehypeHighlight]}
        components={components}
      >
        {prepared}
      </ReactMarkdown>
    ),
    [prepared],
  );

  return (
    <div className="chatMarkdown max-w-[70ch] leading-[1.6] [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
      {rendered}
    </div>
  );
});

export { InsideCodeBlock };
