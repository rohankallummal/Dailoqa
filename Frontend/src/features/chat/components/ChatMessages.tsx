"use client";

import type { Message } from "../lib/messageReducer";
import { ThinkingIndicator } from "./ThinkingIndicator";

export function ChatMessages({
  messages,
  connected,
  thinking,
  toolStatus,
}: {
  messages: Message[];
  connected: boolean;
  thinking?: boolean;
  toolStatus?: string | null;
}) {
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
            data-message-id={message.id}
            tabIndex={-1}
            className={`max-w-[85%] whitespace-pre-wrap rounded-2xl px-3.5 py-2 text-sm leading-relaxed outline-none focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent ${
              message.role === "user" ? "bg-accent text-white" : "border border-line bg-white text-ink"
            }`}
          >
            {message.content}
            {message.streaming ? (
              <span className="ml-0.5 inline-block h-4 w-[2px] translate-y-0.5 animate-pulse bg-ink-muted" />
            ) : null}
          </div>
        </div>
      ))}
      {thinking && <ThinkingIndicator label={toolStatus} />}
    </div>
  );
}
