"use client";

export function ChatPendingNotice() {
  return (
    <div
      role="status"
      className="flex flex-shrink-0 items-center justify-center gap-2 p-3 text-sm text-ink-muted"
    >
      <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-accent" aria-hidden="true" />
      Submitting…
    </div>
  );
}
