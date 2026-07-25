import { query } from "./db";
import { encryptSecret } from "./crypto";
import type { GoogleIdentity } from "./oauth";

type OAuthAccountRow = { id: string; user_id: string };

export async function upsertUserFromGoogle(
  identity: GoogleIdentity,
  refreshToken?: string,
): Promise<{ userId: string }> {
  const existing = await query<OAuthAccountRow>(
    `SELECT id, user_id FROM oauth_accounts
     WHERE provider = $1 AND provider_account_id = $2
     LIMIT 1`,
    ["google", identity.sub],
  );

  if (existing.length > 0) {
    const account = existing[0];
    await query(
      `UPDATE users SET email = $1, name = $2, updated_at = now() WHERE id = $3`,
      [identity.email, identity.name, account.user_id],
    );
    if (refreshToken) {
      await query(
        `UPDATE oauth_accounts SET refresh_token_encrypted = $1, updated_at = now() WHERE id = $2`,
        [encryptSecret(refreshToken), account.id],
      );
    }
    return { userId: account.user_id };
  }

  const inserted = await query<{ id: string }>(
    `INSERT INTO users (email, name) VALUES ($1, $2) RETURNING id`,
    [identity.email, identity.name],
  );
  const userId = inserted[0].id;
  await query(
    `INSERT INTO oauth_accounts (user_id, provider, provider_account_id, refresh_token_encrypted)
     VALUES ($1, $2, $3, $4)`,
    [userId, "google", identity.sub, refreshToken ? encryptSecret(refreshToken) : null],
  );
  return { userId };
}
