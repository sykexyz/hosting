import { useEffect, useState, useRef, useCallback } from "react";
import { useLocation } from "wouter";
import { Logo } from "../components/Logo";
import { StarField } from "../components/StarField";
import { UptimeTimer } from "../components/UptimeTimer";
import { AnimatedCounter } from "../components/AnimatedCounter";
import { motion, AnimatePresence } from "framer-motion";
import {
  useGetCurrentUser,
  useListBots,
  useGetBotSummary,
  useCreateBot,
  useLogout,
  useStartBot,
  useStopBot,
  useDeleteBot,
  useGetBot,
  useListBotLogs,
  getListBotsQueryKey,
  getGetBotSummaryQueryKey,
  BotInputLanguage,
  BotInputRamMb,
  BotInputStorageMb,
} from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { ContextMenu, ContextMenuContent, ContextMenuItem, ContextMenuSeparator, ContextMenuTrigger } from "@/components/ui/context-menu";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { toast } from "sonner";
import { format } from "date-fns";
import { SiPython, SiJavascript, SiTypescript } from "react-icons/si";
import { FaJava } from "react-icons/fa";
import { BsCodeSlash } from "react-icons/bs";
import CodeInput from "@/components/CodeInput";

const LANG_OPTIONS = [
  { id: BotInputLanguage.python,     name: "Python",     Icon: SiPython,     ext: "py" },
  { id: BotInputLanguage.javascript, name: "JavaScript", Icon: SiJavascript, ext: "js" },
  { id: BotInputLanguage.typescript, name: "TypeScript", Icon: SiTypescript, ext: "ts" },
  { id: BotInputLanguage.java,       name: "Java",       Icon: FaJava,       ext: "java" },
  { id: BotInputLanguage.other,      name: "Other",      Icon: BsCodeSlash,  ext: "txt" },
];

const LANG_MODULES: Record<string, string[]> = {
  python:     ["runtime.cpython", "asyncio", "threading", "json", "os", "pathlib"],
  javascript: ["node:events", "node:fs", "node:path", "node:http", "node:stream"],
  typescript: ["ts-node/register", "node:fs", "typescript/lib", "@types/node", "node:path"],
  java:       ["java.io", "java.util", "java.net", "java.lang", "java.nio"],
  other:      ["core.runtime", "io.module", "net.module", "sys.module", "util.module"],
};

const LANG_MONACO: Record<string, string> = {
  python: "python", javascript: "javascript", typescript: "typescript",
  java: "java", other: "plaintext",
};

function formatBotStatus(s: string) { return s === "running" ? "Online" : s === "error" ? "Error" : s; }
function formatBytes(b: number | null | undefined) {
  if (b === null || b === undefined) return "—";
  if (b < 1024) return `${b} B`;
  if (b < 1024 * 1024) return `${(b / 1024).toFixed(1)} KB`;
  return `${(b / (1024 * 1024)).toFixed(2)} MB`;
}
function getUserInitials(email?: string, username?: string) {
  if (username) return username.slice(0, 2).toUpperCase();
  if (email) return email.slice(0, 2).toUpperCase();
  return "??";
}

/* ── Skeleton ── */
function Skeleton({ className }: { className?: string }) {
  return <div className={`skeleton ${className ?? ""}`} />;
}

/* ── Upload overlay ── */
type UploadPhase =
  | { kind: "idle" }
  | { kind: "loading"; fileName: string; steps: string[]; stepIdx: number }
  | { kind: "success"; fileName: string }
  | { kind: "error"; message: string };

function UploadOverlay({ phase, onDismiss }: { phase: Exclude<UploadPhase, { kind: "idle" }>; onDismiss: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[200] flex items-center justify-center bg-black/85 backdrop-blur-md p-6"
      onClick={phase.kind !== "loading" ? onDismiss : undefined}
    >
      <motion.div
        initial={{ scale: 0.95, y: 10 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.95, y: 10 }}
        className="w-full max-w-lg rounded-xl overflow-hidden"
        style={{ background: "#07070a", border: "1px solid rgba(255,255,255,0.1)", boxShadow: "0 0 60px rgba(0,0,0,0.9), 0 0 120px rgba(120,80,220,0.08)" }}
        onClick={e => e.stopPropagation()}
      >
        <div className="p-8 min-h-[220px] flex flex-col items-center justify-center gap-5">
          {phase.kind === "loading" && (() => {
            const total = Math.max(phase.steps.length, 1);
            const pct = Math.round(((phase.stepIdx + 1) / total) * 100);
            return (
              <>
                <p className="text-white/70 text-sm font-medium tracking-wide">Uploading your bot…</p>
                <div className="w-full max-w-sm h-2 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.08)" }}>
                  <div
                    className="h-full rounded-full transition-all duration-300 ease-out"
                    style={{ width: `${pct}%`, background: "linear-gradient(90deg, rgba(168,130,255,0.9), rgba(120,190,255,0.9))" }}
                  />
                </div>
                <p className="text-white/35 text-xs font-mono">{pct}%</p>
              </>
            );
          })()}
          {phase.kind === "success" && (
            <div className="flex flex-col items-center justify-center py-8 gap-4 text-center">
              <div className="text-5xl mb-2 text-green-400" style={{ filter: "drop-shadow(0 0 20px rgba(74,222,128,0.7))" }}>✓</div>
              <p className="text-white text-lg font-bold tracking-wide">Successfully hosted</p>
              <p className="text-white/50 text-sm font-mono bg-white/5 border border-white/10 px-4 py-2 rounded-lg">{phase.fileName}</p>
              <button onClick={onDismiss} className="mt-4 px-6 py-2 rounded-lg text-white/60 text-sm hover:text-white transition-colors" style={{ border: "1px solid rgba(255,255,255,0.15)", background: "rgba(255,255,255,0.04)" }}>Close</button>
            </div>
          )}
          {phase.kind === "error" && (
            <div className="flex flex-col items-center justify-center py-8 gap-4 text-center">
              <div className="text-4xl text-red-400 mb-2">✗</div>
              <p className="text-red-300 text-base font-bold">Upload failed</p>
              <p className="text-white/35 text-sm">{phase.message}</p>
              <button onClick={onDismiss} className="mt-4 px-6 py-2 rounded-lg text-red-300/80 text-sm transition-colors" style={{ border: "1px solid rgba(239,68,68,0.25)", background: "rgba(239,68,68,0.06)" }}>Close</button>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}

/* ── Live logs panel ── */
function BotLogsPanel({ botId }: { botId: number }) {
  const { data: logs, isLoading } = useListBotLogs(botId, { query: { refetchInterval: 3000 } as any });
  const logEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const [search, setSearch] = useState("");
  const [levelFilter, setLevelFilter] = useState<"all" | "info" | "warn" | "err">("all");
  const [fontSize, setFontSize] = useState(12);

  useEffect(() => {
    if (autoScroll) logEndRef.current?.scrollIntoView({ block: "end", behavior: "smooth" });
  }, [logs, autoScroll]);

  const getLogLevel = (msg: string): "err" | "warn" | "info" => {
    if (msg.includes("[ERR]") || msg.includes(" ERR]") || msg.includes("error") || msg.includes("Error")) return "err";
    if (msg.includes("[WARN]") || msg.includes("warn") || msg.includes("WARN")) return "warn";
    return "info";
  };

  const getLogColor = (level: "err" | "warn" | "info") => {
    if (level === "err")  return "text-red-400/90";
    if (level === "warn") return "text-yellow-400/80";
    return "text-white/65";
  };

  const filtered = logs?.filter((log: any) => {
    const level = getLogLevel(log.message);
    if (levelFilter !== "all" && level !== levelFilter) return false;
    if (search && !log.message.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const handleDownload = () => {
    if (!logs?.length) return;
    const text = logs.map((l: any) => `[${format(new Date(l.createdAt), "HH:mm:ss")}] ${l.message}`).join("\n");
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = `bot-${botId}-logs.txt`; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="rounded-xl overflow-hidden crt-overlay" style={{ background: "rgba(0,0,0,0.6)", border: "1px solid rgba(255,255,255,0.07)" }}>
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-white/8" style={{ background: "rgba(255,255,255,0.02)" }}>
        <span className="text-[10px] text-white/35 uppercase tracking-widest font-bold font-mono">Live Console</span>
        <div className="flex items-center gap-2">
          {/* Font size */}
          <button onClick={() => setFontSize(f => Math.max(9, f - 1))} className="text-white/30 hover:text-white/60 text-xs px-1 transition-colors">A-</button>
          <span className="text-white/20 text-[10px] font-mono">{fontSize}px</span>
          <button onClick={() => setFontSize(f => Math.min(18, f + 1))} className="text-white/30 hover:text-white/60 text-xs px-1 transition-colors">A+</button>
          {/* Auto scroll */}
          <button
            onClick={() => setAutoScroll(v => !v)}
            className={`text-[10px] px-2 py-0.5 rounded transition-colors ${autoScroll ? "text-green-400/80 border border-green-400/20 bg-green-400/5" : "text-white/30 border border-white/10"}`}
          >
            {autoScroll ? "↓ AUTO" : "↓ OFF"}
          </button>
          {/* Download */}
          <button onClick={handleDownload} className="text-white/30 hover:text-white/60 text-[10px] px-2 py-0.5 rounded border border-white/8 hover:border-white/20 transition-colors" title="Download logs">⬇ DL</button>
        </div>
      </div>
      {/* Search + filter */}
      <div className="flex gap-2 px-3 py-2 border-b border-white/6">
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search logs..."
          className="flex-1 bg-transparent text-white/60 text-[11px] font-mono outline-none placeholder:text-white/20"
          style={{ fontSize: fontSize - 1 }}
        />
        <div className="flex gap-1">
          {(["all","info","warn","err"] as const).map(l => (
            <button
              key={l}
              onClick={() => setLevelFilter(l)}
              className={`text-[10px] px-2 py-0.5 rounded transition-colors ${
                levelFilter === l
                  ? l === "err" ? "bg-red-400/15 text-red-400/90 border border-red-400/25"
                    : l === "warn" ? "bg-yellow-400/15 text-yellow-400/80 border border-yellow-400/25"
                    : "bg-white/8 text-white/70 border border-white/15"
                  : "text-white/25 hover:text-white/45"
              }`}
            >
              {l.toUpperCase()}
            </button>
          ))}
        </div>
      </div>
      {/* Log content */}
      <div
        ref={containerRef}
        className="p-3 max-h-52 overflow-y-auto space-y-0.5"
        style={{ fontFamily: "'Spline Sans Mono', monospace", fontSize }}
      >
        {isLoading ? (
          <div className="text-white/25">Loading logs...</div>
        ) : !filtered?.length ? (
          <div className="text-white/25">
            {search || levelFilter !== "all" ? "No matching logs." : "No output yet. Start the bot to see console output here."}
          </div>
        ) : (
          filtered.map((log: any) => {
            const level = getLogLevel(log.message);
            return (
              <div key={log.id} className={`flex gap-3 ${getLogColor(level)} leading-relaxed`}>
                <span className="text-white/22 shrink-0">{format(new Date(log.createdAt), "HH:mm:ss")}</span>
                <span className="break-all">{log.message}</span>
              </div>
            );
          })
        )}
        <div ref={logEndRef} />
      </div>
    </div>
  );
}

/* ── Bot details modal ── */
function BotDetailsModal({ botId, onClose }: { botId: number; onClose: () => void }) {
  const { data: bot, isLoading } = useGetBot(botId);

  const handleCopySource = async () => {
    if (!bot) return;
    try {
      const res = await fetch(`${import.meta.env.BASE_URL}api/bots/${botId}/source`, { credentials: "include" });
      const data = await res.json() as { content?: string };
      if (data.content) {
        await navigator.clipboard.writeText(data.content);
        toast.success("Copied!", { description: "Source code copied to clipboard" });
      }
    } catch {
      toast.error("Copy failed");
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[100] flex items-center justify-center p-6"
      style={{ background: "rgba(0,0,0,0.7)", backdropFilter: "blur(16px)" }}
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95, y: 12 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.95, y: 12, opacity: 0 }}
        onClick={e => e.stopPropagation()}
        className="w-full max-w-md"
      >
        <Card className="glass-panel shadow-[0_8px_80px_rgba(0,0,0,0.9)]" style={{ borderColor: "rgba(255,255,255,0.12)" }}>
          <CardHeader className="pb-4 border-b border-white/10">
            <div className="flex justify-between items-center">
              <CardTitle className="text-xl text-white font-bold">Instance Details</CardTitle>
              <div className="flex items-center gap-2">
                <button onClick={handleCopySource} className="h-7 px-3 text-xs text-white/50 hover:text-white rounded-lg border border-white/10 hover:border-white/25 transition-colors font-mono">COPY SRC</button>
                <button onClick={onClose} className="h-7 w-7 text-white/35 hover:text-white rounded-full flex items-center justify-center border border-white/10 hover:border-white/25 transition-colors">✕</button>
              </div>
            </div>
          </CardHeader>
          <CardContent className="pt-5">
            {isLoading ? (
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-16" />)}
                </div>
                <Skeleton className="h-14" />
                <Skeleton className="h-14" />
              </div>
            ) : bot ? (
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { label: "Status", value: (
                      <div className="flex items-center gap-2">
                        {bot.status === "running"
                          ? <div className="relative w-2 h-2 signal-ring"><div className="w-2 h-2 rounded-full bg-green-400 shadow-[0_0_8px_rgba(74,222,128,0.8)]" /></div>
                          : bot.status === "error"
                          ? <div className="w-2 h-2 rounded-full bg-red-400 shadow-[0_0_6px_rgba(248,113,113,0.7)]" />
                          : <div className="w-2 h-2 rounded-full bg-white/20" />}
                        <span className={`capitalize ${bot.status === "running" ? "text-green-400/90" : bot.status === "error" ? "text-red-400/90" : ""}`}>{formatBotStatus(bot.status)}</span>
                      </div>
                    )},
                    { label: "Language", value: <span className="capitalize">{bot.language}</span> },
                    { label: "RAM",      value: `${bot.ramMb} MB` },
                    { label: "Storage",  value: `${bot.storageMb} MB` },
                  ].map(({ label, value }) => (
                    <div key={label} className="p-3 rounded-xl" style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)" }}>
                      <div className="text-[10px] text-white/35 uppercase tracking-widest mb-1.5 font-bold">{label}</div>
                      <div className="text-white font-bold text-sm">{value}</div>
                    </div>
                  ))}
                </div>
                <div className="p-3 rounded-xl" style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)" }}>
                  <div className="text-[10px] text-white/35 uppercase tracking-widest mb-1.5 font-bold">Source File</div>
                  <div className="text-white/75 font-mono text-xs truncate">{bot.fileName || "None"}</div>
                </div>
                <div className="p-3 rounded-xl" style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)" }}>
                  <div className="text-[10px] text-white/35 uppercase tracking-widest mb-1.5 font-bold">Provisioned</div>
                  <div className="text-white/75 text-sm">{format(new Date(bot.createdAt), "PPP p")}</div>
                </div>
                <BotLogsPanel botId={bot.id} />
              </div>
            ) : (
              <div className="text-center py-8 text-white/35">Slot not found</div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}

/* ── Bot card skeleton ── */
function BotCardSkeleton() {
  return (
    <Card className="glass-panel border-white/8">
      <CardHeader className="pb-3">
        <div className="flex justify-between mb-3">
          <Skeleton className="h-6 w-20 rounded-full" />
          <Skeleton className="h-8 w-8 rounded-full" />
        </div>
        <Skeleton className="h-5 w-32 rounded-lg" />
        <Skeleton className="h-4 w-24 rounded-lg mt-1" />
      </CardHeader>
      <CardContent className="pb-3 space-y-3">
        <Skeleton className="h-12 rounded-xl" />
        <Skeleton className="h-10 rounded-xl" />
      </CardContent>
    </Card>
  );
}

/* ── Dashboard ── */
export default function Dashboard() {
  const [, setLocation] = useLocation();
  const queryClient = useQueryClient();

  const { data: user, error: userError, isLoading: loadingUser } = useGetCurrentUser();
  const { data: bots, isLoading: loadingBots } = useListBots({ query: { refetchInterval: 3000 } as any });
  const { data: summary, isLoading: loadingSummary } = useGetBotSummary({ query: { refetchInterval: 3000 } as any });

  const logout    = useLogout();
  const createBot = useCreateBot();
  const startBot  = useStartBot();
  const stopBot   = useStopBot();
  const deleteBot = useDeleteBot();

  const [isDeploying, setIsDeploying]     = useState(false);
  const [newBotName, setNewBotName]       = useState("");
  const [newBotLanguage, setNewBotLanguage] = useState<BotInputLanguage>(BotInputLanguage.python);
  const [newBotRam, setNewBotRam]         = useState<BotInputRamMb>(BotInputRamMb.NUMBER_512);
  const [newBotStorage, setNewBotStorage] = useState<BotInputStorageMb>(BotInputStorageMb.NUMBER_1024);
  const [sourceCode, setSourceCode]       = useState("");
  const [detailsBotId, setDetailsBotId]   = useState<number | null>(null);
  const [uploadPhase, setUploadPhase]     = useState<UploadPhase>({ kind: "idle" });
  const uploadDoneRef = useRef<{ ok: boolean; error?: string } | null>(null);
  const [sortBy, setSortBy]               = useState<"name" | "status" | "created">("created");
  const [viewMode, setViewMode]           = useState<"expanded" | "compact">("expanded");
  const [isScrolled, setIsScrolled]       = useState(false);

  useEffect(() => {
    if (userError) setLocation("/login");
  }, [userError, setLocation]);

  // Sticky header shrink
  useEffect(() => {
    const onScroll = () => setIsScrolled(window.scrollY > 40);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Upload animation
  useEffect(() => {
    if (uploadPhase.kind !== "loading") return;
    const { steps, stepIdx } = uploadPhase;
    if (stepIdx < steps.length - 1) {
      const t = setTimeout(() => setUploadPhase(prev => prev.kind === "loading" ? { ...prev, stepIdx: prev.stepIdx + 1 } : prev), 650);
      return () => clearTimeout(t);
    }
    const t = setInterval(() => {
      const result = uploadDoneRef.current;
      if (!result) return;
      clearInterval(t);
      if (result.ok) {
        setUploadPhase({ kind: "success", fileName: uploadPhase.fileName });
        queryClient.invalidateQueries({ queryKey: getListBotsQueryKey() });
        queryClient.invalidateQueries({ queryKey: getGetBotSummaryQueryKey() });
      } else {
        setUploadPhase({ kind: "error", message: result.error ?? "Upload failed" });
      }
    }, 150);
    return () => clearInterval(t);
  }, [uploadPhase, queryClient]);

  const handleLogout = () => logout.mutate(undefined, { onSuccess: () => setLocation("/") });

  const handleAction = useCallback((id: number, action: "start" | "stop" | "delete") => {
    const opts = {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: getListBotsQueryKey() });
        queryClient.invalidateQueries({ queryKey: getGetBotSummaryQueryKey() });
        if (action === "start") toast.success("Bot started");
        if (action === "stop")  toast.success("Bot stopped");
        if (action === "delete") toast.success("Slot terminated");
      },
      onError: (err: any) => toast.error("Operation failed", { description: err.data?.error || "An error occurred" }),
    };
    if (action === "start")  startBot.mutate({ id }, opts);
    if (action === "stop")   stopBot.mutate({ id }, opts);
    if (action === "delete") {
      if (!window.confirm("Terminate this slot? This cannot be undone.")) return;
      deleteBot.mutate({ id }, opts);
    }
  }, [queryClient, startBot, stopBot, deleteBot]);

  const handleDeploy = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newBotName || !sourceCode.trim()) {
      toast.error("Missing information", { description: "Name and source code are required." });
      return;
    }
    createBot.mutate(
      { data: { name: newBotName, language: newBotLanguage, ramMb: newBotRam, storageMb: newBotStorage } },
      {
        onSuccess: async (createdBot: any) => {
          const savedLang = newBotLanguage;
          const savedCode = sourceCode;
          setIsDeploying(false);
          setNewBotName("");
          setSourceCode("");

          let detectedPackages: string[] = [];
          let uploadError: string | undefined;
          try {
            const res = await fetch(`${import.meta.env.BASE_URL}api/bots/${createdBot.id}/source`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              credentials: "include",
              body: JSON.stringify({ code: savedCode }),
            });
            if (!res.ok) {
              const body = await res.json().catch(() => ({})) as { error?: string };
              uploadError = body.error ?? "Save failed";
            } else {
              const body = await res.json().catch(() => ({})) as { detectedPackages?: string[] };
              detectedPackages = body.detectedPackages ?? [];
            }
          } catch (err: any) {
            uploadError = err?.message ?? "Save failed";
          }

          if (uploadError) { setUploadPhase({ kind: "error", message: uploadError }); return; }

          const steps = detectedPackages.length > 0 ? detectedPackages : (LANG_MODULES[savedLang] ?? LANG_MODULES.other!);
          const ext = LANG_OPTIONS.find(l => l.id === savedLang)?.ext ?? "txt";
          uploadDoneRef.current = { ok: true };
          setUploadPhase({ kind: "loading", fileName: `bot.${ext}`, steps, stepIdx: 0 });
        },
        onError: (err: unknown) => toast.error("Provisioning failed", { description: (err as any)?.data?.error || "Failed to create slot" }),
      }
    );
  };

  // Sort bots
  const sortedBots = [...(bots ?? [])].sort((a, b) => {
    if (sortBy === "name") return a.name.localeCompare(b.name);
    if (sortBy === "status") {
      const order = { running: 0, stopped: 1, error: 2 };
      return (order[a.status as keyof typeof order] ?? 3) - (order[b.status as keyof typeof order] ?? 3);
    }
    return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
  });

  const initials = getUserInitials(user?.email, user?.username);

  return (
    <div className="min-h-[100dvh] flex flex-col relative">
      <StarField />

      {/* Sticky nav */}
      <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[95%] max-w-7xl transition-all duration-300">
        <header
          className={`flex items-center justify-between rounded-full transition-all duration-300 ${
            isScrolled ? "h-11 px-5 shadow-[0_4px_30px_rgba(0,0,0,0.8)]" : "h-14 px-6"
          }`}
          style={{
            background: isScrolled ? "rgba(5,5,7,0.92)" : "rgba(255,255,255,0.04)",
            backdropFilter: "blur(20px)",
            border: "1px solid rgba(255,255,255,0.09)",
            boxShadow: isScrolled
              ? "0 4px 24px rgba(0,0,0,0.9)"
              : "0 4px 24px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.06)",
          }}
        >
          <div className="flex items-center gap-3">
            <Logo className="w-7 h-7 text-white" />
            <span className="text-sm font-bold text-white tracking-tight hidden md:inline-block">Client Portal</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-white/35 hidden sm:block font-mono truncate max-w-[180px]">{user?.email}</span>
            {/* Avatar dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-black hover:scale-105 transition-transform"
                  style={{ background: "rgba(255,255,255,0.88)", boxShadow: "0 0 12px rgba(255,255,255,0.2)" }}
                >
                  {initials}
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48" style={{ background: "rgba(10,10,14,0.96)", backdropFilter: "blur(20px)", border: "1px solid rgba(255,255,255,0.1)" }}>
                <div className="px-3 py-2 text-xs text-white/40 font-mono truncate">{user?.email}</div>
                <DropdownMenuSeparator style={{ background: "rgba(255,255,255,0.08)" }} />
                <DropdownMenuItem onClick={() => setIsDeploying(true)} className="text-white/70 hover:text-white focus:text-white focus:bg-white/8 cursor-pointer text-sm">
                  + Provision Slot
                </DropdownMenuItem>
                <DropdownMenuSeparator style={{ background: "rgba(255,255,255,0.08)" }} />
                <DropdownMenuItem onClick={handleLogout} className="text-red-400/80 hover:text-red-400 focus:text-red-400 focus:bg-red-400/8 cursor-pointer text-sm">
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>
      </div>

      <main className="flex-1 p-4 md:p-6 lg:p-12 max-w-7xl mx-auto w-full space-y-8 pt-24 md:pt-28 relative z-10">

        {/* STATS */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-5">
          {loadingSummary ? (
            [...Array(4)].map((_, i) => <Skeleton key={i} className="h-24 rounded-2xl" />)
          ) : (
            <>
              {[
                {
                  label: "Active Slots",
                  value: <AnimatedCounter value={summary?.runningBots} className="text-3xl md:text-4xl font-bold text-white" />,
                  sub: `/ ${summary?.totalBots ?? 0} total`,
                  glow: "rgba(74,222,128,0.08)",
                },
                {
                  label: "RAM Allocation",
                  value: <><AnimatedCounter value={summary?.totalRamMb} className="text-3xl md:text-4xl font-bold text-white" /><span className="text-sm text-white/30 ml-1">MB</span></>,
                  sub: null,
                  glow: "rgba(120,80,220,0.08)",
                },
                {
                  label: "Storage Provisioned",
                  value: <><AnimatedCounter value={summary?.totalStorageMb} className="text-3xl md:text-4xl font-bold text-white" /><span className="text-sm text-white/30 ml-1">MB</span></>,
                  sub: null,
                  glow: "rgba(80,160,255,0.08)",
                },
              ].map((item, i) => (
                <Card key={i} className="glass-panel card-hover" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
                  <CardHeader className="pb-1 pt-4 px-4">
                    <CardTitle className="text-[10px] text-white/35 font-bold uppercase tracking-widest">{item.label}</CardTitle>
                  </CardHeader>
                  <CardContent className="px-4 pb-4">
                    <div>{item.value}</div>
                    {item.sub && <div className="text-xs text-white/30 mt-0.5">{item.sub}</div>}
                  </CardContent>
                </Card>
              ))}
              {/* Provision button */}
              <Card
                className="glass-panel border-white/8 cursor-pointer group flex flex-col justify-center py-4 hover:border-white/25 card-hover transition-all"
                onClick={() => setIsDeploying(!isDeploying)}
              >
                <div className="text-center">
                  <div
                    className="w-10 h-10 mx-auto rounded-full flex items-center justify-center mb-2 group-hover:shadow-[0_0_20px_rgba(255,255,255,0.15)] transition-all"
                    style={{ border: "1px solid rgba(255,255,255,0.18)", background: "rgba(255,255,255,0.04)" }}
                  >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                  </div>
                  <div className="text-xs font-bold text-white/55 group-hover:text-white transition-colors">Provision Slot</div>
                </div>
              </Card>
            </>
          )}
        </div>

        {/* DEPLOY FORM */}
        <AnimatePresence>
          {isDeploying && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
            >
              <Card className="glass-panel overflow-hidden" style={{ borderColor: "rgba(255,255,255,0.1)" }}>
                <div className="absolute top-0 left-0 w-full h-px" style={{ background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)" }} />
                <CardHeader className="border-b border-white/8 pb-4">
                  <CardTitle className="text-xl text-white font-bold">Deploy Application</CardTitle>
                  <CardDescription className="text-white/35">Configure specs and upload source code</CardDescription>
                </CardHeader>
                <CardContent className="pt-5">
                  <form onSubmit={handleDeploy} className="space-y-7">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                      <div className="space-y-2">
                        <Label className="text-white/60 font-bold text-sm">Application Name</Label>
                        <Input className="input-3d h-11 px-4" value={newBotName} onChange={e => setNewBotName(e.target.value)} placeholder="Bot name" />
                      </div>

                      <div className="space-y-2 md:col-span-2">
                        <Label className="text-white/60 font-bold text-sm block mb-2">Runtime Environment</Label>
                        <div className="grid grid-cols-3 sm:grid-cols-5 gap-2 md:gap-3">
                          {LANG_OPTIONS.map(lang => (
                            <button
                              key={lang.id}
                              type="button"
                              onClick={() => setNewBotLanguage(lang.id)}
                              className={`relative flex flex-col items-center justify-center py-4 px-2 rounded-2xl border transition-all duration-200 group ${
                                newBotLanguage === lang.id
                                  ? "border-white/40 shadow-[0_0_20px_rgba(255,255,255,0.08)]"
                                  : "border-white/8 hover:border-white/20"
                              }`}
                              style={{
                                background: newBotLanguage === lang.id ? "rgba(255,255,255,0.08)" : "rgba(255,255,255,0.025)",
                                transform: newBotLanguage === lang.id ? "scale(1.03)" : undefined,
                              }}
                            >
                              <div
                                className="w-11 h-11 rounded-full mb-2.5 flex items-center justify-center transition-all group-hover:scale-105"
                                style={{
                                  border: "1px solid rgba(255,255,255,0.12)",
                                  background: "rgba(255,255,255,0.04)",
                                  boxShadow: newBotLanguage === lang.id ? "0 0 14px rgba(255,255,255,0.12)" : undefined,
                                }}
                              >
                                <lang.Icon size={22} color="rgba(255,255,255,0.8)" />
                              </div>
                              <span className="text-xs font-bold text-white/65">{lang.name}</span>
                              {newBotLanguage === lang.id && <div className="absolute top-2.5 right-2.5 w-1.5 h-1.5 rounded-full bg-white shadow-[0_0_8px_rgba(255,255,255,0.9)]" />}
                            </button>
                          ))}
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label className="text-white/60 font-bold text-sm">Dedicated RAM</Label>
                        <div className="relative">
                          <select className="flex h-11 w-full input-3d px-4 py-2 text-sm appearance-none font-medium" value={newBotRam} onChange={e => setNewBotRam(Number(e.target.value) as BotInputRamMb)}>
                            {[256,512,1024,2048,4096].map(v => <option key={v} value={v}>{v >= 1024 ? `${v} MB (${v/1024} GB)` : `${v} MB`}</option>)}
                          </select>
                          <div className="absolute inset-y-0 right-4 flex items-center pointer-events-none text-white/30">▾</div>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label className="text-white/60 font-bold text-sm">NVMe Storage</Label>
                        <div className="relative">
                          <select className="flex h-11 w-full input-3d px-4 py-2 text-sm appearance-none font-medium" value={newBotStorage} onChange={e => setNewBotStorage(Number(e.target.value) as BotInputStorageMb)}>
                            {[256,512,1024,2048,5120].map(v => <option key={v} value={v}>{v >= 1024 ? `${v} MB (${v/1024} GB)` : `${v} MB`}</option>)}
                          </select>
                          <div className="absolute inset-y-0 right-4 flex items-center pointer-events-none text-white/30">▾</div>
                        </div>
                      </div>

                      <div className="space-y-2 md:col-span-2">
                        <Label className="text-white/60 font-bold text-sm">Source Code</Label>
                        <CodeInput value={sourceCode} onChange={setSourceCode} height="260px" />
                        <p className="text-xs text-white/25">Dependencies are auto-detected from your imports.</p>
                      </div>
                    </div>

                    <div className="flex flex-wrap justify-end gap-3 pt-4 border-t border-white/8">
                      <button type="button" className="btn-3d px-6 py-2.5 text-sm" onClick={() => setIsDeploying(false)}>Cancel</button>
                      <button
                        type="submit"
                        className="btn-3d btn-3d-primary px-6 py-2.5 text-sm font-bold relative overflow-hidden"
                        disabled={createBot.isPending}
                      >
                        {createBot.isPending ? (
                          <span className="flex items-center gap-2">
                            <span className="w-4 h-4 rounded-full border-2 border-black/30 border-t-black/70 animate-spin" />
                            Provisioning...
                          </span>
                        ) : "Deploy Application"}
                      </button>
                    </div>
                  </form>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>

        {/* BOTS LIST */}
        <div className="space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-lg font-bold text-white tracking-tight">Hosted Applications</h2>
            <div className="flex items-center gap-2">
              {/* Sort */}
              <div className="flex items-center gap-1 text-xs">
                <span className="text-white/30 mr-1 hidden sm:inline">Sort:</span>
                {(["created","name","status"] as const).map(s => (
                  <button
                    key={s}
                    onClick={() => setSortBy(s)}
                    className={`px-2.5 py-1 rounded-lg capitalize transition-colors ${
                      sortBy === s ? "text-white bg-white/10 border border-white/20" : "text-white/35 hover:text-white/60"
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
              {/* View mode */}
              <button
                onClick={() => setViewMode(v => v === "expanded" ? "compact" : "expanded")}
                className="px-2.5 py-1 rounded-lg text-xs text-white/35 hover:text-white/60 border border-white/10 hover:border-white/25 transition-colors"
              >
                {viewMode === "expanded" ? "⊟ Compact" : "⊞ Expand"}
              </button>
            </div>
          </div>

          {loadingBots ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-5">
              {[...Array(3)].map((_, i) => <BotCardSkeleton key={i} />)}
            </div>
          ) : sortedBots.length === 0 ? (
            <div className="glass-panel rounded-2xl p-12 md:p-16 text-center" style={{ borderStyle: "dashed", borderColor: "rgba(255,255,255,0.08)" }}>
              <div
                className="w-16 h-16 rounded-3xl flex items-center justify-center mx-auto mb-5"
                style={{ border: "1px solid rgba(255,255,255,0.09)", background: "rgba(255,255,255,0.025)" }}
              >
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.25)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>
              </div>
              <h3 className="text-lg font-bold text-white mb-2">No Slots Provisioned</h3>
              <p className="text-white/30 text-sm mb-7 max-w-xs mx-auto">Deploy your first application to get started. It only takes a few seconds.</p>
              <button className="btn-3d btn-3d-primary px-8 py-3 font-bold" onClick={() => setIsDeploying(true)}>Deploy First App</button>
            </div>
          ) : (
            <motion.div
              layout
              className={`grid gap-4 md:gap-5 ${
                viewMode === "compact"
                  ? "grid-cols-1"
                  : "grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
              }`}
            >
              {sortedBots.map(bot => {
                const LangIcon = LANG_OPTIONS.find(l => l.id === bot.language)?.Icon || BsCodeSlash;
                const hasFile  = !!bot.fileName;
                const isRunning = bot.status === "running";
                const isError   = bot.status === "error";

                return (
                  <ContextMenu key={bot.id}>
                    <ContextMenuTrigger>
                      <motion.div layout transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Card
                              className={`relative overflow-hidden glass-panel card-hover ${
                                isRunning ? "bot-card-online" : isError ? "bot-card-error" : "border-white/8"
                              } ${viewMode === "compact" ? "!rounded-xl" : ""}`}
                            >
                              {/* Neon top line for online bots */}
                              {isRunning && (
                                <div className="absolute top-0 left-0 w-full h-px" style={{ background: "linear-gradient(90deg, transparent, rgba(74,222,128,0.7), transparent)", boxShadow: "0 0 8px rgba(74,222,128,0.5)" }} />
                              )}
                              {isError && (
                                <div className="absolute top-0 left-0 w-full h-px" style={{ background: "linear-gradient(90deg, transparent, rgba(248,113,113,0.7), transparent)", boxShadow: "0 0 8px rgba(248,113,113,0.5)" }} />
                              )}

                              {viewMode === "compact" ? (
                                /* Compact view */
                                <div className="flex items-center gap-4 px-4 py-3">
                                  <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0" style={{ border: "1px solid rgba(255,255,255,0.1)", background: "rgba(255,255,255,0.03)" }}>
                                    <LangIcon size={14} color="rgba(255,255,255,0.6)" />
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2">
                                      <span className="text-sm font-bold text-white truncate">{bot.name}</span>
                                      <StatusBadge status={bot.status} />
                                      <UptimeTimer createdAt={bot.createdAt} running={isRunning} />
                                    </div>
                                    <div className="text-xs text-white/30 font-mono mt-0.5">{bot.ramMb}MB RAM · {formatBytes(bot.fileSizeBytes)}</div>
                                  </div>
                                  <div className="flex items-center gap-1.5 shrink-0">
                                    {!isRunning
                                      ? <button className="btn-3d py-1.5 px-3 text-xs font-bold" onClick={() => handleAction(bot.id, "start")} disabled={!hasFile}>▶</button>
                                      : <button className="btn-3d py-1.5 px-3 text-xs" onClick={() => handleAction(bot.id, "stop")}>■</button>
                                    }
                                    <button className="btn-3d btn-3d-destructive py-1.5 px-2.5 text-xs" onClick={() => handleAction(bot.id, "delete")}>✕</button>
                                    <button className="text-xs text-white/25 hover:text-white/50 px-1 transition-colors" onClick={() => setDetailsBotId(bot.id)}>⋯</button>
                                  </div>
                                </div>
                              ) : (
                                /* Expanded view */
                                <>
                                  <CardHeader className="pb-3 pt-4 px-4">
                                    <div className="flex justify-between items-start mb-2">
                                      <StatusBadge status={bot.status} />
                                      <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ border: "1px solid rgba(255,255,255,0.1)", background: "rgba(255,255,255,0.03)" }}>
                                        <LangIcon size={14} color="rgba(255,255,255,0.6)" />
                                      </div>
                                    </div>
                                    <div className="flex items-center gap-2 flex-wrap">
                                      <CardTitle className="text-sm md:text-base text-white font-bold truncate max-w-[160px]">{bot.name}</CardTitle>
                                      <UptimeTimer createdAt={bot.createdAt} running={isRunning} />
                                    </div>
                                    <CardDescription className="text-xs text-white/30">
                                      {format(new Date(bot.createdAt), "MMM d, yyyy")}
                                    </CardDescription>
                                  </CardHeader>
                                  <CardContent className="pb-4 px-4">
                                    {/* Resource bar */}
                                    <div className="rounded-xl px-3 py-2.5 mb-3 space-y-2" style={{ background: "rgba(255,255,255,0.025)", border: "1px solid rgba(255,255,255,0.07)" }}>
                                      <div className="flex justify-between text-[10px] text-white/30 uppercase tracking-widest font-bold">
                                        <span>RAM {bot.ramMb} MB</span>
                                        <span>{formatBytes(bot.fileSizeBytes)}</span>
                                      </div>
                                      {/* Animated usage bar (display as allocated %) */}
                                      <div className="h-1 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.07)" }}>
                                        <div
                                          className="h-full rounded-full bar-fill"
                                          style={{
                                            width: `${Math.min(100, (bot.ramMb / 4096) * 100)}%`,
                                            background: isRunning
                                              ? "linear-gradient(90deg, rgba(74,222,128,0.8), rgba(120,220,160,0.6))"
                                              : "rgba(255,255,255,0.2)",
                                            boxShadow: isRunning ? "0 0 6px rgba(74,222,128,0.4)" : undefined,
                                          }}
                                        />
                                      </div>
                                    </div>

                                    {!hasFile && (
                                      <div className="text-xs px-3 py-2 rounded-lg flex items-center gap-2 mb-3" style={{ background: "rgba(255,180,50,0.06)", border: "1px solid rgba(255,180,50,0.15)", color: "rgba(255,200,80,0.8)" }}>
                                        <span>⚠</span> Upload a source file before starting
                                      </div>
                                    )}

                                    <div className="flex gap-2">
                                      {!isRunning ? (
                                        <button
                                          className="flex-1 btn-3d py-2.5 font-bold text-sm disabled:opacity-40 disabled:cursor-not-allowed"
                                          onClick={() => handleAction(bot.id, "start")}
                                          disabled={startBot.isPending || !hasFile}
                                        >
                                          {startBot.isPending ? "..." : "▶ Start"}
                                        </button>
                                      ) : (
                                        <button className="flex-1 btn-3d py-2.5 font-bold text-sm" onClick={() => handleAction(bot.id, "stop")} disabled={stopBot.isPending}>
                                          {stopBot.isPending ? "..." : "■ Stop"}
                                        </button>
                                      )}
                                      <button className="btn-3d btn-3d-destructive px-4 py-2.5" onClick={() => handleAction(bot.id, "delete")} disabled={deleteBot.isPending}>
                                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                                      </button>
                                    </div>

                                    <button className="w-full text-center text-[11px] text-white/18 hover:text-white/40 mt-2 py-1 transition-colors" onClick={() => setDetailsBotId(bot.id)}>
                                      View details →
                                    </button>
                                  </CardContent>
                                </>
                              )}
                            </Card>
                          </TooltipTrigger>
                          <TooltipContent
                            side="top"
                            className="max-w-[200px]"
                            style={{ background: "rgba(10,10,14,0.96)", backdropFilter: "blur(16px)", border: "1px solid rgba(255,255,255,0.1)", color: "rgba(255,255,255,0.85)" }}
                          >
                            <div className="space-y-1 text-xs">
                              <div className="font-bold">{bot.name}</div>
                              <div className="text-white/50">Lang: {bot.language} · RAM: {bot.ramMb}MB</div>
                              <div className="text-white/50">File: {bot.fileName || "none"}</div>
                              <div className="text-white/40">Created {format(new Date(bot.createdAt), "PPP")}</div>
                            </div>
                          </TooltipContent>
                        </Tooltip>
                      </motion.div>
                    </ContextMenuTrigger>
                    <ContextMenuContent style={{ background: "rgba(10,10,14,0.97)", backdropFilter: "blur(20px)", border: "1px solid rgba(255,255,255,0.1)" }}>
                      <ContextMenuItem onClick={() => setDetailsBotId(bot.id)} className="text-white/70 hover:text-white focus:text-white focus:bg-white/8 cursor-pointer text-sm gap-2">
                        ⋯ View Details
                      </ContextMenuItem>
                      <ContextMenuSeparator style={{ background: "rgba(255,255,255,0.08)" }} />
                      {!isRunning ? (
                        <ContextMenuItem onClick={() => handleAction(bot.id, "start")} disabled={!hasFile} className="text-green-400/80 hover:text-green-400 focus:text-green-400 focus:bg-green-400/8 cursor-pointer text-sm gap-2">
                          ▶ Start Bot
                        </ContextMenuItem>
                      ) : (
                        <ContextMenuItem onClick={() => handleAction(bot.id, "stop")} className="text-white/70 hover:text-white focus:text-white focus:bg-white/8 cursor-pointer text-sm gap-2">
                          ■ Stop Bot
                        </ContextMenuItem>
                      )}
                      <ContextMenuSeparator style={{ background: "rgba(255,255,255,0.08)" }} />
                      <ContextMenuItem onClick={() => handleAction(bot.id, "delete")} className="text-red-400/80 hover:text-red-400 focus:text-red-400 focus:bg-red-400/8 cursor-pointer text-sm gap-2">
                        ✕ Delete Slot
                      </ContextMenuItem>
                    </ContextMenuContent>
                  </ContextMenu>
                );
              })}
            </motion.div>
          )}
        </div>
      </main>

      {/* Upload overlay */}
      <AnimatePresence>
        {uploadPhase.kind !== "idle" && (
          <UploadOverlay phase={uploadPhase} onDismiss={() => setUploadPhase({ kind: "idle" })} />
        )}
      </AnimatePresence>

      {/* Details modal */}
      <AnimatePresence>
        {detailsBotId !== null && (
          <BotDetailsModal botId={detailsBotId} onClose={() => setDetailsBotId(null)} />
        )}
      </AnimatePresence>
    </div>
  );
}

/* ── Status badge ── */
function StatusBadge({ status }: { status: string }) {
  const isRunning = status === "running";
  const isError   = status === "error";

  return (
    <div
      className={`px-2.5 py-1 rounded-full text-xs font-bold tracking-wider uppercase flex items-center gap-1.5 border ${
        isRunning
          ? "border-green-400/30 text-green-400/90"
          : isError
          ? "border-red-400/30 text-red-400/90"
          : "border-white/10 text-white/35"
      }`}
      style={{
        background: isRunning ? "rgba(74,222,128,0.07)" : isError ? "rgba(248,113,113,0.07)" : "rgba(255,255,255,0.03)",
      }}
    >
      {isRunning ? (
        <div className="relative w-1.5 h-1.5 signal-ring">
          <div className="w-1.5 h-1.5 rounded-full bg-green-400 shadow-[0_0_6px_rgba(74,222,128,0.9)]" />
        </div>
      ) : isError ? (
        <div className="w-1.5 h-1.5 rounded-full bg-red-400 shadow-[0_0_6px_rgba(248,113,113,0.8)]" />
      ) : (
        <div className="w-1.5 h-1.5 rounded-full bg-white/20" />
      )}
      {formatBotStatus(status)}
    </div>
  );
}
