"use client";

import { createContext, useContext, useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";
import { parseEvent } from "../lib/eventStream";
import type { ChatEvent } from "../lib/messageReducer";

type Handler = (event: ChatEvent) => void;
type StreamValue = { subscribe: (handler: Handler) => () => void; connected: boolean };

const ChatStreamContext = createContext<StreamValue | null>(null);

export function ChatStreamProvider({ children }: { children: ReactNode }) {
  const handlers = useRef(new Set<Handler>());
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const source = new EventSource("/api/events");
    source.onopen = () => setConnected(true);
    source.onerror = () => setConnected(false);
    source.onmessage = (message) => {
      const event = parseEvent(message.data);
      if (event) handlers.current.forEach((handler) => handler(event));
    };
    return () => source.close();
  }, []);

  const value = useMemo<StreamValue>(
    () => ({
      subscribe: (handler) => {
        handlers.current.add(handler);
        return () => {
          handlers.current.delete(handler);
        };
      },
      connected,
    }),
    [connected],
  );

  return <ChatStreamContext.Provider value={value}>{children}</ChatStreamContext.Provider>;
}

export function useEventStream(handler: (event: ChatEvent) => void) {
  const context = useContext(ChatStreamContext);
  if (!context) throw new Error("useEventStream must be used within a ChatStreamProvider");
  const { subscribe, connected } = context;
  useEffect(() => subscribe(handler), [subscribe, handler]);
  return { connected };
}
