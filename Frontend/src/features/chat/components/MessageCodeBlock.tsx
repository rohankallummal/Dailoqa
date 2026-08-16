"use client";

import { createContext, useContext, useState, type ReactNode } from "react";
import { Check, Copy } from "lucide-react";
import { codeLanguage, nodeText } from "../lib/markdown";

export const InsideCodeBlock = createContext(false);

export function useInsideCodeBlock() {
  return useContext(InsideCodeBlock);
}

export function MessageCodeBlock({
  node,
  children,
}: {
  node?: Parameters<typeof nodeText>[0];
  children: ReactNode;
}) {
  const [copied, setCopied] = useState(false);
  const language = codeLanguage(node);
  const source = nodeText(node);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(source);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className="my-3 overflow-hidden rounded-lg border border-line bg-[#1e2230]">
      <div className="flex items-center justify-between border-b border-white/10 px-3 py-1.5">
        <span className="text-[11px] font-medium text-white/60">{language || "text"}</span>
        <button
          type="button"
          onClick={copy}
          aria-label={copied ? "Copied" : "Copy code"}
          className="inline-flex items-center gap-1 rounded-md px-1.5 py-1 text-[11px] text-white/50 transition-colors hover:bg-white/10 hover:text-white/80"
        >
          {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
        </button>
      </div>
      <pre className="overflow-x-auto px-3 py-2.5 text-[12.5px] leading-[1.55] text-white/90">
        <InsideCodeBlock.Provider value={true}>{children}</InsideCodeBlock.Provider>
      </pre>
    </div>
  );
}
