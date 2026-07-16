import type { ReactNode } from "react";
import { AppShell } from "@/components/layout/AppShell";

export default function WebLayout({ children }: { children: ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
