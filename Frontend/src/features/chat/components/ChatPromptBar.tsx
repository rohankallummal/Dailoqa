"use client";

import type { KeyboardEvent } from "react";
import { Send } from "lucide-react";
import { useComposer } from "../hooks/useComposer";

export function ChatPromptBar({ onSend, disabled }: { onSend: (text: string) => void; disabled?: boolean }) {
  const { value, setValue, submit } = useComposer(onSend, disabled);

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      event.preventDefault();
      submit();
    }
  };

  return (
    <div className="flex w-full max-w-3xl items-center rounded-2xl border border-line bg-white px-4 py-2 shadow-sm transition-colors focus-within:border-accent">
      <input
        type="text"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={handleKeyDown}
        aria-label="Message"
        disabled={disabled}
        className="min-w-0 flex-1 bg-transparent text-base text-ink outline-none placeholder:text-ink-muted disabled:opacity-50"
      />
      <button
        type="button"
        onClick={() => submit()}
        disabled={disabled}
        aria-label="Send message"
        className={`ml-3 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-accent text-white transition-opacity duration-200 hover:opacity-90 disabled:opacity-40 ${
          value.trim() ? "" : "invisible"
        }`}
      >
        <Send className="h-4 w-4" strokeWidth={1.9} />
      </button>
    </div>
  );
}
