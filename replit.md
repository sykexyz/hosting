# 1999 Bot Hosting

A bot hosting platform: users sign up, log in, and manage hosted bots from a dashboard; admins have a separate login and dashboard. Glassmorphism/liquid-glass visual style with an animated intro splash and a 3D language picker.

## Run & Operate

- Workflows configured and running: `artifacts/bot-hosting: web` (frontend on port 24722), `artifacts/api-server: API Server` (backend on port 8080)
- `pnpm --filter @workspace/api-server run dev` — run the API server (needs PORT=8080)
- `pnpm --filter @workspace/bot-hosting run dev` — run the frontend (needs PORT=24722)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- Uses PostgreSQL (via `DATABASE_URL`, provisioned in this Repl) — schema is auto-created/verified on server startup (`ensureSchema()`)

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: Express 5
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)

## Where things live

- `artifacts/api-server/src/lib/store.ts` — Drizzle/PostgreSQL data access layer (source of truth for all persistence)
- `artifacts/api-server/src/lib/migrate.ts` — idempotent `ensureSchema()`, creates tables on startup if missing
- `artifacts/api-server/src/routes/` — Express route handlers (auth, bots, admin)
- `artifacts/bot-hosting/src/index.css` — all theme variables and utility classes
- `artifacts/bot-hosting/src/pages/Dashboard.tsx` — main user dashboard with upload animation
- `lib/api-zod/` — Zod schemas for API validation
- `lib/api-client-react/` — Orval-generated React Query hooks

## Architecture decisions

- **PostgreSQL via Drizzle**: previously used JSON file storage; migrated to PostgreSQL (originally for a Railway deployment) — `DATABASE_URL` is required and the server refuses to start without it. Schema is auto-created/verified on every startup via `ensureSchema()`.
- **Always-dark theme**: site is permanently in dark/black-galaxy mode. The `dark` class is force-applied in `main.tsx`; ThemeToggle is hidden via CSS.
- **Upload terminal animation**: file upload shows a fake module-download animation (per language) while the real upload runs in parallel. Success/error shown when both the animation and upload resolve.

## Product

Bot hosting platform: users sign up (Gmail only), log in, deploy bots by uploading source files, and start/stop them from the dashboard. Admins (credentials: risu / cozy24123) have a separate login with a global view of all users, bots, and activity logs.

## User preferences

- Black and white neon theme, black galaxy background with stars
- File upload must show module-download loading animation, then "Successfully hosted: filename"
- Site always dark, no theme toggle

## Gotchas

- The dev/start commands above are wired into Replit workflows (which supply `PORT`/`BASE_PATH`). Running directly in a shell requires setting those env vars yourself.
- Requires `DATABASE_URL` (PostgreSQL) — the API server exits immediately on startup if it's not set.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
