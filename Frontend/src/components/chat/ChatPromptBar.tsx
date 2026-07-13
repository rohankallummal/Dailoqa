import { Mic, Plus } from "lucide-react";

export function ChatPromptBar() {
  return (
    <div className="flex w-full max-w-3xl items-center gap-3 rounded-2xl border border-line bg-white px-4 py-3 shadow-sm transition-colors focus-within:border-accent">
      <button
        type="button"
        aria-label="Add attachment"
        className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full border border-line text-ink-soft transition-colors duration-200 hover:bg-hover hover:text-ink"
      >
        <Plus className="h-[18px] w-[18px]" />
      </button>
      <input
        type="text"
        placeholder="Ask AI anything…"
        aria-label="Message"
        className="min-w-0 flex-1 bg-transparent text-base text-ink outline-none placeholder:text-ink-muted"
      />
      <button
        type="button"
        aria-label="Voice input"
        className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full border border-line text-ink-soft transition-colors duration-200 hover:bg-hover hover:text-ink"
      >
        <Mic className="h-[18px] w-[18px]" />
      </button>
    </div>
  );
}
