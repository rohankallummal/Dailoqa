"use client";

import { createContext, useContext, useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";
import { parseEvent } from "../lib/eventStream";
import type { ChatEvent } from "../lib/messageReducer";

type Handler = (event: ChatEvent) => void;
type StreamValue = { subscribe: (handler: Handler) => () => void; connected: boolean };

const ChatStreamContext = createContext<StreamValue | null>(null);

const RECONNECT_BASE_MS = 1000;
const RECONNECT_MAX_MS = 30000;

export function ChatStreamProvider({ children }: { children: ReactNode }) {
  const handlers = useRef(new Set<Handler>());
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    let source: EventSource | null = null;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let attempt = 0;
    let stopped = false;

    const connect = () => {
      const instance = new EventSource("/api/events");
      source = instance;
      instance.onopen = () => {
        attempt = 0;
        setConnected(true);
      };
      instance.onerror = () => {
        setConnected(false);
        if (instance.readyState !== EventSource.CLOSED) return;
        instance.close();
        if (stopped) return;
        timer = setTimeout(connect, Math.min(RECONNECT_BASE_MS * 2 ** attempt, RECONNECT_MAX_MS));
        attempt += 1;
      };
      instance.onmessage = (message) => {
        const event = parseEvent(message.data);
        if (event) handlers.current.forEach((handler) => handler(event));
      };
    };

    connect();

    return () => {
      stopped = true;
      clearTimeout(timer);
      source?.close();
    };
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
