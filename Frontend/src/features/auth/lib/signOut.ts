import { logout } from "../api/actions";
import { broadcastSignOut } from "./sessionChannel";

export async function signOut(): Promise<void> {
  try {
    await fetch("/api/conversations/cleanup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
  } catch {}
  broadcastSignOut();
  await logout();
}
