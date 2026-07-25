import { Pool } from "pg";
import { getDatabaseUrl } from "./env";

const globalForDb = globalThis as unknown as { __pgPool?: Pool };
export const pool = globalForDb.__pgPool ?? new Pool({ connectionString: getDatabaseUrl() });
if (process.env.NODE_ENV !== "production") globalForDb.__pgPool = pool;

export async function query<T>(text: string, params: unknown[] = []): Promise<T[]> {
  const result = await pool.query(text, params as never[]);
  return result.rows as T[];
}
