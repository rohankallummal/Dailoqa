import { Send } from "lucide-react";

export function ChatComposer() {
  return (
    <div className="flex-shrink-0 border-t border-line p-3">
      <div className="flex items-end gap-2 rounded-xl border border-line bg-page px-3 py-2 transition-colors focus-within:border-accent">
        <textarea
          rows={2}
          placeholder="Ask a question…"
          aria-label="Message"
          className="max-h-40 min-h-[40px] flex-1 resize-none bg-transparent py-1 text-sm leading-relaxed text-ink outline-none placeholder:text-ink-muted [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-scrollbar [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar]:w-1.5"
        />
        <button
          type="button"
          aria-label="Send message"
          className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-accent text-white transition-opacity duration-200 hover:opacity-90"
        >
          <Send className="h-4 w-4" strokeWidth={1.9} />
        </button>
      </div>
    </div>
  );
}
