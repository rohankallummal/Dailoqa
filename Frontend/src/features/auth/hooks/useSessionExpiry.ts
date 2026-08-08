"use client";

import { useEffect, useState } from "react";
import { subscribeToSignOut } from "../lib/sessionChannel";

async function sessionIsGone(): Promise<boolean> {
  try {
    const response = await fetch("/api/auth/session", { cache: "no-store" });
    return response.status === 401;
  } catch {
    return false;
  }
}

export function useSessionExpiry(): boolean {
  const [expired, setExpired] = useState(false);

  useEffect(() => {
    if (expired) return;

    const expire = () => setExpired(true);
    const revalidate = () => {
      if (document.visibilityState !== "visible") return;
      void sessionIsGone().then((gone) => {
        if (gone) expire();
      });
    };

    const unsubscribe = subscribeToSignOut(expire);
    window.addEventListener("focus", revalidate);
    document.addEventListener("visibilitychange", revalidate);

    return () => {
      unsubscribe();
      window.removeEventListener("focus", revalidate);
      document.removeEventListener("visibilitychange", revalidate);
    };
  }, [expired]);

  return expired;
}
