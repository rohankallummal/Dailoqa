"use client";

import { useCallback, useEffect, useRef } from "react";
import { useEventStream, type ChatEvent } from "@/features/chat";
import { useToast } from "@/shared/ui";
import { notificationsClient } from "../api/notificationsClient";

export function useNotifications() {
  const { show } = useToast();
  const seen = useRef<Set<string>>(new Set());

  const handle = useCallback(
    (notification: { id: string; title: string; body: string }) => {
      if (seen.current.has(notification.id)) return;
      seen.current.add(notification.id);
      show({ id: notification.id, title: notification.title, body: notification.body });
      void notificationsClient.markDelivered([notification.id]);
    },
    [show],
  );

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const rows = await notificationsClient.listUndelivered();
      if (!cancelled) rows.forEach((row) => handle({ id: row.id, title: row.title, body: row.body }));
    })();
    return () => {
      cancelled = true;
    };
  }, [handle]);

  const onEvent = useCallback(
    (event: ChatEvent) => {
      if (event.type === "notification") handle({ id: event.id, title: event.title, body: event.body });
    },
    [handle],
  );
  useEventStream(onEvent);
}
