import { config } from "dotenv";
import { defineConfig } from "drizzle-kit";

config({ path: ".env.local" });

export default defineConfig({
  dialect: "postgresql",
  schema: "./src/features/auth/db/schema.ts",
  out: "./src/features/auth/db/migrations",
  dbCredentials: { url: process.env.DATABASE_URL! },
});
