"use client";

import { useCallback, useEffect, useState } from "react";
import { Trash2 } from "lucide-react";
import { chatClient } from "../api/chatClient";

type Conversation = { id: string; title: string | null; updated_at: string };

export function ChatHistoryList({
  surface,
  onOpen,
  activeConversationId,
}: {
  surface: string;
  onOpen: (id: string) => void;
  activeConversationId?: string;
}) {
  const [conversations, setConversations] = useState<Conversation[]>([]);

  const refresh = useCallback(async () => {
    try {
      setConversations(await chatClient.listConversations(surface));
    } catch {
      setConversations([]);
    }
  }, [surface]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const remove = async (id: string) => {
    await chatClient.deleteConversation(id);
    await refresh();
  };

  if (conversations.length === 0) {
    return <p className="px-2 py-4 text-center text-[13px] text-ink-muted">No conversations yet</p>;
  }

  return (
    <ul className="flex flex-col gap-1">
      {conversations.map((conversation) => (
        <li key={conversation.id}>
          <div
            className={`group flex items-center justify-between gap-2 rounded-lg px-3 py-2 text-sm transition-colors duration-200 ${
              conversation.id === activeConversationId
                ? "bg-active text-ink"
                : "text-ink-soft hover:bg-hover hover:text-ink"
            }`}
          >
            <button
              type="button"
              onClick={() => onOpen(conversation.id)}
              className="min-w-0 flex-1 truncate text-left"
            >
              {conversation.title ?? "New conversation"}
            </button>
            <button
              type="button"
              onClick={() => remove(conversation.id)}
              aria-label="Delete conversation"
              className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-md text-ink-muted opacity-0 transition-opacity duration-200 hover:bg-line hover:text-ink group-hover:opacity-100"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}
