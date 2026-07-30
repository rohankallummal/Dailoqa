"use client";

export function ChatPendingNotice() {
  return (
    <div
      role="status"
      className="flex flex-shrink-0 items-center justify-center p-3 text-sm text-ink-muted"
    >
      Submitting…
    </div>
  );
}
