const CHANNEL_NAME = "dailoqa-session";
const SIGN_OUT = "sign-out";

let channel: BroadcastChannel | null = null;

function sharedChannel(): BroadcastChannel | null {
  if (typeof BroadcastChannel === "undefined") return null;
  channel ??= new BroadcastChannel(CHANNEL_NAME);
  return channel;
}

export function broadcastSignOut(): void {
  sharedChannel()?.postMessage(SIGN_OUT);
}

export function subscribeToSignOut(onSignOut: () => void): () => void {
  const subscription = sharedChannel();
  if (!subscription) return () => {};
  const handler = (event: MessageEvent) => {
    if (event.data === SIGN_OUT) onSignOut();
  };
  subscription.addEventListener("message", handler);
  return () => subscription.removeEventListener("message", handler);
}
