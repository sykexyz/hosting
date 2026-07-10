import app from "./app";
import { logger } from "./lib/logger";
import { ensureSchema } from "./lib/migrate";

const rawPort = process.env["PORT"];

if (!rawPort) {
  throw new Error(
    "PORT environment variable is required but was not provided.",
  );
}

const port = Number(rawPort);

if (Number.isNaN(port) || port <= 0) {
  throw new Error(`Invalid PORT value: "${rawPort}"`);
}

// Log env var status so Railway logs show exactly what is/isn't set
logger.info({
  DATABASE_URL: process.env.DATABASE_URL ? "✓ set" : "✗ MISSING",
  FRONTEND_URL: process.env.FRONTEND_URL ? "✓ set" : "(not set — CORS will allow all origins)",
  NODE_ENV: process.env.NODE_ENV ?? "(not set)",
}, "Environment check");

if (!process.env.DATABASE_URL) {
  logger.error(
    "DATABASE_URL is not set! " +
    "On Railway: api-server service → Variables → add DATABASE_URL " +
    "= the DATABASE_URL value from your PostgreSQL service."
  );
  process.exit(1);
}

// Ensure all DB tables exist before accepting traffic.
await ensureSchema();
logger.info("Database schema verified");

app.listen(port, (err) => {
  if (err) {
    logger.error({ err }, "Error listening on port");
    process.exit(1);
  }
  logger.info({ port }, "Server listening");
});
