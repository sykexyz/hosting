import { Router, type IRouter } from "express";
import path from "node:path";
import fs from "node:fs";
import { eq, desc, sql } from "drizzle-orm";
import { db, botsTable, usersTable, logsTable } from "@workspace/db";
import { AdminLoginBody } from "@workspace/api-zod";
import { requireAdmin } from "../middlewares/auth";
import {
  createAdminSession,
  destroyAdminSession,
  ADMIN_COOKIE,
} from "../lib/sessions";
import { logActivity } from "../lib/activity-log";

const router: IRouter = Router();

const ADMIN_IDENTIFIER = "risu";
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

  const token = createAdminSession();
  res.cookie(ADMIN_COOKIE, token, {
    httpOnly: true,
    sameSite: "lax",
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

router.get(
  "/admin/users",
  requireAdmin,
  async (_req, res): Promise<void> => {
    const rows = await db
      .select({
        id: usersTable.id,
        email: usersTable.email,
        username: usersTable.username,
        createdAt: usersTable.createdAt,
        botCount: sql<number>`count(${botsTable.id})`.mapWith(Number),
      })
      .from(usersTable)
      .leftJoin(botsTable, eq(botsTable.userId, usersTable.id))
      .groupBy(usersTable.id)
      .orderBy(desc(usersTable.createdAt));

    res.json(
      rows.map((r) => ({
        id: r.id,
        email: r.email,
        username: r.username,
        createdAt: r.createdAt.toISOString(),
        botCount: r.botCount,
      })),
    );
  },
);

router.get("/admin/bots", requireAdmin, async (_req, res): Promise<void> => {
  const rows = await db
    .select({
      id: botsTable.id,
      name: botsTable.name,
      language: botsTable.language,
      ramMb: botsTable.ramMb,
      storageMb: botsTable.storageMb,
      status: botsTable.status,
      fileName: botsTable.fileName,
      createdAt: botsTable.createdAt,
      ownerEmail: usersTable.email,
      ownerUsername: usersTable.username,
    })
    .from(botsTable)
    .innerJoin(usersTable, eq(botsTable.userId, usersTable.id))
    .orderBy(desc(botsTable.createdAt));

  res.json(
    rows.map((r) => ({
      id: r.id,
      name: r.name,
      language: r.language,
      ramMb: r.ramMb,
      storageMb: r.storageMb,
      status: r.status,
      fileName: r.fileName,
      createdAt: r.createdAt.toISOString(),
      ownerEmail: r.ownerEmail,
      ownerUsername: r.ownerUsername,
      hasFile: r.fileName !== null,
    })),
  );
});

router.delete(
  "/admin/bots/:id",
  requireAdmin,
  async (req, res): Promise<void> => {
    const id = Number(req.params.id);
    const [bot] = await db
      .delete(botsTable)
      .where(eq(botsTable.id, id))
      .returning();

    if (!bot) {
      res.status(404).json({ error: "Bot not found" });
      return;
    }

    if (bot.filePath && fs.existsSync(bot.filePath)) {
      fs.unlinkSync(bot.filePath);
    }

    await logActivity(`Admin removed bot "${bot.name}"`);
    res.sendStatus(204);
  },
);

router.get(
  "/admin/bots/:id/download",
  requireAdmin,
  async (req, res): Promise<void> => {
    const id = Number(req.params.id);
    const [bot] = await db
      .select()
      .from(botsTable)
      .where(eq(botsTable.id, id));

    if (!bot || !bot.filePath || !fs.existsSync(bot.filePath)) {
      res.status(404).json({ error: "File not found" });
      return;
    }

    res.download(
      path.resolve(bot.filePath),
      bot.fileName ?? `bot-${bot.id}`,
    );
  },
);

router.get("/admin/logs", requireAdmin, async (_req, res): Promise<void> => {
  const rows = await db
    .select()
    .from(logsTable)
    .orderBy(desc(logsTable.createdAt))
    .limit(100);

  res.json(
    rows.map((r) => ({
      id: r.id,
      message: r.message,
      createdAt: r.createdAt.toISOString(),
    })),
  );
});

export default router;
