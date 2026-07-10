# 1999 Bot Hosting

A bot hosting platform: users sign up, log in, and manage hosted bots from a dashboard; admins have a separate login and dashboard. Glassmorphism/liquid-glass visual style with an animated intro splash and a 3D language picker.

## Run & Operate

- Workflows are already configured and running: `artifacts/bot-hosting: web` (frontend), `artifacts/api-server: API Server` (backend), `artifacts/mockup-sandbox: Component Preview Server` (canvas previews).
- `pnpm --filter @workspace/api-server run dev` — run the API server
- `pnpm --filter @workspace/bot-hosting run dev` — run the frontend
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- Required env: `DATABASE_URL` — Postgres connection string (already provisioned via Replit's built-in Postgres database)

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: Express 5
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)

## Where things live

_Populate as you build — short repo map plus pointers to the source-of-truth file for DB schema, API contracts, theme files, etc._

## Architecture decisions

_Populate as you build — non-obvious choices a reader couldn't infer from the code (3-5 bullets)._

## Product

_Describe the high-level user-facing capabilities of this app once they exist._

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

- The dev/start commands above are wired into the pre-configured Replit workflows (which supply `PORT`/`BASE_PATH` automatically). Running them directly in a shell requires setting those env vars yourself.
- `pnpm run typecheck` currently fails in `artifacts/bot-hosting` (5 pre-existing `TS2339` errors on `.error` in Login/Signup/Dashboard/AdminLogin/AdminDashboard, from the imported Orval-generated API error type). Pre-existing from import, not introduced by setup.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
