"use client";

import { useState, type ReactNode } from "react";
import { ChevronRight } from "lucide-react";

export function Expandable({
  title,
  defaultOpen = false,
  children,
}: {
  title?: string;
  defaultOpen?: boolean;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="my-3">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex w-full items-center gap-1.5 text-left text-sm font-medium text-ink-soft transition-colors hover:text-ink"
      >
        <ChevronRight
          className={`h-4 w-4 flex-shrink-0 transition-transform ${
            open ? "rotate-90" : ""
          }`}
        />
        <span className="min-w-0 flex-1">{title}</span>
      </button>
      {open ? (
        <div className="mt-2 border-l-2 border-line pl-4 text-sm leading-relaxed text-ink-soft [&_p:first-child]:mt-0 [&_p:last-child]:mb-0">
          {children}
        </div>
      ) : null}
    </div>
  );
}
