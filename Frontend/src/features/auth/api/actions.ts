"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { randomBytes } from "node:crypto";
import { buildAuthorizationUrl } from "../lib/oauth";
import { clearSessionCookie } from "../lib/session";

const STATE_COOKIE = "oauth_state";

export async function signInWithGoogle(): Promise<void> {
  const state = randomBytes(16).toString("hex");
  (await cookies()).set(STATE_COOKIE, state, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: 600,
  });
  redirect(buildAuthorizationUrl(state));
}

export async function logout(): Promise<void> {
  await clearSessionCookie();
  redirect("/");
}
