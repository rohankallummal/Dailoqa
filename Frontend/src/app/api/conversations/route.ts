import { proxyJson } from "@/features/backend-client";

export async function GET(request: Request) {
  const surface = new URL(request.url).searchParams.get("surface") ?? "";
  return proxyJson("GET", `/conversations?surface=${encodeURIComponent(surface)}`);
}
