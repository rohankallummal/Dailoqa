# Dedicated Database/ Folder Refactor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the database a dedicated `Project/Database/` home whose plain SQL is the single source of truth for the `dailoqa` schema; remove Alembic + Drizzle from the apps; drop and recreate `dailoqa` from that SQL; keep both apps running.

**Architecture:** `Project/Database/` holds `schema/*.sql` (parity DDL for the `public`, `app`, and `langgraph` schemas) and `scripts/` (a gated PowerShell orchestrator over `psql` that resets and provisions). The Backend keeps SQLAlchemy/psycopg for runtime queries but loses Alembic. The Frontend keeps `pg` but loses all of Drizzle; its tiny auth query layer is rewritten to parameterized SQL. The runtime `DATABASE_URL` is unchanged.

**Tech Stack:** PostgreSQL 15+, `psql`, PowerShell 5.1; Backend Python 3.12 (FastAPI, SQLAlchemy async, psycopg); Frontend Next.js 16 / TypeScript (node-postgres `pg`).

## Global Constraints

- **No git commits.** Project policy (`Frontend/CLAUDE.md`) forbids committing unless the user explicitly asks. Every task closes with a verification step, not a commit. A single optional commit may be offered at the very end on request.
- **Parity only.** No new tables, columns, constraints, indexes, or behavior. DDL must reproduce the current schema exactly.
- **Runtime connection unchanged.** Do not alter `DATABASE_URL`, credentials, host, port, or db name. Backend URL scheme stays `postgresql+psycopg://`; Frontend stays `postgres://`.
- **Backend naming:** snake_case modules/functions, PascalCase classes, docstrings required on public modules/classes/functions, no inline comments.
- **Frontend naming:** kebab-case folders, camelCase files/vars, PascalCase types, feature code imports only via a feature's `index.ts`, no comments except required framework directives.
- **The destructive DB reset (Task 5) runs ONLY after an explicit user go-ahead**, with the exact commands shown first. Tasks 1–4 are non-destructive and touch no live data.
- **Backend has no automated test suite.** Backend verification is an import smoke check in the WSL venv `~/.venvs/dailoqa-backend` (Windows `R:` = WSL `/mnt/r`) plus the live boot in Task 6.

---

### Task 1: Author `Database/schema/` parity DDL

**Files:**
- Create: `Project/Database/schema/00_schemas.sql`
- Create: `Project/Database/schema/01_public.sql`
- Create: `Project/Database/schema/02_app.sql`

**Interfaces:**
- Consumes: nothing.
- Produces: three SQL files applied in numeric order by Task 2's `provision.sql`. `01_public.sql` reproduces `public.users` + `public.oauth_accounts` (source: `Frontend/src/features/auth/db/migrations/0000_zippy_william_stryker.sql`). `02_app.sql` reproduces the six `app.*` tables (source: `Backend/src/app/migrations/versions/0001_initial.py`).

- [ ] **Step 1: Create `00_schemas.sql`**

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS app;
CREATE SCHEMA IF NOT EXISTS langgraph;
```

(The `public` schema exists by default in a fresh database. `langgraph`'s checkpoint tables are created at runtime by the backend's `AsyncPostgresSaver.setup()`; only its schema is pre-created here.)

- [ ] **Step 2: Create `01_public.sql`** (exact parity with the Drizzle migration)

```sql
CREATE TABLE public.users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
    email text NOT NULL,
    name text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE public.oauth_accounts (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    provider text NOT NULL,
    provider_account_id text NOT NULL,
    refresh_token_encrypted text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT provider_account_unique UNIQUE (provider, provider_account_id),
    CONSTRAINT oauth_accounts_user_id_users_id_fk
        FOREIGN KEY (user_id) REFERENCES public.users (id) ON DELETE CASCADE
);
```

- [ ] **Step 3: Create `02_app.sql`** (exact parity with `0001_initial.py`)

```sql
CREATE TABLE app.conversations (
    id varchar PRIMARY KEY,
    user_sub varchar NOT NULL,
    surface varchar NOT NULL,
    title varchar,
    status varchar NOT NULL DEFAULT 'active',
    deleted_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);
CREATE INDEX ix_conversations_user_sub ON app.conversations (user_sub);

CREATE TABLE app.messages (
    id varchar PRIMARY KEY,
    conversation_id varchar NOT NULL,
    role varchar NOT NULL,
    content text NOT NULL,
    metadata jsonb,
    job_id varchar,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT uq_message_job UNIQUE (job_id),
    CONSTRAINT fk_messages_conversation_id_conversations
        FOREIGN KEY (conversation_id) REFERENCES app.conversations (id) ON DELETE CASCADE
);
CREATE INDEX ix_messages_conversation_id ON app.messages (conversation_id);

CREATE TABLE app.tickets (
    id varchar PRIMARY KEY,
    jira_key varchar NOT NULL,
    type varchar NOT NULL,
    title varchar NOT NULL,
    summary text,
    status varchar,
    conversation_id varchar,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT uq_ticket_jira_key UNIQUE (jira_key)
);

CREATE TABLE app.ticket_reporters (
    id varchar PRIMARY KEY,
    ticket_id varchar NOT NULL,
    user_sub varchar NOT NULL,
    added_at timestamp with time zone DEFAULT now(),
    CONSTRAINT uq_ticket_reporter UNIQUE (ticket_id, user_sub),
    CONSTRAINT fk_ticket_reporters_ticket_id_tickets
        FOREIGN KEY (ticket_id) REFERENCES app.tickets (id) ON DELETE CASCADE
);

CREATE TABLE app.jobs (
    id varchar PRIMARY KEY,
    type varchar NOT NULL DEFAULT 'create_ticket',
    status varchar NOT NULL DEFAULT 'queued',
    conversation_id varchar NOT NULL,
    user_sub varchar NOT NULL,
    payload jsonb NOT NULL,
    jira_key varchar,
    action varchar,
    attempts integer NOT NULL DEFAULT 0,
    last_error text,
    locked_at timestamp with time zone,
    locked_by varchar,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);
CREATE INDEX ix_jobs_status ON app.jobs (status);

CREATE TABLE app.notifications (
    id varchar PRIMARY KEY,
    user_sub varchar NOT NULL,
    conversation_id varchar,
    type varchar NOT NULL,
    title varchar NOT NULL,
    body text NOT NULL,
    jira_key varchar,
    job_id varchar,
    read_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT uq_notification_job UNIQUE (job_id)
);
CREATE INDEX ix_notifications_user_sub ON app.notifications (user_sub);
```

- [ ] **Step 4: Parity self-check (no DB op)**

Compare each column/type/constraint against the two source files. Confirm: `messages.metadata` is `jsonb` (ORM attribute `meta` maps to column `metadata`); `jobs.payload` is `jsonb NOT NULL`; string PKs are `varchar` (app supplies UUID strings); `public.*` PKs are `uuid DEFAULT gen_random_uuid()`. Expected: every table/column in the sources is present with matching type and nullability.

---

### Task 2: Author `Database/scripts/` + `README.md`

**Files:**
- Create: `Project/Database/scripts/reset.sql`
- Create: `Project/Database/scripts/provision.sql`
- Create: `Project/Database/scripts/setup.ps1`
- Create: `Project/Database/README.md`

**Interfaces:**
- Consumes: `../schema/00_schemas.sql`, `01_public.sql`, `02_app.sql` from Task 1.
- Produces: `setup.ps1`, the single entry point that resets + provisions `dailoqa`. Reads DB credentials from `Backend/.env`'s `DATABASE_URL` (no secret is hardcoded).

- [ ] **Step 1: Create `reset.sql`** (run against maintenance db `postgres`)

```sql
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'dailoqa' AND pid <> pg_backend_pid();

DROP DATABASE IF EXISTS dailoqa;
CREATE DATABASE dailoqa;
```

- [ ] **Step 2: Create `provision.sql`** (run against `dailoqa`; `\ir` includes relative to this file)

```sql
\ir ../schema/00_schemas.sql
\ir ../schema/01_public.sql
\ir ../schema/02_app.sql
```

- [ ] **Step 3: Create `setup.ps1`**

```powershell
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$envFile = Join-Path $scriptDir "..\..\Backend\.env"

$dbUrl = (Get-Content $envFile | Where-Object { $_ -match "^DATABASE_URL=" }) -replace "^DATABASE_URL=", ""
if (-not $dbUrl) { throw "DATABASE_URL not found in $envFile" }

if ($dbUrl -notmatch "://([^:]+):([^@]+)@([^:/]+):(\d+)/(\w+)") {
    throw "Could not parse DATABASE_URL: $dbUrl"
}
$pgUser = $Matches[1]
$pgPass = [System.Uri]::UnescapeDataString($Matches[2])
$pgHost = $Matches[3]
$pgPort = $Matches[4]

$env:PGPASSWORD = $pgPass

Write-Host "Resetting database 'dailoqa' on $pgHost`:$pgPort ..." -ForegroundColor Yellow
psql -h $pgHost -p $pgPort -U $pgUser -d postgres -v ON_ERROR_STOP=1 -f (Join-Path $scriptDir "reset.sql")
if ($LASTEXITCODE -ne 0) { throw "reset.sql failed" }

Write-Host "Provisioning schema into 'dailoqa' ..." -ForegroundColor Yellow
psql -h $pgHost -p $pgPort -U $pgUser -d dailoqa -v ON_ERROR_STOP=1 -f (Join-Path $scriptDir "provision.sql")
if ($LASTEXITCODE -ne 0) { throw "provision.sql failed" }

Write-Host "Verifying tables ..." -ForegroundColor Yellow
psql -h $pgHost -p $pgPort -U $pgUser -d dailoqa -c "\dt public.*" -c "\dt app.*"

Write-Host "Done." -ForegroundColor Green
```

- [ ] **Step 4: Create `README.md`**

````markdown
# Database

Single source of truth for the `dailoqa` PostgreSQL database. Both the Backend
and Frontend connect to it at `localhost:5432/dailoqa` via `DATABASE_URL`; this
folder owns the schema definition and provisioning — the apps no longer carry
migration tooling.

## Schemas

| Schema      | Owner    | Defined in                | Tables |
|-------------|----------|---------------------------|--------|
| `public`    | Frontend | `schema/01_public.sql`    | `users`, `oauth_accounts` |
| `app`       | Backend  | `schema/02_app.sql`       | `conversations`, `messages`, `tickets`, `ticket_reporters`, `jobs`, `notifications` |
| `langgraph` | Backend  | schema in `schema/00_schemas.sql`; tables created at runtime by `AsyncPostgresSaver.setup()` | checkpoints/writes |

## Provision / reset (destructive)

Drops and recreates `dailoqa`, then applies all schema files in order.
Credentials are read from `Backend/.env`.

```powershell
./scripts/setup.ps1
```

`WARNING:` this deletes all data in `dailoqa`.
````

- [ ] **Step 5: Static review (no DB op)**

Confirm `setup.ps1`'s regex parses `postgresql+psycopg://postgres:%23pes1ug22am134@localhost:5432/dailoqa` into user=`postgres`, pass=`#pes1ug22am134` (after `UnescapeDataString`), host=`localhost`, port=`5432`. Confirm `provision.sql`'s `\ir` paths resolve from `scripts/` to `schema/`. Expected: paths and parse are correct.

---

### Task 3: Backend — remove Alembic

**Files:**
- Delete: `Project/Backend/alembic.ini`
- Delete: `Project/Backend/src/app/migrations/` (env.py, script.py.mako, versions/0001_initial.py)
- Modify: `Project/Backend/pyproject.toml` (remove `alembic>=1.14`)
- Modify: `Project/Backend/entrypoint.sh` (remove `alembic upgrade head`)

**Interfaces:**
- Consumes: nothing.
- Produces: a backend with no Alembic dependency or migration folder; SQLAlchemy models/repositories untouched.

- [ ] **Step 1: Delete Alembic files**

```bash
rm -f "R:/Dailoqa/Project/Backend/alembic.ini"
rm -rf "R:/Dailoqa/Project/Backend/src/app/migrations"
```

- [ ] **Step 2: Remove the `alembic` dependency from `pyproject.toml`**

Delete this line from the `dependencies` array:

```toml
    "alembic>=1.14",
```

- [ ] **Step 3: Rewrite `entrypoint.sh`** (schema provisioning is now the `Database/` step)

```bash
#!/usr/bin/env bash
set -euo pipefail

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- [ ] **Step 4: Verify no dangling Alembic references**

Run (PowerShell, from `Project/Backend`):
```
Select-String -Path (Get-ChildItem -Recurse -Include *.py,*.sh,*.ini,*.toml,*.yml -File) -Pattern "alembic" 2>$null
```
Expected: no matches.

- [ ] **Step 5: Backend import smoke check (WSL venv)**

Run:
```bash
wsl bash -lc "cd /mnt/r/Dailoqa/Project/Backend && ~/.venvs/dailoqa-backend/bin/python -c 'import app.main; import app.worker.processor; import app.agent.graph; print(\"backend imports OK\")'"
```
Expected: prints `backend imports OK` with no `ModuleNotFoundError: alembic` and no other import error.

---

### Task 4: Frontend — remove Drizzle, rewrite auth query layer to raw `pg`

**Files:**
- Delete: `Project/Frontend/drizzle.config.ts`
- Delete: `Project/Frontend/src/features/auth/db/` (schema.ts + migrations/)
- Modify: `Project/Frontend/package.json` (remove drizzle deps/scripts + dotenv)
- Modify: `Project/Frontend/src/features/auth/lib/db.ts` (raw `pg`)
- Modify: `Project/Frontend/src/features/auth/lib/users.ts` (parameterized SQL)

**Interfaces:**
- Consumes: `getDatabaseUrl()` from `./env`; `encryptSecret` from `./crypto`; `GoogleIdentity` (`{ sub: string; email: string; name: string }`) from `./oauth`.
- Produces: `db.ts` exports `pool: Pool` and `query<T>(text, params): Promise<T[]>`. `users.ts` keeps its public signature `upsertUserFromGoogle(identity, refreshToken?): Promise<{ userId: string }>` — no other file changes.

- [ ] **Step 1: Delete Drizzle config and the `db/` folder**

```bash
rm -f "R:/Dailoqa/Project/Frontend/drizzle.config.ts"
rm -rf "R:/Dailoqa/Project/Frontend/src/features/auth/db"
```

- [ ] **Step 2: Edit `package.json`** — remove the three `db:*` scripts and the `drizzle-orm`, `drizzle-kit`, `dotenv` dependencies. Keep `pg` and `@types/pg`. Resulting `scripts` and dependency-relevant sections:

```json
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint"
  },
```

Remove from `dependencies`: `"drizzle-orm": "^0.45.2",`. Remove from `devDependencies`: `"drizzle-kit": "^0.31.10",` and `"dotenv": "^17.4.2",`.

- [ ] **Step 3: Rewrite `src/features/auth/lib/db.ts`**

```ts
import { Pool } from "pg";
import { getDatabaseUrl } from "./env";

const globalForDb = globalThis as unknown as { __pgPool?: Pool };
export const pool = globalForDb.__pgPool ?? new Pool({ connectionString: getDatabaseUrl() });
if (process.env.NODE_ENV !== "production") globalForDb.__pgPool = pool;

export async function query<T>(text: string, params: unknown[] = []): Promise<T[]> {
  const result = await pool.query(text, params as never[]);
  return result.rows as T[];
}
```

- [ ] **Step 4: Rewrite `src/features/auth/lib/users.ts`**

```ts
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
```

- [ ] **Step 5: Refresh the lockfile**

Run (PowerShell, from `Project/Frontend`):
```
npm install
```
Expected: `package-lock.json` updates; `drizzle-orm`, `drizzle-kit`, `dotenv` no longer present.

- [ ] **Step 6: Verify no dangling Drizzle references + typecheck + lint**

Run (PowerShell, from `Project/Frontend`):
```
Select-String -Path (Get-ChildItem -Recurse -Include *.ts,*.tsx -File -Path src) -Pattern "drizzle" 2>$null
npx tsc --noEmit
npx eslint src
```
Expected: no `drizzle` matches in `src`; `tsc` exits 0; `eslint` reports no errors.

---

### Task 5: Destructive reset + provision (GATED — requires explicit user go-ahead)

**Files:** none changed. Runs `Database/scripts/setup.ps1`.

**Interfaces:**
- Consumes: Task 1 schema files, Task 2 scripts, `Backend/.env`.
- Produces: a freshly recreated `dailoqa` database containing `public.*` and `app.*` tables (langgraph tables appear at first backend run).

- [ ] **Step 1: Show the user exactly what will run and get an explicit "go"**

Display `reset.sql` (drops + recreates `dailoqa`) and state that all current data will be permanently lost. Do NOT proceed to Step 2 without an affirmative response.

- [ ] **Step 2: Run the orchestrator**

Run (PowerShell, from `Project/Database`):
```
./scripts/setup.ps1
```
Expected: "Resetting…", "Provisioning…", then a `\dt` listing showing `public.users`, `public.oauth_accounts` and the six `app.*` tables, then "Done.".

- [ ] **Step 3: Verify the schema independently**

Run (PowerShell):
```
$env:PGPASSWORD="#pes1ug22am134"; psql -h localhost -U postgres -d dailoqa -c "\dn" -c "\dt public.*" -c "\dt app.*"
```
Expected: schemas `app`, `langgraph`, `public` present; two `public` tables and six `app` tables listed.

---

### Task 6: Full integration verification (live boot smoke test)

**Files:** none changed.

**Interfaces:**
- Consumes: the provisioned DB (Task 5) and refactored apps (Tasks 3–4).
- Produces: evidence the app runs end-to-end against the new schema.

- [ ] **Step 1: Backend boots and connects**

Start the API in the WSL venv:
```bash
wsl bash -lc "cd /mnt/r/Dailoqa/Project/Backend && ~/.venvs/dailoqa-backend/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000"
```
Expected: uvicorn reports "Application startup complete" with no traceback. Then `GET http://localhost:8000/` (or the app's health route) returns without a DB error.

- [ ] **Step 2: Frontend builds and boots**

Run (PowerShell, from `Project/Frontend`):
```
npm run dev
```
Expected: Next.js "Ready" with no compile errors.

- [ ] **Step 3: End-to-end smoke**

With both running: complete Google login (writes `public.users` + `public.oauth_accounts`) and send one chat message that triggers a ticket/notification flow (writes `app.*` and creates `langgraph` checkpoint tables). Then confirm rows landed:
```
$env:PGPASSWORD="#pes1ug22am134"; psql -h localhost -U postgres -d dailoqa -c "SELECT count(*) FROM public.users;" -c "SELECT count(*) FROM app.conversations;" -c "\dt langgraph.*"
```
Expected: `users` count ≥ 1 after login; `conversations` count ≥ 1 after chat; langgraph checkpoint tables now exist.

- [ ] **Step 4: Report results**

Summarize what passed and any deviations. Offer an optional single git commit of the refactor only if the user asks.

---

## Self-Review

**Spec coverage:**
- Remove Drizzle/Alembic + config/folders/artifacts → Tasks 3 (backend Alembic) & 4 (frontend Drizzle incl. `drizzle-orm`, `drizzle-kit`, `dotenv`, config, `db/` folder, scripts). ✔
- Delete existing PostgreSQL DB completely → Task 5 `reset.sql` (drop). ✔
- Recreate `dailoqa` from scratch inside `Database/` + in PostgreSQL → Tasks 1–2 (SQL + scripts) applied in Task 5. ✔
- Update backend/frontend to use new location; fix imports/paths/config → Task 3 (entrypoint, pyproject) & Task 4 (db.ts/users.ts/package.json). ✔
- Verify app runs + DB ops work → Task 6 (live boot + row checks). ✔

**Placeholder scan:** No TBD/TODO; every code and command step contains concrete content. ✔

**Type consistency:** `query<T>` defined in Task 4 Step 3 is consumed in Step 4 with `OAuthAccountRow`/`{ id: string }`. `upsertUserFromGoogle` signature preserved. `GoogleIdentity` matches `./oauth`. ✔

**Known substitution:** "backend tests" from the spec's verification are replaced by an import smoke check (Task 3 Step 5) + live boot (Task 6) because no backend test suite exists. Flagged in Global Constraints.
