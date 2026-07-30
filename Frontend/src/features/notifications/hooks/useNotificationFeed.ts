"use client";

import { useCallback, useEffect, useState } from "react";
import { useEventStream, type ChatEvent } from "@/features/chat";
import { notificationsClient, type NotificationRow } from "../api/notificationsClient";

export function useNotificationFeed() {
  const [items, setItems] = useState<NotificationRow[]>([]);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const rows = await notificationsClient.listHistory();
      if (!cancelled) setItems(rows);
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const onEvent = useCallback((event: ChatEvent) => {
    if (event.type !== "notification") return;
    void notificationsClient.listHistory().then(setItems);
  }, []);
  useEventStream(onEvent);

  const markAllRead = useCallback(async () => {
    let hadUnread = false;
    setItems((previous) =>
      previous.map((item) => {
        if (item.read_at) return item;
        hadUnread = true;
        return { ...item, read_at: new Date().toISOString() };
      }),
    );
    if (!hadUnread) return;
    await notificationsClient.markAllRead();
  }, []);

  return {
    items,
    unreadCount: items.filter((item) => item.read_at === null).length,
    markAllRead,
  };
}
