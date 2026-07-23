"use client";

import { useState } from "react";
import { Expand, MessageSquarePlus, Sparkles, SquarePen, X } from "lucide-react";
import { useChatPanel } from "./ChatPanelProvider";
import { ChatEmptyState } from "./ChatEmptyState";
import { ChatComposer } from "./ChatComposer";
import { ChatMessages } from "./ChatMessages";
import { ChatHistoryList } from "./ChatHistoryList";
import { useChat } from "../hooks/useChat";

export function ChatPanel() {
  const { open, closePanel } = useChatPanel();
  const { messages, send, connected, newChat, openConversation, activeConversationId } = useChat("panel");
  const [showHistory, setShowHistory] = useState(false);

  return (
    <aside
      aria-hidden={!open}
      className={`h-full shrink-0 overflow-hidden border-l border-line bg-white transition-[width] duration-300 ease-in-out motion-reduce:transition-none ${
        open ? "w-[400px]" : "w-0"
      }`}
    >
      <section
        aria-label="AI Assistant"
        className="flex h-full w-[400px] flex-col shadow-[-8px_0_24px_-16px_rgba(20,23,28,0.25)]"
      >
        <header className="flex h-16 flex-shrink-0 items-center justify-between border-b border-line px-5">
          <div className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-active text-accent">
              <Sparkles className="h-[18px] w-[18px]" strokeWidth={1.8} />
            </span>
          </div>
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => {
                newChat();
                setShowHistory(false);
              }}
              aria-label="New chat"
              className="flex h-9 w-9 items-center justify-center rounded-lg border border-transparent text-ink-soft transition-colors duration-200 hover:border-line hover:bg-hover hover:text-ink"
            >
              <SquarePen className="h-[18px] w-[18px]" />
            </button>
            <button
              type="button"
              onClick={() => setShowHistory((value) => !value)}
              aria-label="Chat history"
              aria-pressed={showHistory}
              className={`flex h-9 w-9 items-center justify-center rounded-lg border transition-colors duration-200 hover:border-line hover:bg-hover hover:text-ink ${
                showHistory ? "border-line bg-hover text-ink" : "border-transparent text-ink-soft"
              }`}
            >
              <MessageSquarePlus className="h-[18px] w-[18px]" />
            </button>
            <a
              href="/ask-ai"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Open in full screen"
              className="flex h-9 w-9 items-center justify-center rounded-lg border border-transparent text-ink-soft transition-colors duration-200 hover:border-line hover:bg-hover hover:text-ink"
            >
              <Expand className="h-[18px] w-[18px]" />
            </a>
            <button
              type="button"
              onClick={closePanel}
              aria-label="Close AI Assistant"
              className="flex h-9 w-9 items-center justify-center rounded-lg border border-transparent text-ink-soft transition-colors duration-200 hover:border-line hover:bg-hover hover:text-ink"
            >
              <X className="h-[18px] w-[18px]" />
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-scrollbar [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar]:w-1.5">
          {showHistory ? (
            <div className="p-3">
              <ChatHistoryList
                surface="panel"
                activeConversationId={activeConversationId}
                onOpen={(id) => {
                  openConversation(id);
                  setShowHistory(false);
                }}
              />
            </div>
          ) : messages.length === 0 ? (
            <ChatEmptyState />
          ) : (
            <ChatMessages messages={messages} connected={connected} onSend={send} />
          )}
        </div>

        <ChatComposer onSend={send} disabled={!connected} />
      </section>
    </aside>
  );
}
