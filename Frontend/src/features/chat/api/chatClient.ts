import type { InputState, Message } from "../lib/messageReducer";
import type { EvidenceFile } from "../lib/evidenceRules";
import type { ClientEnvironment } from "../lib/clientEnvironment";

const TIMEOUT_MS = 30000;

export class ChatRequestError extends Error {
  readonly status: number;

  constructor(status: number) {
    super(`chat request failed: ${status}`);
    this.status = status;
  }
}

async function withTimeout(input: string, init?: RequestInit): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    return await fetch(input, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

export const chatClient = {
  async sendMessage(body: {
    conversationId?: string;
    surface: string;
    text: string;
    evidence?: EvidenceFile[];
    clientEnvironment?: ClientEnvironment;
  }) {
    const res = await withTimeout("/api/chat/send", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        conversation_id: body.conversationId,
        surface: body.surface,
        text: body.text,
        evidence: body.evidence,
        client_environment: body.clientEnvironment,
      }),
    });
    if (!res.ok) throw new ChatRequestError(res.status);
    return (await res.json()) as { conversation_id: string; turn_id: string; input_state: InputState };
  },
  async listConversations(surface: string) {
    const res = await withTimeout(`/api/conversations?surface=${surface}`);
    if (!res.ok) throw new Error(`list failed: ${res.status}`);
    return (await res.json()) as { id: string; title: string | null; updated_at: string }[];
  },
  async listMessages(id: string) {
    const res = await withTimeout(`/api/conversations/${id}/messages`);
    if (!res.ok) throw new Error(`messages failed: ${res.status}`);
    return (await res.json()) as { messages: Message[]; input_state: InputState };
  },
  async deleteConversation(id: string) {
    const res = await withTimeout(`/api/conversations/${id}`, { method: "DELETE" });
    if (!res.ok) throw new ChatRequestError(res.status);
  },
};
