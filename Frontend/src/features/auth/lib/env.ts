function required(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`Missing env var: ${name}`);
  return value;
}

export const getDatabaseUrl = () => required("DATABASE_URL");
export const getSessionSecret = () => required("SESSION_SECRET");
export const getEncryptionKey = () => required("ENCRYPTION_KEY");
export const getGoogleClientId = () => required("GOOGLE_CLIENT_ID");
export const getGoogleClientSecret = () => required("GOOGLE_CLIENT_SECRET");
export const getAppUrl = () => process.env.APP_URL ?? "http://localhost:3000";
