export type NotificationRow = { id: string; type: string; title: string; body: string; jira_key: string | null };

export const notificationsClient = {
  async listUnread(): Promise<NotificationRow[]> {
    try {
      const res = await fetch("/api/notifications");
      if (!res.ok) return [];
      return (await res.json()) as NotificationRow[];
    } catch {
      return [];
    }
  },
  async markRead(ids: string[]): Promise<void> {
    if (ids.length === 0) return;
    try {
      await fetch("/api/notifications/mark-read", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ids }),
      });
    } catch {
      return;
    }
  },
};
