import type { ReactNode } from "react";
import { Sidebar } from "@/components/sidebar/Sidebar";

export function AppShell({
  children,
  role,
}: {
  children: ReactNode;
  role?: string;
}) {
  return (
    <div className="flex h-screen overflow-hidden bg-page">
      <Sidebar role={role} />
      <main className="min-w-0 flex-1 overflow-y-auto">{children}</main>
    </div>
  );
}
