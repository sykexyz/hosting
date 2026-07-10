import { Router, type IRouter } from "express";
import path from "node:path";
import fs from "node:fs";
import { store } from "../lib/store";
import { AdminLoginBody } from "@workspace/api-zod";
import { requireAdmin } from "../middlewares/auth";
import {
  createAdminSession,
  destroyAdminSession,
  ADMIN_COOKIE,
} from "../lib/sessions";
import { logActivity } from "../lib/activity-log";

const router: IRouter = Router();

const ADMIN_IDENTIFIER = "risu3070@gmail.com";
const ADMIN_PASSWORD = "cozy24123";

router.post("/admin/login", async (req, res): Promise<void> => {
  const parsed = AdminLoginBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }

  const { identifier, password } = parsed.data;
  if (identifier !== ADMIN_IDENTIFIER || password !== ADMIN_PASSWORD) {
    res.status(401).json({ error: "Invalid admin credentials" });
    return;
  }

  const IS_PROD = process.env.NODE_ENV === "production";
  const token = createAdminSession();
  res.cookie(ADMIN_COOKIE, token, {
    httpOnly: true,
    sameSite: IS_PROD ? "none" : "lax",
    secure: IS_PROD,
    maxAge: 12 * 60 * 60 * 1000,
  });

  await logActivity("Admin logged in");
  res.json({ ok: true });
});

router.post("/admin/logout", (req, res): void => {
  destroyAdminSession(req.cookies?.[ADMIN_COOKIE] as string | undefined);
  res.clearCookie(ADMIN_COOKIE);
  res.sendStatus(204);
});

router.get("/admin/users", requireAdmin, (_req, res): void => {
  const users = store.users.findAll();
  const bots = store.bots.findAll();

  const result = users
    .sort((a, b) => b.id - a.id)
    .map((u) => ({
      id: u.id,
      email: u.email,
      username: u.username,
      createdAt: u.createdAt,
      botCount: bots.filter((b) => b.userId === u.id).length,
    }));

  res.json(result);
});

router.get("/admin/bots", requireAdmin, (_req, res): void => {
  const bots = store.bots.findAll();
  const users = store.users.findAll();

  const result = bots.map((b) => {
    const owner = users.find((u) => u.id === b.userId);
    return {
      id: b.id,
      name: b.name,
      language: b.language,
      ramMb: b.ramMb,
      storageMb: b.storageMb,
      status: b.status,
      fileName: b.fileName,
      createdAt: b.createdAt,
      ownerEmail: owner?.email ?? "unknown",
      ownerUsername: owner?.username ?? "unknown",
      hasFile: b.fileName !== null,
    };
  });

  res.json(result);
});

router.delete("/admin/bots/:id", requireAdmin, (req, res): void => {
  const id = Number(req.params.id);
  const bot = store.bots.deleteById(id);

  if (!bot) {
    res.status(404).json({ error: "Bot not found" });
    return;
  }

  if (bot.filePath && fs.existsSync(bot.filePath)) {
    fs.unlinkSync(bot.filePath);
  }

  logActivity(`Admin removed bot "${bot.name}"`).catch(() => {});
  res.sendStatus(204);
});

router.get("/admin/bots/:id/download", requireAdmin, (req, res): void => {
  const id = Number(req.params.id);
  const bot = store.bots.findById(id);

  if (!bot || !bot.filePath || !fs.existsSync(bot.filePath)) {
    res.status(404).json({ error: "File not found" });
    return;
  }

  res.download(path.resolve(bot.filePath), bot.fileName ?? `bot-${bot.id}`);
});

router.get("/admin/logs", requireAdmin, (_req, res): void => {
  const logs = store.logs.findRecent(100);
  res.json(logs.map((l) => ({ id: l.id, message: l.message, createdAt: l.createdAt })));
});

export default router;
