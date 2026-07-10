import type { ReactNode } from "react";
import { cookies } from "next/headers";
import { AppShell } from "@/components/layout/AppShell";

export default async function WebLayout({ children }: { children: ReactNode }) {
  const role = (await cookies()).get("role")?.value;
  return <AppShell role={role}>{children}</AppShell>;
}
