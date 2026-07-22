import { cookies } from "next/headers";
import { SignJWT, jwtVerify } from "jose";
import { getSessionSecret } from "./env";

const SESSION_COOKIE = "session";
const MAX_AGE = 60 * 60 * 24 * 7;

export type SessionPayload = {
  userId: string;
  sub: string;
  email: string;
  name: string;
};

const secret = () => new TextEncoder().encode(getSessionSecret());

export async function createSessionToken(payload: SessionPayload): Promise<string> {
  return new SignJWT({ ...payload })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime(`${MAX_AGE}s`)
    .sign(secret());
}

export async function verifySessionToken(token: string): Promise<SessionPayload | null> {
  try {
    const { payload } = await jwtVerify(token, secret());
    return {
      userId: String(payload.userId),
      sub: String(payload.sub),
      email: String(payload.email),
      name: String(payload.name),
    };
  } catch {
    return null;
  }
}

export function sessionCookieOptions() {
  return {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax" as const,
    path: "/",
    maxAge: MAX_AGE,
  };
}

export async function getSession(): Promise<SessionPayload | null> {
  const token = (await cookies()).get(SESSION_COOKIE)?.value;
  return token ? verifySessionToken(token) : null;
}

export async function clearSessionCookie(): Promise<void> {
  (await cookies()).set(SESSION_COOKIE, "", { ...sessionCookieOptions(), maxAge: 0 });
}

export { SESSION_COOKIE };
