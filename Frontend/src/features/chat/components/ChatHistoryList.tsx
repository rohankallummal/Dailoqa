"use client";

import { useEffect, useRef, useState } from "react";
import { Trash2 } from "lucide-react";
import { chatClient } from "../api/chatClient";

type Conversation = { id: string; title: string | null; updated_at: string };

type Status = "loading" | "ready" | "error";

const TITLE_POLL_MS = 1500;
const MAX_TITLE_POLLS = 8;
const MAX_LOAD_RETRIES = 4;
const RETRY_BASE_MS = 400;

function TitleSkeleton() {
  return (
    <span className="flex h-5 items-center" aria-hidden="true">
      <span className="h-3.5 w-3/5 animate-pulse rounded bg-line" />
    </span>
  );
}

export function ChatHistoryList({
  surface,
  onOpen,
  onDeleted,
  activeConversationId,
}: {
  surface: string;
  onOpen: (id: string) => void;
  onDeleted?: (id: string) => void;
  activeConversationId?: string;
}) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [status, setStatus] = useState<Status>("loading");
  const [reloadToken, setReloadToken] = useState(0);
  const [poll, setPoll] = useState({ key: "", attempts: 0 });

  const failures = useRef(0);

  useEffect(() => {
    let ignore = false;
    let timer: ReturnType<typeof setTimeout> | undefined;
    chatClient
      .listConversations(surface)
      .then((rows) => {
        if (ignore) return;
        failures.current = 0;
        setConversations(rows);
        setStatus("ready");
      })
      .catch(() => {
        if (ignore) return;
        if (failures.current >= MAX_LOAD_RETRIES) {
          setStatus("error");
          return;
        }
        const delay = RETRY_BASE_MS * 2 ** failures.current;
        failures.current += 1;
        timer = setTimeout(() => setReloadToken((token) => token + 1), delay);
      });
    return () => {
      ignore = true;
      clearTimeout(timer);
    };
  }, [surface, reloadToken, activeConversationId]);

  const pendingKey = conversations
    .filter((conversation) => conversation.title === null)
    .map((conversation) => conversation.id)
    .sort()
    .join(",");

  const attempts = poll.key === pendingKey ? poll.attempts : 0;
  const stoppedWaiting = Boolean(pendingKey) && attempts >= MAX_TITLE_POLLS;

  useEffect(() => {
    if (!pendingKey || attempts >= MAX_TITLE_POLLS) return;
    const timer = setTimeout(() => {
      setPoll({ key: pendingKey, attempts: attempts + 1 });
      setReloadToken((token) => token + 1);
    }, TITLE_POLL_MS);
    return () => clearTimeout(timer);
  }, [pendingKey, attempts]);

  const reload = () => {
    failures.current = 0;
    setStatus("loading");
    setReloadToken((token) => token + 1);
  };

  const remove = async (id: string) => {
    const deleted = await chatClient
      .deleteConversation(id)
      .then(() => true)
      .catch(() => false);
    if (deleted) onDeleted?.(id);
    reload();
  };

  if (status === "loading") {
    return <p className="px-2 py-4 text-center text-[13px] text-ink-muted">Loading…</p>;
  }

  if (status === "error") {
    return (
      <div className="flex flex-col items-center gap-2 px-2 py-4 text-center">
        <p className="text-[13px] text-ink-muted">Unable to load conversations</p>
        <button
          type="button"
          onClick={reload}
          className="text-[13px] font-medium text-accent transition-opacity duration-200 hover:opacity-80"
        >
          Try again
        </button>
      </div>
    );
  }

  if (conversations.length === 0) {
    return <p className="px-2 py-4 text-center text-[13px] text-ink-muted">No conversations yet</p>;
  }

  return (
    <ul className="flex flex-col gap-1">
      {conversations.map((conversation) => {
        const titlePending = conversation.title === null && !stoppedWaiting;
        return (
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
                aria-label={titlePending ? "Conversation, title loading" : undefined}
                className="min-w-0 flex-1 truncate text-left"
              >
                {titlePending ? <TitleSkeleton /> : (conversation.title ?? "New conversation")}
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
        );
      })}
    </ul>
  );
}
