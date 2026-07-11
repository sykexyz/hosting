/**
 * Bot process manager.
 * Spawns, tracks, and terminates bot child processes.
 * Installs detected dependencies before first run.
 */

import { spawn, execSync, type ChildProcess } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { logActivity } from "./activity-log.js";
import { detectPackages } from "./dep-detector.js";

// botId → live process
const running = new Map<number, ChildProcess>();

// Base directory for per-bot environments (node_modules / venvs)
const BOT_ENVS = path.join(process.cwd(), "bot-envs");
fs.mkdirSync(BOT_ENVS, { recursive: true });

function envDir(botId: number): string {
  const d = path.join(BOT_ENVS, String(botId));
  fs.mkdirSync(d, { recursive: true });
  return d;
}

// ---------------------------------------------------------------------------
// Dependency installation
// ---------------------------------------------------------------------------

function installPython(packages: string[], dir: string): void {
  if (packages.length === 0) return;
  const venv = path.join(dir, "venv");

  if (!fs.existsSync(path.join(venv, "bin", "python3"))) {
    execSync(`python3 -m venv "${venv}"`, { timeout: 60_000, stdio: "pipe" });
  }

  const pip = path.join(venv, "bin", "pip");
  execSync(`"${pip}" install --quiet ${packages.map(p => JSON.stringify(p)).join(" ")}`, {
    timeout: 180_000,
    stdio: "pipe",
  });
}

function installNode(packages: string[], dir: string): void {
  if (packages.length === 0) return;
  const pkgJson = path.join(dir, "package.json");
  if (!fs.existsSync(pkgJson)) {
    fs.writeFileSync(pkgJson, JSON.stringify({ name: "bot", version: "1.0.0", private: true }));
  }
  execSync(`npm install --prefix "${dir}" --save ${packages.join(" ")} 2>&1`, {
    timeout: 180_000,
    stdio: "pipe",
  });
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export function isBotRunning(botId: number): boolean {
  return running.has(botId);
}

/**
 * Install dependencies detected in the source file, then spawn the bot.
 * Returns the list of packages that were installed (may be empty).
 */
export async function startBot(
  botId: number,
  botName: string,
  language: string,
  filePath: string,
): Promise<{ packages: string[] }> {
  // Kill existing process for this bot if any
  await stopBot(botId, botName, /* silent */ true);

  const source = fs.readFileSync(filePath, "utf-8");
  const packages = detectPackages(language, source);
  const dir = envDir(botId);

  // Install deps synchronously (execSync) — this runs in the request handler
  // but is fine since start is an intentional user action, not a hot path.
  try {
    if (language === "python") {
      installPython(packages, dir);
    } else if (language === "javascript" || language === "typescript") {
      installNode(packages, dir);
    }
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    logActivity(`[${botName}] dep install warning: ${msg}`).catch(() => {});
    // Non-fatal: attempt to run anyway
  }

  // Build spawn command
  let cmd: string;
  let args: string[];
  const env: NodeJS.ProcessEnv = { ...process.env };

  if (language === "python") {
    const venvPy = path.join(dir, "venv", "bin", "python3");
    cmd = fs.existsSync(venvPy) ? venvPy : "python3";
    args = [filePath];
  } else if (language === "javascript") {
    cmd = "node";
    args = [filePath];
    env["NODE_PATH"] = path.join(dir, "node_modules");
  } else if (language === "typescript") {
    // Prefer tsx (faster, no compile step); fall back to ts-node
    const tsxBin = path.join(dir, "node_modules", ".bin", "tsx");
    if (fs.existsSync(tsxBin)) {
      cmd = tsxBin;
      args = [filePath];
    } else {
      cmd = "npx";
      args = ["--yes", "tsx", filePath];
    }
    env["NODE_PATH"] = path.join(dir, "node_modules");
  } else if (language === "java") {
    // Compile first, then run
    const classDir = path.join(dir, "classes");
    fs.mkdirSync(classDir, { recursive: true });
    execSync(`javac -d "${classDir}" "${filePath}"`, { timeout: 30_000, stdio: "pipe" });
    const className = path.basename(filePath, ".java");
    cmd = "java";
    args = ["-cp", classDir, className];
  } else {
    throw new Error(`Language "${language}" is not supported for execution yet.`);
  }

  const proc = spawn(cmd, args, {
    cwd: dir,
    env,
    stdio: ["ignore", "pipe", "pipe"],
  });

  running.set(botId, proc);

  proc.stdout?.on("data", (chunk: Buffer) => {
    const text = chunk.toString().trim();
    if (text) logActivity(`[${botName}] ${text}`).catch(() => {});
  });

  proc.stderr?.on("data", (chunk: Buffer) => {
    const text = chunk.toString().trim();
    if (text) logActivity(`[${botName} ERR] ${text}`).catch(() => {});
  });

  proc.on("exit", (code, signal) => {
    running.delete(botId);
    logActivity(`Bot "${botName}" exited (code=${code ?? "?"} signal=${signal ?? "-"})`).catch(() => {});
  });

  proc.on("error", (err) => {
    running.delete(botId);
    logActivity(`Bot "${botName}" spawn error: ${err.message}`).catch(() => {});
  });

  logActivity(`Bot "${botName}" started (pid=${proc.pid}, lang=${language}, deps=[${packages.join(",")}])`).catch(() => {});
  return { packages };
}

export async function stopBot(
  botId: number,
  botName: string,
  silent = false,
): Promise<void> {
  const proc = running.get(botId);
  if (!proc) return;

  proc.kill("SIGTERM");

  // Give it 3 s to exit gracefully, then SIGKILL
  await new Promise<void>((resolve) => {
    const timeout = setTimeout(() => {
      try { proc.kill("SIGKILL"); } catch { /* already dead */ }
      resolve();
    }, 3000);
    proc.once("exit", () => { clearTimeout(timeout); resolve(); });
  });

  running.delete(botId);
  if (!silent) logActivity(`Bot "${botName}" stopped`).catch(() => {});
}
