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

# Same python3 packages needed at runtime so the server can spawn python bots
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy built output + runtime node_modules from builder
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

CMD ["node", "--enable-source-maps", "./dist/index.mjs"]
