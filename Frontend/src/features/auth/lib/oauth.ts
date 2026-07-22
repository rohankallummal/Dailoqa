import { createRemoteJWKSet, jwtVerify } from "jose";
import { getGoogleCredentials } from "./googleCredentials";

const AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth";
const TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token";

export function buildAuthorizationUrl(state: string): string {
  const { clientId, redirectUri } = getGoogleCredentials();
  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: redirectUri,
    response_type: "code",
    scope: "openid email profile",
    access_type: "offline",
    state,
  });
  return `${AUTH_ENDPOINT}?${params.toString()}`;
}

export type GoogleTokens = {
  access_token: string;
  id_token: string;
  refresh_token?: string;
  expires_in: number;
};

export async function exchangeCodeForTokens(code: string): Promise<GoogleTokens> {
  const { clientId, clientSecret, redirectUri } = getGoogleCredentials();
  const response = await fetch(TOKEN_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      code,
      client_id: clientId,
      client_secret: clientSecret,
      redirect_uri: redirectUri,
      grant_type: "authorization_code",
    }),
  });
  if (!response.ok) {
    throw new Error(`Token exchange failed: ${response.status}`);
  }
  return response.json();
}

export type GoogleIdentity = { sub: string; email: string; name: string };

const GOOGLE_JWKS = createRemoteJWKSet(
  new URL("https://www.googleapis.com/oauth2/v3/certs"),
);

export async function verifyIdToken(idToken: string): Promise<GoogleIdentity> {
  const { clientId } = getGoogleCredentials();
  const { payload } = await jwtVerify(idToken, GOOGLE_JWKS, {
    issuer: ["https://accounts.google.com", "accounts.google.com"],
    audience: clientId,
  });
  return {
    sub: String(payload.sub),
    email: String(payload.email),
    name: payload.name ? String(payload.name) : String(payload.email),
  };
}
