import { proxyJson } from "@/features/backend-client";

export async function POST(request: Request) {
  return proxyJson("POST", "/conversations/abandon", await request.text());
}
