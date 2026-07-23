import { proxyStream } from "@/features/backend-client";

export const dynamic = "force-dynamic";

export async function GET() {
  return proxyStream("/events");
}
