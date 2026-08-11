import type { ReactNode } from "react";

export function Tooltip({
  tip,
  children,
}: {
  tip?: string;
  children?: ReactNode;
}) {
  return (
    <span
      title={tip}
      className="cursor-help underline decoration-ink-muted decoration-dotted underline-offset-2"
    >
      {children}
    </span>
  );
}
