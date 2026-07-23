import type { Message } from "../lib/messageReducer";

const TIMEOUT_MS = 15000;

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
  async sendMessage(body: { conversationId?: string; surface: string; text: string }) {
    const res = await withTimeout("/api/chat/send", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conversation_id: body.conversationId, surface: body.surface, text: body.text }),
    });
    if (!res.ok) throw new Error(`send failed: ${res.status}`);
    return (await res.json()) as { conversation_id: string; turn_id: string };
  },
  async listConversations(surface: string) {
    const res = await withTimeout(`/api/conversations?surface=${surface}`);
    if (!res.ok) throw new Error(`list failed: ${res.status}`);
    return (await res.json()) as { id: string; title: string | null; updated_at: string }[];
  },
  async listMessages(id: string) {
    const res = await withTimeout(`/api/conversations/${id}/messages`);
    if (!res.ok) throw new Error(`messages failed: ${res.status}`);
    return (await res.json()) as Message[];
  },
  async deleteConversation(id: string) {
    await withTimeout(`/api/conversations/${id}`, { method: "DELETE" });
  },
};
