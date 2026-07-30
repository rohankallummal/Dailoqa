"use client";

import { useState, type KeyboardEvent } from "react";

export function ChatPromptBar({ onSend }: { onSend: (text: string) => void }) {
  const [value, setValue] = useState("");

  const submit = () => {
    const text = value.trim();
    if (!text) return;
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
        className="min-w-0 flex-1 bg-transparent text-base text-ink outline-none placeholder:text-ink-muted"
      />
    </div>
  );
}
