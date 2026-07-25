# Design: Dedicated top-level `Database/` folder

Date: 2026-07-24
Status: Approved (pending spec review)

## Goal

Give the database a dedicated `Project/Database/` home. Remove the migration
frameworks (Alembic in the Backend, Drizzle in the Frontend) and Drizzle's ORM
from the application projects. Make plain SQL under `Database/` the single
source of truth for the `dailoqa` schema, drop and recreate the `dailoqa`
PostgreSQL database from that SQL, and keep both apps running against it.

## Current state (before)

One PostgreSQL database `dailoqa`, reached by both apps at
`localhost:5432/dailoqa` via `DATABASE_URL`. Three schemas:

| Schema      | Owner    | Tooling                                   | Tables |
|-------------|----------|-------------------------------------------|--------|
| `public`    | Frontend | Drizzle (`drizzle-orm` + `drizzle-kit`) over `pg` | `users`, `oauth_accounts` |
| `app`       | Backend  | Alembic + SQLAlchemy over `psycopg`       | `conversations`, `messages`, `tickets`, `ticket_reporters`, `jobs`, `notifications` |
| `langgraph` | Backend  | LangGraph `AsyncPostgresSaver` (runtime self-setup) | checkpoints/writes |

Migrations are applied by `alembic upgrade head` (Backend `entrypoint.sh`) and
`drizzle-kit` npm scripts (Frontend).

## Decisions

- **Removal scope:** Remove the migration frameworks (Alembic, drizzle-kit) AND
  the Drizzle ORM (`drizzle-orm`). Keep the runtime drivers/ORM the apps need to
  function: SQLAlchemy + psycopg (Backend, unchanged) and `pg` (Frontend).
- **Schema source of truth:** hand-written SQL under `Database/schema/`,
  reproducing today's tables exactly.
- **Provisioning:** a PowerShell orchestrator (`setup.ps1`) drives `psql`.
- **Runtime connection is unchanged:** same `DATABASE_URL`, same host/db name.
  "New database location" means the schema definition and provisioning move to
  `Database/`, not a new DSN.
- **Verification:** frontend `tsc --noEmit` + `eslint`, backend `pytest` in the
  WSL venv `~/.venvs/dailoqa-backend`, `psql` table check, plus a live boot
  smoke test of both apps.

## Target `Database/` structure

```
Project/Database/
├── README.md                 # schema map, how to reset/provision, ownership notes
├── schema/
│   ├── 00_schemas.sql        # CREATE SCHEMA public/app/langgraph; CREATE EXTENSION pgcrypto
│   ├── 01_public.sql         # users, oauth_accounts            (was Frontend/Drizzle)
│   └── 02_app.sql            # conversations, messages, tickets, ticket_reporters, jobs, notifications (was Backend/Alembic)
└── scripts/
    ├── reset.sql             # terminate conns + DROP DATABASE IF EXISTS dailoqa + CREATE DATABASE dailoqa (run on `postgres`)
    ├── provision.sql         # \i schema/00,01,02 in order (run on `dailoqa`)
    └── setup.ps1             # orchestrator: psql reset.sql (postgres) -> psql provision.sql (dailoqa) -> verify
```

`langgraph` schema is created in `00_schemas.sql` for completeness, but its
checkpoint tables stay owned/created by the backend's
`AsyncPostgresSaver.setup()` at runtime — unchanged behavior.

### DDL parity (must match current schema exactly)

`01_public.sql` — `public.users`, `public.oauth_accounts` with
`gen_random_uuid()` PK defaults, `provider_account_unique` UNIQUE(provider,
provider_account_id), FK `oauth_accounts.user_id -> users.id ON DELETE CASCADE`,
timestamptz `created_at`/`updated_at` defaulting to `now()`.

`02_app.sql` — the six `app.*` tables reproducing
`Backend/src/app/migrations/versions/0001_initial.py`: string PKs (UUIDs
supplied by the app), `messages.metadata` JSONB column (ORM attribute `meta`),
`jsonb` `payload`, unique constraints `uq_message_job`, `uq_ticket_jira_key`,
`uq_ticket_reporter`, `uq_notification_job`, FKs with `ON DELETE CASCADE`,
indexes on `conversations.user_sub`, `messages.conversation_id`, `jobs.status`,
`notifications.user_sub`.

## Changes by project

### Backend — remove Alembic, keep runtime data access

Delete:
- `Backend/alembic.ini`
- `Backend/src/app/migrations/` (env.py, script.py.mako, versions/0001_initial.py)

Edit:
- `Backend/pyproject.toml`: drop `alembic>=1.14` from `dependencies`.
- `Backend/entrypoint.sh`: remove the `alembic upgrade head` line; the container
  now just `exec uvicorn ...`. Schema provisioning becomes the deliberate,
  separate `Database/` step.

Keep untouched: `db/base.py`, `db/models.py`, `db/repositories.py`,
`db/notifications.py`, `agent/checkpointer.py`, and all SQLAlchemy/psycopg use.

### Frontend — remove Drizzle entirely, rewrite auth query layer to raw `pg`

Delete:
- `Frontend/drizzle.config.ts`
- `Frontend/src/features/auth/db/` (schema.ts + migrations/)

Edit:
- `Frontend/package.json`: remove deps `drizzle-orm`, `drizzle-kit`, `dotenv`;
  remove scripts `db:generate`, `db:migrate`, `db:push`. Keep `pg` + `@types/pg`.
  Run `npm install` to update the lockfile.
- `Frontend/src/features/auth/lib/db.ts`: export a singleton `pg` `Pool` and a
  small typed `query<T>()` helper; drop Drizzle.
- `Frontend/src/features/auth/lib/users.ts`: reimplement `upsertUserFromGoogle`
  (select existing oauth account -> update user/token, else insert user +
  account) as parameterized SQL. Define local `User` / `OAuthAccount` TS types.

Untouched: `session.ts`, `oauth.ts`, `crypto.ts`, `callback.ts`, `signOut.ts`,
`googleCredentials.ts`, `api/actions.ts` — none import Drizzle.

## Destructive reset (gated)

`setup.ps1` will, via the active `psql`:
1. On maintenance DB `postgres`: terminate connections to `dailoqa`,
   `DROP DATABASE IF EXISTS dailoqa`, `CREATE DATABASE dailoqa`.
2. On `dailoqa`: run `provision.sql` (00 -> 01 -> 02).

This permanently destroys all data currently in `dailoqa`. The file refactor
(above) is done first and is non-destructive. The drop/recreate runs ONLY after
an explicit go-ahead from the user, who is shown the exact commands first.

## Verification

1. `psql` check: `public.users`, `public.oauth_accounts`, and all six `app.*`
   tables exist with expected columns.
2. Backend: `pytest` in `~/.venvs/dailoqa-backend`; confirm no `alembic` import
   errors and `app.main` imports cleanly.
3. Frontend: `npx tsc --noEmit` and `npx eslint` pass after the raw-`pg` rewrite.
4. Live smoke test: boot backend (uvicorn) + frontend (next dev); exercise
   Google login (writes `public.users`/`oauth_accounts`) and a chat/ticket flow
   (writes `app.*` + langgraph checkpoints).

## Out of scope

- No change to `DATABASE_URL`, credentials, or Docker networking.
- No change to backend ORM models or query logic beyond deleting Alembic.
- No new tables, columns, or behavior — parity refactor only.
