export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  stage?: string;
  streaming?: boolean;
};

export type InputState = "open" | "awaiting_confirm" | "awaiting_evidence" | "pending" | "thinking";

export type ChatEvent =
  | {
      type: "delta";
      turnId: string;
      text: string;
      conversationId: string;
      stage?: string;
      /** Set on the turn's final event: `text` is the whole answer, not another delta. */
      replace?: boolean;
      tool?: string | null;
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
  if (event.stage === "tool_status") return messages;
  const streaming = event.stage === "token";
  const index = messages.findIndex((message) => message.id === event.turnId);

  // The agent was asked to rewrite its answer, so what has been streamed belongs to the draft
  // being replaced. Emptying the bubble rather than removing it keeps the turn in place and
  // avoids the message jumping to the bottom of the list when the rewrite starts arriving.
  if (event.stage === "restart") {
    if (index === -1) return messages;
    const reset = [...messages];
    reset[index] = { ...reset[index], content: "", streaming: true };
    return reset;
  }

  if (index === -1) {
    if (!event.text) return messages;
    return [
      ...messages,
      { id: event.turnId, role: "assistant", content: event.text, stage: event.stage, streaming },
    ];
  }
  const next = [...messages];
  next[index] = {
    ...next[index],
    // The turn's final event carries the whole answer, so it overwrites rather than appends.
    // That makes the last word the server's: if a `restart` was missed and a superseded draft
    // is still on screen, this corrects it, and what the user ends up reading always matches
    // what was persisted. Streaming still appends, so the answer arrives as it is written.
    content: event.replace ? event.text : next[index].content + event.text,
    stage: event.stage ?? next[index].stage,
    streaming,
  };
  return next;
}
