"use client";

import { useState } from "react";
import { PanelLeftOpen, Sparkles } from "lucide-react";
import { ChatHistorySidebar } from "@/components/chat/ChatHistorySidebar";
import { ChatPromptBar } from "@/components/chat/ChatPromptBar";

export function AskAiWorkspace() {
  const [collapsed, setCollapsed] = useState(false);
  const toggle = () => setCollapsed((value) => !value);

  return (
    <div className="flex h-screen overflow-hidden bg-page">
      <ChatHistorySidebar collapsed={collapsed} onToggle={toggle} />

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
            className="flex h-9 items-center gap-2 rounded-lg border border-line bg-page px-3.5 text-sm font-medium text-ink-soft transition-colors duration-200 hover:bg-hover hover:text-ink"
          >
            <Sparkles className="h-4 w-4 text-accent" strokeWidth={1.8} />
            New Chat
          </button>
        </header>

        <div className="flex flex-1 flex-col items-center justify-center gap-8 px-6">
          <h1 className="text-3xl font-semibold tracking-tight text-ink">
            What can I help with?
          </h1>
          <ChatPromptBar />
        </div>
      </div>
    </div>
  );
}
