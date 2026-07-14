"use client";

import { useState, type ReactNode } from "react";
import { ChevronRight } from "lucide-react";
import { Icon } from "./Icon";

export function Accordion({
  title,
  icon,
  defaultOpen = false,
  children,
}: {
  title?: string;
  icon?: string;
  defaultOpen?: boolean;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="my-3 overflow-hidden rounded-xl border border-line bg-white">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex w-full items-center gap-2 px-4 py-3 text-left text-sm font-medium text-ink"
      >
        <ChevronRight
          className={`h-4 w-4 flex-shrink-0 text-ink-muted transition-transform ${
            open ? "rotate-90" : ""
          }`}
        />
        {icon ? (
          <span className="inline-flex text-ink-soft">
            <Icon icon={icon} size={16} />
          </span>
        ) : null}
        <span className="min-w-0 flex-1">{title}</span>
      </button>
      {open ? (
        <div className="border-t border-line px-4 py-3 text-sm leading-relaxed text-ink-soft [&_p:first-child]:mt-0 [&_p:last-child]:mb-0">
          {children}
        </div>
      ) : null}
    </div>
  );
}
