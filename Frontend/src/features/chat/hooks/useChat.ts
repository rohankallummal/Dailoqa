"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ChatRequestError, chatClient } from "../api/chatClient";
import { applyDelta, type ChatEvent, type InputState, type Message } from "../lib/messageReducer";
import type { EvidenceFile } from "../lib/evidenceRules";
import { readClientEnvironment } from "../lib/clientEnvironment";
import { useEventStream } from "./useEventStream";

const SEND_FAILED = "Your message could not be sent. Please try again.";
const SEND_BUSY = "The assistant is still replying. Please send that again in a moment.";
const CONVERSATION_GONE = "That conversation no longer exists. We've started a new chat for you.";
const STALLED_TURN_MS = 120000;

export function useChat(surface: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputState, setInputState] = useState<InputState>("open");
  const [activeConversationId, setActiveConversationId] = useState<string | undefined>();
  const [error, setError] = useState<string | null>(null);
  const conversationRef = useRef<string | undefined>(undefined);
  const stallTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const track = useCallback((id: string | undefined) => {
    conversationRef.current = id;
    setActiveConversationId(id);
  }, []);

  const load = useCallback(async (id: string) => {
    const { messages: history, input_state } = await chatClient.listMessages(id);
    setMessages(history);
    setInputState(input_state);
  }, []);

  const clearStallTimer = useCallback(() => {
    clearTimeout(stallTimer.current);
    stallTimer.current = undefined;
  }, []);

  const resync = useCallback(async () => {
    const id = conversationRef.current;
    if (!id) return;
    try {
      await load(id);
    } catch {
      setError(SEND_FAILED);
    }
  }, [load]);

  const armStallTimer = useCallback(() => {
    clearStallTimer();
    stallTimer.current = setTimeout(() => {
      void resync();
    }, STALLED_TURN_MS);
  }, [clearStallTimer, resync]);

  useEffect(() => clearStallTimer, [clearStallTimer]);

  const onEvent = useCallback(
    (event: ChatEvent) => {
      if (event.type === "notification") {
        if (conversationRef.current && event.conversationId === conversationRef.current) {
          void resync();
        }
        return;
      }
      if (conversationRef.current && event.conversationId !== conversationRef.current) return;
      if (!conversationRef.current && stallTimer.current === undefined) return;
      if (!conversationRef.current) track(event.conversationId);
      clearStallTimer();
      setMessages((previous) => applyDelta(previous, event));
      if (event.inputState) setInputState(event.inputState);
    },
    [clearStallTimer, resync, track],
  );
  const { connected } = useEventStream(onEvent);

  const wasConnected = useRef(connected);
  useEffect(() => {
    const reconnected = connected && !wasConnected.current;
    wasConnected.current = connected;
    if (reconnected) void resync();
  }, [connected, resync]);

  const send = useCallback(
    async (text: string, evidence?: EvidenceFile[]) => {
      const optimisticId = `u-${Date.now()}`;
      setError(null);
      setInputState("thinking");
      setMessages((previous) => [...previous, { id: optimisticId, role: "user", content: text }]);
      armStallTimer();
      try {
        const { conversation_id } = await chatClient.sendMessage({
          conversationId: conversationRef.current,
          surface,
          text,
          evidence,
          clientEnvironment: readClientEnvironment(),
        });
        track(conversation_id);
      } catch (failure) {
        setMessages((previous) => previous.filter((message) => message.id !== optimisticId));
        if (failure instanceof ChatRequestError && failure.status === 409) {
          setError(SEND_BUSY);
          return;
        }
        clearStallTimer();
        setInputState("open");
        if (failure instanceof ChatRequestError && failure.status === 404) {
          setMessages([]);
          track(undefined);
          setError(CONVERSATION_GONE);
          return;
        }
        setError(SEND_FAILED);
      }
    },
    [armStallTimer, clearStallTimer, surface, track],
  );

  const newChat = useCallback(() => {
    clearStallTimer();
    track(undefined);
    setMessages([]);
    setInputState("open");
    setError(null);
  }, [clearStallTimer, track]);

  const openConversation = useCallback(
    async (id: string) => {
      clearStallTimer();
      track(id);
      setError(null);
      await load(id);
    },
    [clearStallTimer, load, track],
  );

  return {
    messages,
    send,
    connected,
    inputState,
    activeConversationId,
    error,
    newChat,
    openConversation,
  };
}
