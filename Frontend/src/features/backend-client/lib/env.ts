function required(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`Missing env var: ${name}`);
  return value;
}

export const getBackendUrl = () => process.env.BACKEND_URL ?? "http://localhost:8000";
export const getServiceJwtSecret = () => required("SERVICE_JWT_SECRET");
