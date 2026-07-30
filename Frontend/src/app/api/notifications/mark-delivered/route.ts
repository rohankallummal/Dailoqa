import { proxyJson } from "@/features/backend-client";

export async function POST(request: Request) {
  return proxyJson("POST", "/notifications/mark-delivered", await request.text());
}
