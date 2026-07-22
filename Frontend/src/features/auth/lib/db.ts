import { Pool } from "pg";
import { drizzle } from "drizzle-orm/node-postgres";
import * as schema from "../db/schema";
import { getDatabaseUrl } from "./env";

const globalForDb = globalThis as unknown as { __pgPool?: Pool };
const pool = globalForDb.__pgPool ?? new Pool({ connectionString: getDatabaseUrl() });
if (process.env.NODE_ENV !== "production") globalForDb.__pgPool = pool;

export const db = drizzle(pool, { schema });
