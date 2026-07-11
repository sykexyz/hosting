## ── Stage 1: build ──────────────────────────────────────────────────────────
FROM node:24-bookworm-slim AS builder

# Install python3 + venv (needed both at build time for bot-runner venv calls
# AND at runtime so spawned bots can use it)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm (same version as the workspace)
RUN npm install -g pnpm@10.26.1

WORKDIR /app

# Copy workspace manifests + root TypeScript configs first (for layer caching).
# tsconfig.base.json lives at the repo root; every package tsconfig extends it
# via a relative path (../../tsconfig.base.json) — without it the build fails.
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml .npmrc tsconfig.base.json tsconfig.json ./

# Copy all packages (source + configs)
COPY lib/ ./lib/
COPY artifacts/ ./artifacts/

# Install all workspace deps
RUN pnpm install --frozen-lockfile

# Build api-server (build.mjs also builds the bot-hosting frontend and copies it to dist/public)
RUN pnpm --filter @workspace/api-server run build

## ── Stage 2: runtime ────────────────────────────────────────────────────────
FROM node:24-bookworm-slim AS runtime

# Python3 is required at runtime so the server can spawn python bots
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm so Railway's configured start command
# "pnpm --filter @workspace/api-server start" resolves correctly.
RUN npm install -g pnpm@10.26.1

WORKDIR /app

# Workspace manifests needed for pnpm --filter to resolve the package
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/pnpm-workspace.yaml ./pnpm-workspace.yaml

# api-server package.json (contains the "start" script definition)
COPY --from=builder /app/artifacts/api-server/package.json ./artifacts/api-server/package.json

# Built output + runtime node_modules
COPY --from=builder /app/artifacts/api-server/dist ./artifacts/api-server/dist
COPY --from=builder /app/artifacts/api-server/node_modules ./artifacts/api-server/node_modules
COPY --from=builder /app/node_modules ./node_modules

# Writable runtime directories (uploads & per-bot envs)
RUN mkdir -p artifacts/api-server/uploads artifacts/api-server/bot-envs

EXPOSE 8080

ENV NODE_ENV=production
ENV PORT=8080

# The server's process.cwd() determines where bot-envs/ and uploads/ live.
# Run from the api-server dir so relative paths (bot-envs/{id}/venv etc.) stay consistent.
WORKDIR /app/artifacts/api-server

# Railway may override this CMD with "pnpm --filter @workspace/api-server start"
# (which pnpm resolves to the same node command below). Both work.
CMD ["node", "--enable-source-maps", "./dist/index.mjs"]
