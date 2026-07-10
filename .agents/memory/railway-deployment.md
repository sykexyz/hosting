---
name: Railway deployment - PostgreSQL migration
description: Why the app was migrated from JSON store to PostgreSQL, and what env vars Railway needs.
---

# Railway Deployment Fix

## What changed
- Migrated from ephemeral `store.json` (JSON file) to PostgreSQL via Drizzle ORM (`@workspace/db`)
- Sessions migrated from in-memory Map to `sessions` DB table
- `artifacts/api-server/src/lib/migrate.ts` runs `CREATE TABLE IF NOT EXISTS` on every startup — ensures tables exist on fresh Railway DB

## Why
- Railway's filesystem is ephemeral: `store.json` wiped on every deploy → accounts lost → "invalid credentials"
- In-memory sessions reset on restart → users logged out on every deploy

## Railway env vars required
- `DATABASE_URL` — PostgreSQL connection string (add Railway PostgreSQL service)
- `FRONTEND_URL` — frontend Railway service URL (e.g. `https://xxx.railway.app`) for CORS
- `VITE_API_URL` — API Railway service URL (e.g. `https://api-xxx.railway.app`) for frontend → set in Railway frontend service
- `NODE_ENV=production` — Railway sets this automatically
- `SESSION_SECRET` — already in Replit secrets
- `ADMIN_EMAIL` / `ADMIN_PASSWORD` — optional, defaults to hardcoded values if not set (should set on Railway)

## How to apply
Whenever debugging Railway auth issues, check these env vars first.
