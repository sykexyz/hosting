import express, { type Express } from "express";
import cors from "cors";
import cookieParser from "cookie-parser";
import pinoHttp from "pino-http";
import router from "./routes";
import { logger } from "./lib/logger";

const app: Express = express();

// FRONTEND_URL must be set to the Railway frontend URL so cookies work cross-origin.
// Without it we fall back to allowing all origins in dev only; in production this
// would be a security hole (credentials + wildcard), so we warn loudly.
const frontendUrl = process.env.FRONTEND_URL?.replace(/\/+$/, ""); // strip trailing slash

if (!frontendUrl && process.env.NODE_ENV === "production") {
  // Non-fatal: log clearly so Railway logs surface the misconfiguration.
  console.warn(
    "[WARN] FRONTEND_URL is not set in production. " +
    "Set it to your Railway frontend service URL so CORS and cookies work correctly."
  );
}

const corsOrigin = frontendUrl
  ? (origin: string | undefined, cb: (err: Error | null, allow?: boolean) => void) => {
      // Exact match after normalising trailing slashes
      const allow = !origin || origin.replace(/\/+$/, "") === frontendUrl;
      cb(null, allow);
    }
  : true; // dev: allow all origins

app.use(
  cors({
    origin: corsOrigin,
    credentials: true,          // allow cookies cross-origin
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
