import { Sparkles } from "lucide-react";

export function ChatEmptyState() {
  return (
    <div className="flex h-full flex-col items-center justify-center px-8 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-line bg-page text-accent">
        <Sparkles className="h-6 w-6" strokeWidth={1.8} />
      </div>
      <h2 className="mt-4 text-sm font-semibold text-ink">Ask AI anything</h2>
      <p className="mt-1.5 text-[13px] leading-relaxed text-ink-muted">
        Start a conversation to get help with your workspace, playbooks, and
        data.
      </p>
    </div>
  );
}
