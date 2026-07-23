import { proxyJson } from "@/features/backend-client";

export async function GET(_request: Request, ctx: { params: Promise<{ id: string }> }) {
  const { id } = await ctx.params;
  return proxyJson("GET", `/conversations/${encodeURIComponent(id)}/messages`);
}
