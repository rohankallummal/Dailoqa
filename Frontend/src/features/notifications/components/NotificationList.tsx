"use client";

import type { NotificationRow } from "../api/notificationsClient";
import { relativeTime } from "../lib/relativeTime";

export function NotificationList({ items }: { items: NotificationRow[] }) {
  if (items.length === 0) {
    return <p className="px-4 py-10 text-center text-sm text-ink-muted">No notifications yet.</p>;
  }

  return (
    <div className="max-h-96 overflow-y-auto [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-scrollbar [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar]:w-1.5">
      {items.map((item) => {
        const unread = item.read_at === null;
        return (
          <div key={item.id} className="border-b border-line px-4 py-3 last:border-b-0">
            <div className="flex items-start justify-between gap-2">
              <span className={`text-sm text-ink ${unread ? "font-semibold" : "font-medium"}`}>{item.title}</span>
              {unread && <span className="mt-1.5 h-2 w-2 flex-shrink-0 rounded-full bg-accent" />}
            </div>
            <p className="mt-0.5 text-sm leading-relaxed text-ink-soft">{item.body}</p>
            <div className="mt-1 text-xs text-ink-muted">{relativeTime(item.created_at)}</div>
          </div>
        );
      })}
    </div>
  );
}
