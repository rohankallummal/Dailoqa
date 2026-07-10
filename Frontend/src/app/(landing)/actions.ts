"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export async function enterApp(role: string) {
  const store = await cookies();
  store.set("role", role === "admin" ? "admin" : "user", { path: "/" });
  redirect("/dashboard");
}
