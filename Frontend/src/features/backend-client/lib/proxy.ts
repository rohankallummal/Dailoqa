import { getSession } from "@/features/auth";
import { getBackendUrl } from "./env";
import { mintServiceToken } from "./serviceJwt";

async function authHeader(): Promise<string | null> {
  const session = await getSession();
  if (!session) return null;
  return `Bearer ${await mintServiceToken(session.sub, session.userId)}`;
}

export async function proxyJson(method: string, path: string, body?: string): Promise<Response> {
  const authorization = await authHeader();
  if (!authorization) return new Response("Unauthorized", { status: 401 });
  const headers: Record<string, string> = { Authorization: authorization };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const upstream = await fetch(`${getBackendUrl()}${path}`, { method, headers, body, cache: "no-store" });
  return new Response(await upstream.text(), {
    status: upstream.status,
    headers: { "Content-Type": upstream.headers.get("content-type") ?? "application/json" },
  });
}

const STREAM_HEADERS = {
  "Content-Type": "text/event-stream",
  "Cache-Control": "no-cache, no-transform",
  "X-Accel-Buffering": "no",
  Connection: "keep-alive",
};

const STREAM_RETRY_MS = 3000;

function retryStream(): Response {
  return new Response(`retry: ${STREAM_RETRY_MS}\n\n`, { status: 200, headers: STREAM_HEADERS });
}

export async function proxyStream(path: string): Promise<Response> {
  const authorization = await authHeader();
  if (!authorization) return new Response("Unauthorized", { status: 401 });

  let upstream: Response;
  try {
    upstream = await fetch(`${getBackendUrl()}${path}`, {
      headers: { Authorization: authorization, Accept: "text/event-stream" },
      cache: "no-store",
    });
  } catch {
    return retryStream();
  }

  if (!upstream.ok) return retryStream();

  return new Response(upstream.body, { status: 200, headers: STREAM_HEADERS });
}
