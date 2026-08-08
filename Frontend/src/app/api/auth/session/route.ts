import { getSession } from "@/features/auth";

export const dynamic = "force-dynamic";

export async function GET() {
  const session = await getSession();
  return new Response(null, { status: session ? 204 : 401 });
}
