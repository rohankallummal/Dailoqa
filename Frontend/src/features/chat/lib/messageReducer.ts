export type Message = { id: string; role: "user" | "assistant"; content: string; stage?: string };

export type InputState = "open" | "awaiting_confirm" | "awaiting_evidence" | "pending" | "thinking";

export type ChatEvent =
  | {
      type: "delta";
      turnId: string;
      text: string;
      conversationId: string;
      stage?: string;
      inputState?: InputState;
    }
  | {
      type: "notification";
      id: string;
      title: string;
      body: string;
      jiraKey?: string;
      notificationType?: string;
      conversationId?: string;
    };

export function applyDelta(messages: Message[], event: Extract<ChatEvent, { type: "delta" }>): Message[] {
  const index = messages.findIndex((message) => message.id === event.turnId);
  if (index === -1) {
    if (!event.text) return messages;
    return [...messages, { id: event.turnId, role: "assistant", content: event.text, stage: event.stage }];
  }
  const next = [...messages];
  next[index] = { ...next[index], content: next[index].content + event.text, stage: event.stage ?? next[index].stage };
  return next;
}
