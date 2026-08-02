"use client";

import { useEffect, useRef, useState } from "react";
import { PanelLeftOpen, Sparkles } from "lucide-react";
import { ChatHistorySidebar } from "./ChatHistorySidebar";
import { ChatPromptBar } from "./ChatPromptBar";
import { ChatConfirmActions } from "./ChatConfirmActions";
import { ChatErrorNotice } from "./ChatErrorNotice";
import { ChatMessages } from "./ChatMessages";
import { ChatPendingNotice } from "./ChatPendingNotice";
import { EvidenceCard } from "./EvidenceCard";
import { useChat } from "../hooks/useChat";

export function AskAiWorkspace({ initialConversationId }: { initialConversationId?: string }) {
  const [collapsed, setCollapsed] = useState(false);
  const toggle = () => setCollapsed((value) => !value);
  const { messages, send, connected, inputState, error, newChat, openConversation, activeConversationId } =
    useChat("full");

  const opened = useRef(false);
  useEffect(() => {
    if (opened.current || !initialConversationId) return;
    opened.current = true;
    void openConversation(initialConversationId);
  }, [initialConversationId, openConversation]);

  return (
    <div className="flex h-screen overflow-hidden bg-page">
      <ChatHistorySidebar
        collapsed={collapsed}
        onToggle={toggle}
        onOpen={openConversation}
        onDeleted={(id) => {
          if (id === activeConversationId) newChat();
        }}
        activeConversationId={activeConversationId}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-16 flex-shrink-0 items-center justify-between border-b border-line bg-white px-8">
          <div className="flex items-center">
            {collapsed && (
              <button
                type="button"
                onClick={toggle}
                aria-label="Open sidebar"
                className="flex h-9 w-9 items-center justify-center rounded-lg border border-transparent text-ink-soft transition-colors duration-200 hover:border-line hover:bg-hover hover:text-ink"
              >
                <PanelLeftOpen className="h-[18px] w-[18px]" />
              </button>
            )}
          </div>

          <button
            type="button"
            onClick={newChat}
            className="flex h-9 items-center gap-2 rounded-lg border border-line bg-page px-3.5 text-sm font-medium text-ink-soft transition-colors duration-200 hover:bg-hover hover:text-ink"
          >
            <Sparkles className="h-4 w-4 text-accent" strokeWidth={1.8} />
            New Chat
          </button>
        </header>

        {messages.length === 0 ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-8 px-6">
            <h1 className="text-3xl font-semibold tracking-tight text-ink">What can I help with?</h1>
            <div className="flex w-full flex-col items-center">
              <ChatPromptBar onSend={send} />
              {error && <ChatErrorNotice message={error} />}
            </div>
          </div>
        ) : (
          <>
            <div className="flex-1 overflow-y-auto">
              <div className="mx-auto w-full max-w-3xl">
                <ChatMessages messages={messages} connected={connected} thinking={inputState === "thinking"} />
              </div>
            </div>
            <div className="flex flex-col px-6 pb-6">
              {error && <ChatErrorNotice message={error} />}
              <div className="flex justify-center">
                {inputState === "awaiting_evidence" ? (
                  <div className="w-full max-w-3xl">
                    <EvidenceCard
                      conversationId={activeConversationId}
                      onSubmit={(text, evidence) => send(text, evidence)}
                      onCancel={(text) => send(text)}
                    />
                  </div>
                ) : inputState === "awaiting_confirm" ? (
                  <ChatConfirmActions onDecide={send} />
                ) : inputState === "pending" ? (
                  <ChatPendingNotice />
                ) : (
                  <ChatPromptBar onSend={send} disabled={inputState === "thinking"} />
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
