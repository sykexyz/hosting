# 1999 Bot Hosting

A bot hosting platform: users sign up, log in, and manage hosted bots from a dashboard; admins have a separate login and dashboard. Glassmorphism/liquid-glass visual style with an animated intro splash and a 3D language picker.

## Run & Operate

- Workflows configured and running: `artifacts/bot-hosting: web` (frontend on port 24722), `artifacts/api-server: API Server` (backend on port 8080)
- `pnpm --filter @workspace/api-server run dev` — run the API server (needs PORT=8080)
- `pnpm --filter @workspace/bot-hosting run dev` — run the frontend (needs PORT=24722)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- No database required — data stored in `artifacts/api-server/data/store.json` (resets on container rebuild)

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: Express 5
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)

## Where things live

- `artifacts/api-server/src/lib/store.ts` — JSON file data store (source of truth for all persistence)
- `artifacts/api-server/src/routes/` — Express route handlers (auth, bots, admin)
- `artifacts/api-server/data/store.json` — live data file (auto-created; resets on container rebuild)
- `artifacts/bot-hosting/src/index.css` — all theme variables and utility classes
- `artifacts/bot-hosting/src/pages/Dashboard.tsx` — main user dashboard with upload animation
- `lib/api-zod/` — Zod schemas for API validation
- `lib/api-client-react/` — Orval-generated React Query hooks

## Architecture decisions

- **JSON file storage instead of PostgreSQL**: user requested no database dependency. Data stored in `artifacts/api-server/data/store.json` with atomic writes (temp + rename). Resets on container rebuild — that's intentional.
- **Always-dark theme**: site is permanently in dark/black-galaxy mode. The `dark` class is force-applied in `main.tsx`; ThemeToggle is hidden via CSS.
- **Upload terminal animation**: file upload shows a fake module-download animation (per language) while the real upload runs in parallel. Success/error shown when both the animation and upload resolve.

## Product

Bot hosting platform: users sign up (Gmail only), log in, deploy bots by uploading source files, and start/stop them from the dashboard. Admins (credentials: risu / cozy24123) have a separate login with a global view of all users, bots, and activity logs.

## User preferences

- Black and white neon theme, black galaxy background with stars
- No database required — JSON file storage is fine (data can reset)
- File upload must show module-download loading animation, then "Successfully hosted: filename"
- Site always dark, no theme toggle

## Gotchas

- The dev/start commands above are wired into Replit workflows (which supply `PORT`/`BASE_PATH`). Running directly in a shell requires setting those env vars yourself.
- JSON store is process-local and file-based. Concurrent multi-process deployments would need proper locking or a database upgrade.
- `pnpm run typecheck` has 5 pre-existing `TS2339` errors in `artifacts/bot-hosting` on `.error` in Orval-generated API hooks — not introduced by these changes.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
