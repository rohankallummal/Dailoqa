import { and, eq } from "drizzle-orm";
import { db } from "./db";
import { oauthAccounts, users } from "../db/schema";
import { encryptSecret } from "./crypto";
import type { GoogleIdentity } from "./oauth";

export async function upsertUserFromGoogle(
  identity: GoogleIdentity,
  refreshToken?: string,
): Promise<{ userId: string }> {
  const existing = await db
    .select()
    .from(oauthAccounts)
    .where(
      and(
        eq(oauthAccounts.provider, "google"),
        eq(oauthAccounts.providerAccountId, identity.sub),
      ),
    )
    .limit(1);

  if (existing.length > 0) {
    const account = existing[0];
    await db
      .update(users)
      .set({ email: identity.email, name: identity.name, updatedAt: new Date() })
      .where(eq(users.id, account.userId));
    if (refreshToken) {
      await db
        .update(oauthAccounts)
        .set({ refreshTokenEncrypted: encryptSecret(refreshToken), updatedAt: new Date() })
        .where(eq(oauthAccounts.id, account.id));
    }
    return { userId: account.userId };
  }

  const [user] = await db
    .insert(users)
    .values({ email: identity.email, name: identity.name })
    .returning();
  await db.insert(oauthAccounts).values({
    userId: user.id,
    provider: "google",
    providerAccountId: identity.sub,
    refreshTokenEncrypted: refreshToken ? encryptSecret(refreshToken) : null,
  });
  return { userId: user.id };
}
