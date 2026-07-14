"use client";

import { useState } from "react";
import { Check, Copy } from "lucide-react";

export function CodeBlock({
  language,
  title,
  code,
  headless = false,
}: {
  language?: string;
  title?: string;
  code?: string;
  headless?: boolean;
}) {
  const [copied, setCopied] = useState(false);
  const value = code ?? "";
  const label = title || language || "";

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      setCopied(false);
    }
  };

  if (headless) {
    return (
      <div className="relative">
        <div className="absolute right-2 top-2">
          <CopyButton copied={copied} onCopy={copy} />
        </div>
        <pre className="overflow-x-auto px-4 py-3 text-sm leading-relaxed text-white/90">
          <code>{value}</code>
        </pre>
      </div>
    );
  }

  return (
    <div className="my-4 overflow-hidden rounded-xl border border-line bg-[#1e2230]">
      <div className="flex items-center justify-between border-b border-white/10 px-4 py-2">
        <span className="text-xs font-medium text-white/60">{label}</span>
        <CopyButton copied={copied} onCopy={copy} />
      </div>
      <pre className="overflow-x-auto px-4 py-3 text-sm leading-relaxed text-white/90">
        <code>{value}</code>
      </pre>
    </div>
  );
}

function CopyButton({
  copied,
  onCopy,
}: {
  copied: boolean;
  onCopy: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onCopy}
      aria-label="Copy code"
      className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs text-white/50 transition-colors hover:bg-white/10 hover:text-white/80"
    >
      {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
    </button>
  );
}
