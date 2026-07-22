import type { ReactNode } from "react";
import { redirect } from "next/navigation";
import { AppShell } from "@/features/navigation";
import { getSession } from "@/features/auth";

export default async function WebLayout({ children }: { children: ReactNode }) {
  if (!(await getSession())) redirect("/");
  return <AppShell>{children}</AppShell>;
}
