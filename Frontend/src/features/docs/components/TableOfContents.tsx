"use client";

import { useEffect, useState } from "react";
import type { TocItem } from "../lib/plugins";

export function TableOfContents({ items }: { items: TocItem[] }) {
  const [activeSlug, setActiveSlug] = useState<string>("");

  useEffect(() => {
    if (items.length === 0) return;
    const headings = items
      .map((item) => document.getElementById(item.slug))
      .filter((element): element is HTMLElement => element !== null);

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible[0]) {
          setActiveSlug(visible[0].target.id);
        }
      },
      { rootMargin: "0px 0px -70% 0px", threshold: 0 },
    );

    headings.forEach((heading) => observer.observe(heading));
    return () => observer.disconnect();
  }, [items]);

  if (items.length === 0) return null;

  return (
    <nav className="sticky top-6 hidden max-h-[calc(100vh-3rem)] overflow-y-auto text-sm xl:block">
      <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-ink-muted">
        On this page
      </p>
      <ul className="space-y-1 border-l border-line">
        {items.map((item) => {
          const isActive = item.slug === activeSlug;
          return (
            <li key={item.slug}>
              <a
                href={`#${item.slug}`}
                className={`-ml-px block border-l py-1 transition-colors ${
                  item.depth === 3 ? "pl-6" : "pl-4"
                } ${
                  isActive
                    ? "border-accent font-medium text-accent"
                    : "border-transparent text-ink-soft hover:text-ink"
                }`}
              >
                {item.text}
              </a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
