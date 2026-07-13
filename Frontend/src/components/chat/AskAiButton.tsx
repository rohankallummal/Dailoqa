"use client";

import { MessageSquare } from "lucide-react";
import { useChatPanel } from "@/components/chat/ChatPanelProvider";

export function AskAiButton() {
  const { open, togglePanel } = useChatPanel();

  return (
    <button
      type="button"
      onClick={togglePanel}
      aria-expanded={open}
      aria-label="Ask AI"
      className={`flex h-9 items-center gap-2 rounded-lg border px-3 text-sm font-medium transition-colors duration-200 ${
        open
          ? "border-accent bg-active text-accent"
          : "border-line bg-page text-ink-soft hover:bg-hover hover:text-ink"
      }`}
    >
      <MessageSquare className="h-4 w-4 shrink-0" />
      Ask AI
    </button>
  );
}
