"use client";

import { useEffect, useRef, useState } from "react";
import { Bell } from "lucide-react";
import { useNotificationFeed } from "../hooks/useNotificationFeed";
import { NotificationList } from "./NotificationList";

export function NotificationBell() {
  const { items, unreadCount, markAllRead } = useNotificationFeed();
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (event: PointerEvent) => {
      if (containerRef.current?.contains(event.target as Node)) return;
      setOpen(false);
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  const toggle = () => {
    const next = !open;
    setOpen(next);
    if (next) void markAllRead();
  };

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        onClick={toggle}
        aria-label="Notifications"
        aria-expanded={open}
        className="relative flex h-9 w-9 items-center justify-center rounded-lg border border-transparent transition-colors duration-200 hover:border-line hover:bg-hover"
      >
        <Bell className="h-[18px] w-[18px] text-ink-soft" />
        {unreadCount > 0 && (
          <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-accent px-1 text-[10px] font-semibold text-white">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-11 z-50 w-[380px] overflow-hidden rounded-xl border border-line bg-white shadow-[0_12px_32px_-12px_rgba(20,23,28,0.3)]">
          <header className="flex h-12 flex-shrink-0 items-center border-b border-line px-4">
            <span className="text-sm font-semibold text-ink">Notifications</span>
          </header>
          <NotificationList items={items} />
        </div>
      )}
    </div>
  );
}
