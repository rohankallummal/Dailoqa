"use client";

import { useNotifications } from "../hooks/useNotifications";

export function NotificationsListener() {
  useNotifications();
  return null;
}
