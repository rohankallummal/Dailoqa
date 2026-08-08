import type { ReactNode } from "react";
import { redirect } from "next/navigation";
import { getSession } from "@/features/auth";

export default async function AskAiLayout({ children }: { children: ReactNode }) {
  const session = await getSession();
  if (!session) redirect("/");
  return <>{children}</>;
}
