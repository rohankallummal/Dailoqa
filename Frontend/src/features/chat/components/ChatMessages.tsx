"use client";

import type { Message } from "../lib/messageReducer";

export function ChatMessages({ messages, connected }: { messages: Message[]; connected: boolean }) {
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
    </div>
  );
}
