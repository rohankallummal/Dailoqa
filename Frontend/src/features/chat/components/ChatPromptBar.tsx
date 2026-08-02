"use client";

import { useState, type KeyboardEvent } from "react";

export function ChatPromptBar({ onSend, disabled }: { onSend: (text: string) => void; disabled?: boolean }) {
  const [value, setValue] = useState("");

  const submit = () => {
    const text = value.trim();
    if (!text || disabled) return;
    onSend(text);
    setValue("");
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      event.preventDefault();
      submit();
    }
  };

  return (
    <div className="flex w-full max-w-3xl items-center rounded-2xl border border-line bg-white px-4 py-3 shadow-sm transition-colors focus-within:border-accent">
      <input
        type="text"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask AI anything…"
        aria-label="Message"
        disabled={disabled}
        className="min-w-0 flex-1 bg-transparent text-base text-ink outline-none placeholder:text-ink-muted disabled:opacity-50"
      />
    </div>
  );
}
