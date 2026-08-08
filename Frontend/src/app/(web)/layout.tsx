import type { ReactNode } from "react";
import { redirect } from "next/navigation";
import { AppShell } from "@/features/navigation";
import { SessionBoundary, getSession } from "@/features/auth";

export default async function WebLayout({ children }: { children: ReactNode }) {
  const session = await getSession();
  if (!session) redirect("/");
  return (
    <SessionBoundary>
      <AppShell userName={session.name}>{children}</AppShell>
    </SessionBoundary>
  );
}
