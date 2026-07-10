import { Router, type IRouter } from "express";
import fs from "node:fs";
import { store, type Bot } from "../lib/store";
import { CreateBotBody } from "@workspace/api-zod";
import { requireAuth } from "../middlewares/auth";
import { upload } from "../lib/uploads";
import { logActivity } from "../lib/activity-log";

const router: IRouter = Router();

function serializeBot(bot: Bot) {
  return {
    id: bot.id,
    name: bot.name,
    language: bot.language,
    ramMb: bot.ramMb,
    storageMb: bot.storageMb,
    status: bot.status,
    fileName: bot.fileName,
    createdAt: bot.createdAt,
  };
}

router.get("/bots", requireAuth, async (req, res): Promise<void> => {
  const bots = await store.bots.findByUserId(req.userId!);
  res.json(bots.map(serializeBot));
});

router.get("/bots/summary", requireAuth, async (req, res): Promise<void> => {
  const bots = await store.bots.findByUserId(req.userId!);
  const totalBots = bots.length;
  const runningBots = bots.filter((b) => b.status === "running").length;
  const totalRamMb = bots.reduce((sum, b) => sum + b.ramMb, 0);
  const totalStorageMb = bots.reduce((sum, b) => sum + b.storageMb, 0);
  res.json({ totalBots, runningBots, totalRamMb, totalStorageMb });
});

router.post("/bots", requireAuth, async (req, res): Promise<void> => {
  const parsed = CreateBotBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }

  const bot = await store.bots.insert({
    userId: req.userId!,
    name: parsed.data.name,
    language: parsed.data.language,
    ramMb: parsed.data.ramMb,
    storageMb: parsed.data.storageMb,
    status: "stopped",
    fileName: null,
    filePath: null,
  });

  logActivity(`Bot slot "${bot.name}" created`).catch(() => {});
  res.status(201).json(serializeBot(bot));
});

router.get("/bots/:id", requireAuth, async (req, res): Promise<void> => {
  const id = Number(req.params.id);
  const bot = await store.bots.findByIdAndUserId(id, req.userId!);
  if (!bot) {
    res.status(404).json({ error: "Bot not found" });
    return;
  }
  res.json(serializeBot(bot));
});

router.delete("/bots/:id", requireAuth, async (req, res): Promise<void> => {
  const id = Number(req.params.id);
  const bot = await store.bots.deleteByIdAndUserId(id, req.userId!);
  if (!bot) {
    res.status(404).json({ error: "Bot not found" });
    return;
  }

  if (bot.filePath && fs.existsSync(bot.filePath)) {
    fs.unlinkSync(bot.filePath);
  }

  logActivity(`Bot "${bot.name}" deleted`).catch(() => {});
  res.sendStatus(204);
});

// Validate that the bot exists and belongs to the requester BEFORE multer writes anything to disk.
async function requireOwnedBot(
  req: import("express").Request,
  res: import("express").Response,
  next: import("express").NextFunction,
): Promise<void> {
  const id = Number(req.params.id);
  const bot = await store.bots.findByIdAndUserId(id, req.userId!);
  if (!bot) {
    res.status(404).json({ error: "Bot not found" });
    return;
  }
  req.bot = bot;
  next();
}

router.post(
  "/bots/:id/upload",
  requireAuth,
  requireOwnedBot,
  upload.single("file"),
  async (req, res): Promise<void> => {
    const bot = req.bot!;

    if (!req.file) {
      res.status(400).json({ error: "No file uploaded" });
      return;
    }

    if (bot.filePath && fs.existsSync(bot.filePath) && bot.filePath !== req.file.path) {
      fs.unlinkSync(bot.filePath);
    }

    const updated = await store.bots.update(bot.id, {
      fileName: req.file.originalname,
      filePath: req.file.path,
    });

    if (!updated) {
      res.status(404).json({ error: "Bot not found" });
      return;
    }

    logActivity(`Source uploaded for bot "${bot.name}"`).catch(() => {});
    res.json(serializeBot(updated));
  },
);

router.post("/bots/:id/start", requireAuth, async (req, res): Promise<void> => {
  const id = Number(req.params.id);
  const bot = await store.bots.findByIdAndUserId(id, req.userId!);
  if (!bot) {
    res.status(404).json({ error: "Bot not found" });
    return;
  }

  if (!bot.fileName) {
    res.status(400).json({ error: "Upload a source file before starting this bot" });
    return;
  }

  const updated = await store.bots.update(id, { status: "running" });
  logActivity(`Bot "${bot.name}" started`).catch(() => {});
  res.json(serializeBot(updated ?? bot));
});

router.post("/bots/:id/stop", requireAuth, async (req, res): Promise<void> => {
  const id = Number(req.params.id);
  const bot = await store.bots.findByIdAndUserId(id, req.userId!);
  if (!bot) {
    res.status(404).json({ error: "Bot not found" });
    return;
  }

  const updated = await store.bots.update(id, { status: "stopped" });
  logActivity(`Bot "${bot.name}" stopped`).catch(() => {});
  res.json(serializeBot(updated ?? bot));
});

export default router;
