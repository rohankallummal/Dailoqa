import type { ReactNode } from "react";
import { Info, Lightbulb, type LucideIcon } from "lucide-react";

function Callout({
  icon: Glyph,
  accent,
  tint,
  children,
}: {
  icon: LucideIcon;
  accent: string;
  tint: string;
  children: ReactNode;
}) {
  return (
    <div
      className={`my-4 flex gap-3 rounded-xl border border-line ${tint} px-4 py-3`}
    >
      <Glyph className={`mt-0.5 h-4 w-4 flex-shrink-0 ${accent}`} aria-hidden />
      <div className="min-w-0 flex-1 text-sm leading-relaxed text-ink-soft [&_p]:my-0 [&_p+p]:mt-2">
        {children}
      </div>
    </div>
  );
}

export function Note({ children }: { children: ReactNode }) {
  return (
    <Callout icon={Info} accent="text-accent-2" tint="bg-accent-2/5">
      {children}
    </Callout>
  );
}

export function Tip({ children }: { children: ReactNode }) {
  return (
    <Callout icon={Lightbulb} accent="text-accent" tint="bg-accent/5">
      {children}
    </Callout>
  );
}
