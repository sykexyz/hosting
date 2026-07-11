---
name: Railway deployment fix & bot execution
description: Migration from JSON store to PostgreSQL, CORS resolution, and real bot execution implementation
---

## PostgreSQL migration
- Migrated from ephemeral `store.json` to PostgreSQL via Drizzle ORM
- `lib/db` has Drizzle schema for users, bots, logs, sessions tables
- `artifacts/api-server/src/lib/migrate.ts` runs `CREATE TABLE IF NOT EXISTS` on every boot
- `pg` is marked external in esbuild (native bindings)
- User sessions are DB-backed; admin sessions still in-memory Set

## Railway env vars required
| Var | Service | Notes |
|---|---|---|
| `DATABASE_URL` | api-server | PostgreSQL connection string (use Neon.tech — Railway internal linking was broken) |
| `NODE_ENV` | api-server | Set to `production` |

`FRONTEND_URL` and `VITE_API_URL` are NO LONGER NEEDED — see architecture below.

## Architecture: single-service deployment
- api-server builds AND serves the bot-hosting frontend (via `build.mjs` calling `vite build` then copying to `dist/public`)
- Express serves `dist/public` as static files + SPA fallback for non-`/api` routes
- **No CORS issues** — everything on same origin
- User accesses site at the api-server Railway URL, NOT the bot-hosting URL
- Bot-hosting Railway service is obsolete/unused

**Why:** Two separate Railway services with cross-origin cookies and CORS was persistently broken. Single-service approach eliminates CORS entirely.

## Cookie settings
- `SameSite`/`Secure` driven by `FRONTEND_URL` env var presence (not `NODE_ENV`) — but since single-service now, cookies are same-origin and `SameSite=Lax` is correct

## Real bot execution (implemented 2026-07-11)
- `artifacts/api-server/src/lib/dep-detector.ts` — parses real `import`/`from`/`require` statements, filters stdlib
- `artifacts/api-server/src/lib/bot-runner.ts` — spawns actual child processes, manages them in-memory Map
- Per-bot isolated environments in `bot-envs/{id}/` — Python venv or node_modules
- Upload endpoint returns `detectedPackages[]` — frontend animates REAL packages, not fake hardcoded ones
- Start: installs deps with pip/npm then spawns process; Stop: SIGTERM → SIGKILL after 3s
- Supported: Python (venv), JavaScript (node + NODE_PATH), TypeScript (tsx), Java (javac+java)
- `nixpacks.toml` at repo root adds Python3 + pip + virtualenv to Railway build

## How to apply
- Railway needs one redeploy of the api-server after each push (auto-deploy if GitHub integration enabled)
- Neon.tech free PostgreSQL recommended over Railway internal PostgreSQL (simpler setup)
