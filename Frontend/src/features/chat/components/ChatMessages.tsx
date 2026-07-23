"use client";

import type { Message } from "../lib/messageReducer";

export function ChatMessages({
  messages,
  connected,
  onSend,
}: {
  messages: Message[];
  connected: boolean;
  onSend: (text: string) => void;
}) {
  const last = messages[messages.length - 1];
  const awaitingConfirm = last?.role === "assistant" && last.stage === "confirm";

  return (
    <div className="flex flex-col gap-3 px-4 py-4">
      {!connected && (
        <div className="mx-auto rounded-full bg-hover px-3 py-1 text-[11px] font-medium text-ink-muted">
          Reconnecting…
        </div>
      )}
      {messages.map((message) => (
        <div key={message.id} className={message.role === "user" ? "flex justify-end" : "flex justify-start"}>
          <div
            className={`max-w-[85%] whitespace-pre-wrap rounded-2xl px-3.5 py-2 text-sm leading-relaxed ${
              message.role === "user" ? "bg-accent text-white" : "border border-line bg-white text-ink"
            }`}
          >
            {message.content}
          </div>
        </div>
      ))}
      {awaitingConfirm && (
        <div className="flex justify-start gap-2 pl-1">
          <button
            type="button"
            onClick={() => onSend("yes")}
            className="rounded-lg bg-accent px-3 py-1.5 text-sm font-medium text-white transition-opacity duration-200 hover:opacity-90"
          >
            Yes, create it
          </button>
          <button
            type="button"
            onClick={() => onSend("no")}
            className="rounded-lg border border-line px-3 py-1.5 text-sm font-medium text-ink-soft transition-colors duration-200 hover:bg-hover hover:text-ink"
          >
            No
          </button>
        </div>
      )}
    </div>
  );
}
