"use client";

import type { ReactNode } from "react";
import { useSessionExpiry } from "../hooks/useSessionExpiry";
import { SessionExpired } from "./SessionExpired";

export function SessionBoundary({ children }: { children: ReactNode }) {
  const expired = useSessionExpiry();
  if (expired) return <SessionExpired />;
  return <>{children}</>;
}
