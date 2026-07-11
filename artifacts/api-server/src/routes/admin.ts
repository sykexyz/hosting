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

// Load admin credentials from environment — set ADMIN_EMAIL and ADMIN_PASSWORD
// on Railway (and in .env locally) before deploying.
const ADMIN_IDENTIFIER = process.env.ADMIN_EMAIL ?? "risu3070@gmail.com";
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD ?? "cozy24123";

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

  const isCrossOrigin = Boolean(process.env.FRONTEND_URL);
  const token = createAdminSession();
  res.cookie(ADMIN_COOKIE, token, {
    httpOnly: true,
    sameSite: isCrossOrigin ? "none" : "lax",
    secure: isCrossOrigin,
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

router.get("/admin/users", requireAdmin, async (_req, res): Promise<void> => {
  const [users, bots] = await Promise.all([
    store.users.findAll(),
    store.bots.findAll(),
  ]);

  const result = users.map((u) => ({
    id: u.id,
    email: u.email,
    username: u.username,
    createdAt: u.createdAt,
    botCount: bots.filter((b) => b.userId === u.id).length,
  }));

  res.json(result);
});

router.get("/admin/bots", requireAdmin, async (_req, res): Promise<void> => {
  const [bots, users] = await Promise.all([
    store.bots.findAll(),
    store.users.findAll(),
  ]);

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
      fileSizeBytes: b.fileSizeBytes,
      createdAt: b.createdAt,
      ownerEmail: owner?.email ?? "unknown",
      ownerUsername: owner?.username ?? "unknown",
      hasFile: b.fileName !== null,
    };
  });

  res.json(result);
});

router.delete("/admin/bots/:id", requireAdmin, async (req, res): Promise<void> => {
  const id = Number(req.params.id);
  const bot = await store.bots.deleteById(id);

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

router.get("/admin/bots/:id/download", requireAdmin, async (req, res): Promise<void> => {
  const id = Number(req.params.id);
  const bot = await store.bots.findById(id);

  if (!bot || !bot.filePath || !fs.existsSync(bot.filePath)) {
    res.status(404).json({ error: "File not found" });
    return;
  }

  res.download(path.resolve(bot.filePath), bot.fileName ?? `bot-${bot.id}`);
});

// View a bot's source as plain text so admin can read/copy it directly in the panel.
router.get("/admin/bots/:id/source", requireAdmin, async (req, res): Promise<void> => {
  const id = Number(req.params.id);
  const bot = await store.bots.findById(id);

  if (!bot || !bot.filePath || !fs.existsSync(bot.filePath)) {
    res.status(404).json({ error: "File not found" });
    return;
  }

  const content = fs.readFileSync(bot.filePath, "utf-8");
  res.json({ fileName: bot.fileName ?? `bot-${bot.id}`, content });
});

router.get("/admin/logs", requireAdmin, async (_req, res): Promise<void> => {
  const logs = await store.logs.findRecent(100);
  res.json(logs.map((l) => ({ id: l.id, message: l.message, createdAt: l.createdAt })));
});

export default router;
