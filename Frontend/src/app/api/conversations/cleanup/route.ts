import { proxyJson } from "@/features/backend-client";

export async function POST(request: Request) {
  return proxyJson("POST", "/conversations/cleanup", await request.text());
}
