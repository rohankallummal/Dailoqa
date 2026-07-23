import { logout } from "../api/actions";

export async function signOut(): Promise<void> {
  try {
    await fetch("/api/conversations/abandon", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
  } catch {}
  await logout();
}
