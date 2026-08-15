"use client";

import type { Message } from "../lib/messageReducer";
import { MessageMarkdown } from "./MessageMarkdown";
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
            className={`max-w-[85%] rounded-2xl px-3.5 py-2 text-sm leading-relaxed ${
              message.role === "user"
                ? "whitespace-pre-wrap bg-accent text-white"
                : "border border-line bg-white text-ink"
            }`}
          >
            {/* Only the assistant answers in Markdown. A user's message is rendered verbatim so
                that typing a `#` or an underscore never reformats what they wrote back at them. */}
            {message.role === "user" ? message.content : <MessageMarkdown content={message.content} />}
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
