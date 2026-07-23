import { SignJWT } from "jose";
import { getServiceJwtSecret } from "./env";

const secret = () => new TextEncoder().encode(getServiceJwtSecret());

export async function mintServiceToken(sub: string, userId: string): Promise<string> {
  return new SignJWT({ userId })
    .setProtectedHeader({ alg: "HS256" })
    .setSubject(sub)
    .setAudience("backend")
    .setIssuedAt()
    .setExpirationTime("120s")
    .sign(secret());
}
