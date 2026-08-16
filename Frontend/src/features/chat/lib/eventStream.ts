import type { ChatEvent } from "./messageReducer";

export function parseEvent(data: string): ChatEvent | null {
  try {
    const raw = JSON.parse(data);
    if (raw.type === "delta") {
      return {
        type: "delta",
        turnId: raw.turn_id,
        text: raw.text,
        conversationId: raw.conversation_id,
        stage: raw.stage,
        replace: raw.replace ?? false,
        tool: raw.tool ?? null,
        inputState: raw.input_state,
      };
    }
    if (raw.type === "notification") {
      return {
        type: "notification",
        id: raw.id,
        title: raw.title,
        body: raw.body,
        jiraKey: raw.jira_key,
        notificationType: raw.notification_type,
        conversationId: raw.conversation_id,
      };
    }
    return null;
  } catch {
    return null;
  }
}
