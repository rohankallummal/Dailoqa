import { proxyJson } from "@/features/backend-client";

export async function GET() {
  return proxyJson("GET", "/notifications");
}
