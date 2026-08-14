"use client";

import { useState, type ReactNode } from "react";
import { ChevronRight, Folder as FolderGlyph } from "lucide-react";

export function TreeFolder({
  name,
  defaultOpen = false,
  children,
}: {
  name?: string;
  defaultOpen?: boolean;
  children?: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div>
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex w-full items-center gap-1.5 py-0.5 text-left transition-colors hover:text-ink"
      >
        <ChevronRight
          className={`h-3.5 w-3.5 flex-shrink-0 text-ink-muted transition-transform ${
            open ? "rotate-90" : ""
          }`}
        />
        <FolderGlyph className="h-3.5 w-3.5 flex-shrink-0 text-accent" />
        {name}
      </button>
      {open ? (
        <div className="ml-2 border-l border-line pl-3">{children}</div>
      ) : null}
    </div>
  );
}
