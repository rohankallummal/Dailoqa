import type { ReactNode } from "react";
import Image from "next/image";

export function ChatEmptyState({
  title = "Ask AI anything",
  description = "Start a conversation to get help with your workspace, playbooks, and data.",
  showIcon = true,
  className = "flex h-full flex-col items-center justify-center px-8 text-center",
}: {
  title?: string;
  description?: ReactNode;
  showIcon?: boolean;
  className?: string;
}) {
  return (
    <div className={className}>
      {showIcon && (
        <Image
          src="/Mascot1.png"
          alt="AI assistant mascot"
          width={745}
          height={805}
          className="mb-4 h-64 w-auto"
        />
      )}
      <h2 className="text-sm font-semibold text-ink">{title}</h2>
      <p className="mt-1.5 text-[13px] leading-relaxed text-ink-muted">
        {description}
      </p>
    </div>
  );
}
