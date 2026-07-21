import type { ReactNode } from "react";
import { AppShell } from "@/features/navigation";

export default function WebLayout({ children }: { children: ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
