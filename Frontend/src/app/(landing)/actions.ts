"use server";

import { redirect } from "next/navigation";

export async function enterApp() {
  redirect("/dashboard");
}
