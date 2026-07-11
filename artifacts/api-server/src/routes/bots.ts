import { Router, type IRouter } from "express";
import fs from "node:fs";
import path from "node:path";
import { store, type Bot } from "../lib/store";
import { CreateBotBody } from "@workspace/api-zod";
import { requireAuth } from "../middlewares/auth";
import { upload } from "../lib/uploads";
import { logActivity } from "../lib/activity-log";
import { detectPackages } from "../lib/dep-detector";
import { startBot, stopBot, isBotRunning } from "../lib/bot-runner";

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

    if (!updated) { res.status(404).json({ error: "Bot not found" }); return; }

    let detectedPackages: string[] = [];
    try {
      const source = fs.readFileSync(req.file.path, "utf-8");
      detectedPackages = detectPackages(bot.language, source);
    } catch { /* non-fatal */ }

    logActivity(`Source uploaded for bot "${bot.name}" (${detectedPackages.length} deps detected)`).catch(() => {});
    res.json({ ...serializeBot(updated), detectedPackages });
  },
);

// Save source code sent as plain text (replaces file upload for the textarea flow)
router.post("/bots/:id/source", requireAuth, requireOwnedBot, async (req, res): Promise<void> => {
  const bot = req.bot!;
  const { code, fileName } = req.body as { code?: string; fileName?: string };

  if (typeof code !== "string" || code.trim().length === 0) {
    res.status(400).json({ error: "code is required" });
    return;
  }

  // Determine file extension from language
  const extMap: Record<string, string> = {
    python: "py", javascript: "js", typescript: "ts", java: "java", other: "txt",
  };
  const ext = extMap[bot.language] ?? "txt";
  const name = fileName?.trim() || `bot.${ext}`;

  // Write to uploads directory
  const uploadsDir = path.join(process.cwd(), "uploads");
  fs.mkdirSync(uploadsDir, { recursive: true });
  const filePath = path.join(uploadsDir, `${bot.id}-${Date.now()}-${name}`);

  // Remove old file if any
  if (bot.filePath && fs.existsSync(bot.filePath) && bot.filePath !== filePath) {
    fs.unlinkSync(bot.filePath);
  }

  fs.writeFileSync(filePath, code, "utf-8");

  const updated = await store.bots.update(bot.id, { fileName: name, filePath });
  if (!updated) { res.status(404).json({ error: "Bot not found" }); return; }

  const detectedPackages = detectPackages(bot.language, code);
  logActivity(`Source saved for bot "${bot.name}" (${detectedPackages.length} deps detected)`).catch(() => {});
  res.json({ ...serializeBot(updated), detectedPackages });
});

router.post("/bots/:id/start", requireAuth, async (req, res): Promise<void> => {
  const id = Number(req.params.id);
  const bot = await store.bots.findByIdAndUserId(id, req.userId!);
  if (!bot) { res.status(404).json({ error: "Bot not found" }); return; }
  if (!bot.filePath || !bot.fileName) {
    res.status(400).json({ error: "Upload a source file before starting this bot" });
    return;
  }
  if (!fs.existsSync(bot.filePath)) {
    res.status(400).json({ error: "Source file not found on server — please re-upload" });
    return;
  }

  try {
    const { packages } = await startBot(id, bot.name, bot.language, bot.filePath);
    const updated = await store.bots.update(id, { status: "running" });
    res.json({ ...serializeBot(updated ?? bot), installedPackages: packages });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    await store.bots.update(id, { status: "stopped" });
    res.status(500).json({ error: `Failed to start bot: ${msg}` });
  }
});

router.post("/bots/:id/stop", requireAuth, async (req, res): Promise<void> => {
  const id = Number(req.params.id);
  const bot = await store.bots.findByIdAndUserId(id, req.userId!);
  if (!bot) { res.status(404).json({ error: "Bot not found" }); return; }

  await stopBot(id, bot.name);
  const updated = await store.bots.update(id, { status: "stopped" });
  res.json(serializeBot(updated ?? bot));
});

export default router;
