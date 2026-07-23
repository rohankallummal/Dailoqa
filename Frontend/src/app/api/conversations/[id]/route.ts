import { proxyJson } from "@/features/backend-client";

export async function DELETE(_request: Request, ctx: { params: Promise<{ id: string }> }) {
  const { id } = await ctx.params;
  return proxyJson("DELETE", `/conversations/${encodeURIComponent(id)}`);
}
