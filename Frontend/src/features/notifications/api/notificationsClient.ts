export type NotificationRow = {
  id: string;
  type: string;
  title: string;
  body: string;
  jira_key: string | null;
  conversation_id: string | null;
  read_at: string | null;
  created_at: string | null;
};

async function getRows(path: string): Promise<NotificationRow[]> {
  try {
    const res = await fetch(path);
    if (!res.ok) return [];
    return (await res.json()) as NotificationRow[];
  } catch {
    return [];
  }
}

async function post(path: string, body?: unknown): Promise<void> {
  try {
    await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body ?? {}),
    });
  } catch {
    return;
  }
}

export const notificationsClient = {
  listUndelivered: () => getRows("/api/notifications"),
  listHistory: () => getRows("/api/notifications/history"),
  async markDelivered(ids: string[]): Promise<void> {
    if (ids.length === 0) return;
    await post("/api/notifications/mark-delivered", { ids });
  },
  markAllRead: () => post("/api/notifications/mark-all-read"),
};
