import { NextResponse, type NextRequest } from "next/server";
import { cookies } from "next/headers";
import { exchangeCodeForTokens, verifyIdToken } from "./oauth";
import { upsertUserFromGoogle } from "./users";
import { createSessionToken, sessionCookieOptions, SESSION_COOKIE } from "./session";
import { getAppUrl } from "./env";

const STATE_COOKIE = "oauth_state";

export async function handleGoogleCallback(request: NextRequest): Promise<Response> {
  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");
  const base = getAppUrl();

  const cookieStore = await cookies();
  const expectedState = cookieStore.get(STATE_COOKIE)?.value;

  if (url.searchParams.get("error") || !code || !state || state !== expectedState) {
    return NextResponse.redirect(new URL("/?error=oauth", base));
  }

  try {
    const tokens = await exchangeCodeForTokens(code);
    const identity = await verifyIdToken(tokens.id_token);
    const { userId } = await upsertUserFromGoogle(identity, tokens.refresh_token);
    const token = await createSessionToken({
      userId,
      sub: identity.sub,
      email: identity.email,
      name: identity.name,
    });

    const response = NextResponse.redirect(new URL("/dashboard", base));
    response.cookies.set(SESSION_COOKIE, token, sessionCookieOptions());
    response.cookies.set(STATE_COOKIE, "", { path: "/", maxAge: 0 });
    return response;
  } catch {
    const response = NextResponse.redirect(new URL("/?error=oauth", base));
    response.cookies.set(STATE_COOKIE, "", { path: "/", maxAge: 0 });
    return response;
  }
}
