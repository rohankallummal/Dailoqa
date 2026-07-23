"use client";

import { useCallback, useState } from "react";
import { chatClient } from "../api/chatClient";
import { applyDelta, type ChatEvent, type Message } from "../lib/messageReducer";
import { useEventStream } from "./useEventStream";

export function useChat(surface: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | undefined>();

  const onEvent = useCallback(
    (event: ChatEvent) => {
      if (event.type !== "delta") return;
      if (activeConversationId && event.conversationId !== activeConversationId) return;
      setMessages((previous) => applyDelta(previous, event));
    },
    [activeConversationId],
  );
  const { connected } = useEventStream(onEvent);

  const send = useCallback(
    async (text: string) => {
      setMessages((previous) => [...previous, { id: `u-${Date.now()}`, role: "user", content: text }]);
      const { conversation_id } = await chatClient.sendMessage({ conversationId: activeConversationId, surface, text });
      setActiveConversationId(conversation_id);
    },
    [activeConversationId, surface],
  );

  const newChat = useCallback(() => {
    setActiveConversationId(undefined);
    setMessages([]);
  }, []);

  const openConversation = useCallback(async (id: string) => {
    setActiveConversationId(id);
    setMessages(await chatClient.listMessages(id));
  }, []);

  return { messages, send, connected, activeConversationId, newChat, openConversation };
}
