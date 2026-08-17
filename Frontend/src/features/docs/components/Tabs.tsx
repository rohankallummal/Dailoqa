"use client";

import type { ReactNode } from "react";
import { useTabbedChildren } from "../lib/tabbedChildren";

type TabProps = {
  title?: string;
  children?: ReactNode;
};

export function Tab({ children }: TabProps) {
  return <>{children}</>;
}

export function Tabs({ children }: { children: ReactNode }) {
  const { tabs, current, setActive } = useTabbedChildren<TabProps>(children);

  if (tabs.length === 0) return null;

  return (
    <div className="my-4">
      <div className="flex flex-wrap items-center gap-6 border-b border-line">
        {tabs.map((tab, index) => {
          const isActive = index === current;
          return (
            <button
              key={index}
              type="button"
              onClick={() => setActive(index)}
              className={`relative -mb-px pb-2.5 text-sm font-medium transition-colors ${
                isActive ? "text-accent" : "text-ink-soft hover:text-ink"
              }`}
            >
              {tab.props.title || `Tab ${index + 1}`}
              {isActive ? (
                <span className="absolute inset-x-0 bottom-0 h-0.5 rounded-full bg-accent" />
              ) : null}
            </button>
          );
        })}
      </div>
      <div className="pt-3">{tabs[current]}</div>
    </div>
  );
}
