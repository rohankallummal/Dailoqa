"use client";

import {
  Children,
  cloneElement,
  isValidElement,
  useState,
  type ReactElement,
  type ReactNode,
} from "react";

type CodeBlockProps = {
  language?: string;
  title?: string;
  code?: string;
  headless?: boolean;
};

export function CodeGroup({ children }: { children: ReactNode }) {
  const blocks = Children.toArray(children).filter((child) =>
    isValidElement(child),
  ) as ReactElement<CodeBlockProps>[];

  const [active, setActive] = useState(0);

  if (blocks.length === 0) return null;
  if (blocks.length === 1) return <>{blocks[0]}</>;

  const current = Math.min(active, blocks.length - 1);

  return (
    <div className="my-4 overflow-hidden rounded-xl border border-line bg-[#1e2230]">
      <div className="flex flex-wrap items-center gap-1 border-b border-white/10 px-2 py-1.5">
        {blocks.map((block, index) => {
          const label =
            block.props.title || block.props.language || `Tab ${index + 1}`;
          const isActive = index === current;
          return (
            <button
              key={index}
              type="button"
              onClick={() => setActive(index)}
              className={`rounded-md px-3 py-1 text-xs font-medium transition-colors ${
                isActive
                  ? "bg-white/10 text-white"
                  : "text-white/50 hover:text-white/80"
              }`}
            >
              {label}
            </button>
          );
        })}
      </div>
      {cloneElement(blocks[current], { headless: true })}
    </div>
  );
}
