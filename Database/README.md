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

## Layout

```
Database/
  schema/
    00_schemas.sql   # extensions + app/langgraph schemas
    01_public.sql    # frontend auth tables
    02_app.sql       # backend domain tables
  scripts/
    reset.sql        # drop + recreate the dailoqa database
    provision.sql    # apply schema/*.sql in order
    setup.ps1        # orchestrator (reset -> provision -> verify)
```

## Provision / reset (destructive)

Drops and recreates `dailoqa`, then applies all schema files in order.
Credentials are read from `Backend/.env`'s `DATABASE_URL` — no secret is stored
here.

```powershell
./scripts/setup.ps1
```

`WARNING:` this permanently deletes all data in `dailoqa`.
