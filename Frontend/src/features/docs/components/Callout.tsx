import type { ReactNode } from "react";
import { Info, Lightbulb, TriangleAlert } from "lucide-react";
import { Icon } from "./Icon";

function CalloutShell({
  glyph,
  tint,
  children,
}: {
  glyph: ReactNode;
  tint: string;
  children: ReactNode;
}) {
  return (
    <div
      className={`my-4 flex gap-3 rounded-xl border border-line ${tint} px-4 py-3`}
    >
      <span className="mt-0.5 flex h-4 w-4 flex-shrink-0 items-center justify-center">
        {glyph}
      </span>
      <div className="min-w-0 flex-1 text-sm leading-relaxed text-ink-soft [&_p]:my-0 [&_p+p]:mt-2">
        {children}
      </div>
    </div>
  );
}

export function Note({ children }: { children: ReactNode }) {
  return (
    <CalloutShell
      glyph={<Info className="h-4 w-4 text-accent-2" aria-hidden />}
      tint="bg-accent-2/5"
    >
      {children}
    </CalloutShell>
  );
}

export function Tip({ children }: { children: ReactNode }) {
  return (
    <CalloutShell
      glyph={<Lightbulb className="h-4 w-4 text-accent" aria-hidden />}
      tint="bg-accent/5"
    >
      {children}
    </CalloutShell>
  );
}

export function Warning({ children }: { children: ReactNode }) {
  return (
    <CalloutShell
      glyph={<TriangleAlert className="h-4 w-4 text-amber-600" aria-hidden />}
      tint="bg-amber-500/5"
    >
      {children}
    </CalloutShell>
  );
}

export function Callout({
  icon,
  children,
}: {
  icon?: string;
  children: ReactNode;
}) {
  return (
    <CalloutShell
      glyph={<Icon icon={icon} size={16} className="text-ink-muted" />}
      tint="bg-hover"
    >
      {children}
    </CalloutShell>
  );
}
