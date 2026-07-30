"use client";

export function ChatConfirmActions({ onDecide }: { onDecide: (answer: string) => void }) {
  return (
    <div className="flex flex-shrink-0 items-center justify-center gap-3 p-3">
      <button
        type="button"
        onClick={() => onDecide("yes")}
        className="rounded-lg bg-accent px-6 py-2 text-sm font-medium text-white transition-opacity duration-200 hover:opacity-90"
      >
        Yes
      </button>
      <button
        type="button"
        onClick={() => onDecide("no")}
        className="rounded-lg border border-line px-6 py-2 text-sm font-medium text-ink-soft transition-colors duration-200 hover:bg-hover hover:text-ink"
      >
        No
      </button>
    </div>
  );
}
