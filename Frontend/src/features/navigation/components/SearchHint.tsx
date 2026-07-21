"use client";

import { useSyncExternalStore } from "react";

function subscribe() {
  return () => {};
}

function getIsMac() {
  return /mac|iphone|ipad|ipod/i.test(navigator.userAgent);
}

export function SearchHint() {
  const isMac = useSyncExternalStore(subscribe, getIsMac, () => false);

  return (
    <kbd className="pointer-events-none flex shrink-0 items-center rounded border border-line bg-white px-1.5 py-0.5 font-sans text-[11px] font-medium text-ink-muted">
      {isMac ? "⌘K" : "Ctrl K"}
    </kbd>
  );
}
