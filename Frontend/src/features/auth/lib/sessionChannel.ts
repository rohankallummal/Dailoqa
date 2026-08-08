const CHANNEL_NAME = "dailoqa-session";
const SIGN_OUT = "sign-out";

function openChannel(): BroadcastChannel | null {
  if (typeof BroadcastChannel === "undefined") return null;
  return new BroadcastChannel(CHANNEL_NAME);
}

export function broadcastSignOut(): void {
  const channel = openChannel();
  if (!channel) return;
  channel.postMessage(SIGN_OUT);
  channel.close();
}

export function subscribeToSignOut(onSignOut: () => void): () => void {
  const channel = openChannel();
  if (!channel) return () => {};
  channel.onmessage = (event) => {
    if (event.data === SIGN_OUT) onSignOut();
  };
  return () => channel.close();
}
