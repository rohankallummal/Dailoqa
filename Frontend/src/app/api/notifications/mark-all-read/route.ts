import { proxyJson } from "@/features/backend-client";

export async function POST() {
  return proxyJson("POST", "/notifications/mark-all-read", "{}");
}
