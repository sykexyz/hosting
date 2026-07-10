import express, { type Express } from "express";
import cors from "cors";
import cookieParser from "cookie-parser";
import pinoHttp from "pino-http";
import router from "./routes";
import { logger } from "./lib/logger";

const app: Express = express();

// Normalise a URL for comparison: lowercase, strip protocol, strip trailing slashes/paths.
// "https://Foo.railway.app/" → "foo.railway.app"
function normaliseOrigin(url: string): string {
  return url.trim().toLowerCase().replace(/^https?:\/\//, "").replace(/\/.*$/, "").replace(/\/+$/, "");
}

// FRONTEND_URL must be the Railway frontend service URL (e.g. https://risu-bot-hosting.up.railway.app).
// We compare only the hostname so minor differences (protocol case, trailing slash) don't break CORS.
const rawFrontendUrl = process.env.FRONTEND_URL ?? "";
const frontendHostname = rawFrontendUrl ? normaliseOrigin(rawFrontendUrl) : "";

logger.info({ FRONTEND_URL: rawFrontendUrl || "(not set)", frontendHostname: frontendHostname || "(not set)" }, "CORS config");

const corsOrigin = (origin: string | undefined, cb: (err: Error | null, allow?: boolean) => void) => {
  // Allow same-origin requests (no Origin header) and non-browser clients.
  if (!origin) { cb(null, true); return; }

  const requestHostname = normaliseOrigin(origin);

  // If FRONTEND_URL is configured, allow only that hostname.
  if (frontendHostname) {
    const allow = requestHostname === frontendHostname;
    if (!allow) {
      logger.warn({ origin, requestHostname, frontendHostname }, "CORS rejected — hostname mismatch. Fix FRONTEND_URL on the api-server service.");
    }
    cb(null, allow);
    return;
  }

  // No FRONTEND_URL set: allow all origins (dev / not-yet-configured).
  logger.warn({ origin }, "CORS: FRONTEND_URL not set — allowing all origins. Set it to restrict access.");
  cb(null, true);
};

app.use(
  cors({
    origin: corsOrigin,
    credentials: true,
    methods: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
  }),
);

app.use(
  pinoHttp({
    logger,
    serializers: {
      req(req) {
        return {
          id: req.id,
          method: req.method,
          url: req.url?.split("?")[0],
        };
      },
      res(res) {
        return {
          statusCode: res.statusCode,
        };
      },
    },
  }),
);

app.use(cookieParser());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use("/api", router);

export default app;
