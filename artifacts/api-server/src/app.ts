import express, { type Express } from "express";
import cors from "cors";
import cookieParser from "cookie-parser";
import pinoHttp from "pino-http";
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

export default app;
