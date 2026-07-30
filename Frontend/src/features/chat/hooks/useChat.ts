"use client";

import { useCallback, useState } from "react";
import { chatClient } from "../api/chatClient";
import { applyDelta, type ChatEvent, type InputState, type Message } from "../lib/messageReducer";
import type { EvidenceFile } from "../lib/evidenceRules";
import { useEventStream } from "./useEventStream";

const SEND_FAILED = "Your message could not be sent. Please try again.";

export function useChat(surface: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputState, setInputState] = useState<InputState>("open");
  const [activeConversationId, setActiveConversationId] = useState<string | undefined>();
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (id: string) => {
    const { messages: history, input_state } = await chatClient.listMessages(id);
    setMessages(history);
    setInputState(input_state);
  }, []);

  const onEvent = useCallback(
    (event: ChatEvent) => {
      if (event.type === "notification") {
        if (activeConversationId && event.conversationId === activeConversationId) {
          void load(activeConversationId);
        }
        return;
      }
      if (activeConversationId && event.conversationId !== activeConversationId) return;
      setMessages((previous) => applyDelta(previous, event));
      if (event.inputState) setInputState(event.inputState);
    },
    [activeConversationId, load],
  );
  const { connected } = useEventStream(onEvent);

  const send = useCallback(
    async (text: string, evidence?: EvidenceFile[]) => {
      const optimisticId = `u-${Date.now()}`;
      setError(null);
      setMessages((previous) => [...previous, { id: optimisticId, role: "user", content: text }]);
      try {
        const { conversation_id, input_state } = await chatClient.sendMessage({
          conversationId: activeConversationId,
          surface,
          text,
          evidence,
        });
        setActiveConversationId(conversation_id);
        setInputState(input_state);
      } catch {
        setMessages((previous) => previous.filter((message) => message.id !== optimisticId));
        setError(SEND_FAILED);
      }
    },
    [activeConversationId, surface],
  );

  const newChat = useCallback(() => {
    setActiveConversationId(undefined);
    setMessages([]);
    setInputState("open");
    setError(null);
  }, []);

  const openConversation = useCallback(
    async (id: string) => {
      setActiveConversationId(id);
      setError(null);
      await load(id);
    },
    [load],
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
