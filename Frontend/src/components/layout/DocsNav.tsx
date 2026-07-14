"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { docsNavItems } from "./docsNavConfig";

export function DocsNav() {
  const pathname = usePathname();

  return (
    <nav className="flex h-12 flex-shrink-0 items-center gap-1 overflow-x-auto border-b border-line bg-white px-6">
      {docsNavItems.map((item) => {
        const active = pathname === item.href;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={`relative flex h-full items-center whitespace-nowrap px-3 text-sm font-medium transition-colors ${
              active ? "text-ink" : "text-ink-soft hover:text-ink"
            }`}
          >
            {item.label}
            {active && (
              <span className="absolute inset-x-3 bottom-0 h-0.5 rounded-full bg-accent" />
            )}
          </Link>
        );
      })}
    </nav>
  );
}
