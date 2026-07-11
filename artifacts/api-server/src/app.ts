import express, { type Express } from "express";
import cors from "cors";
import cookieParser from "cookie-parser";
import pinoHttp from "pino-http";
import path from "node:path";
import router from "./routes";
import { logger } from "./lib/logger";

const app: Express = express();

// Reflect the request's own Origin back — this is the only way to support
// credentials (cookies) cross-origin without knowing the frontend URL in advance.
// Railway proxies the request so the Origin header always contains the real
// browser origin, which the browser then validates against the response header.
app.use(
  cors({
    origin: true,          // reflect request origin → works with any frontend domain
    credentials: true,     // allow cookies
    methods: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
    preflightContinue: false,   // cors handles OPTIONS itself, no need for app.options()
    optionsSuccessStatus: 204,
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

// Serve the bot-hosting frontend (built into dist/public during `pnpm run build`).
// In dev this directory won't exist — that's fine, the frontend uses its own Vite server.
const publicDir = path.join(globalThis.__dirname ?? "dist", "public");
app.use(express.static(publicDir));

// SPA fallback — any non-API path gets index.html so client-side routing works.
app.use((req, res, next) => {
  if (req.path.startsWith("/api")) return next();
  res.sendFile(path.join(publicDir, "index.html"), (err) => {
    if (err) next(); // no index.html in dev — just 404
  });
});

export default app;
