import { useEffect, useState, useRef } from "react";
import { useLocation } from "wouter";
import { Logo } from "../components/Logo";
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
  BotInputStorageMb
} from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { format } from "date-fns";
import { SiPython, SiJavascript, SiTypescript } from "react-icons/si";
import { FaJava } from "react-icons/fa";
import { BsCodeSlash } from "react-icons/bs";

const LANG_OPTIONS = [
  { id: BotInputLanguage.python,     name: "Python",     Icon: SiPython,     color: "#ffffff" },
  { id: BotInputLanguage.javascript, name: "JavaScript", Icon: SiJavascript, color: "#ffffff" },
  { id: BotInputLanguage.typescript, name: "TypeScript", Icon: SiTypescript, color: "#ffffff" },
  { id: BotInputLanguage.java,       name: "Java",       Icon: FaJava,       color: "#ffffff" },
  { id: BotInputLanguage.other,      name: "Other",      Icon: BsCodeSlash,  color: "#ffffff" }
];

const LANG_MODULES: Record<string, string[]> = {
  python:     ["runtime.cpython", "asyncio", "threading", "json", "os", "pathlib"],
  javascript: ["node:events", "node:fs", "node:path", "node:http", "node:stream"],
  typescript: ["ts-node/register", "node:fs", "typescript/lib", "@types/node", "node:path"],
  java:       ["java.io", "java.util", "java.net", "java.lang", "java.nio"],
  other:      ["core.runtime", "io.module", "net.module", "sys.module", "util.module"],
};

function formatBytes(bytes: number | null | undefined): string {
  if (bytes === null || bytes === undefined) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

/* ── Upload animation overlay ── */
type UploadPhase =
  | { kind: "idle" }
  | { kind: "loading"; fileName: string; steps: string[]; stepIdx: number }
  | { kind: "success"; fileName: string }
  | { kind: "error"; message: string };

function UploadOverlay({ phase, onDismiss }: { phase: Exclude<UploadPhase, { kind: "idle" }>; onDismiss: () => void }) {
  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center bg-black/80 backdrop-blur-sm p-6">
      <div
        className="w-full max-w-lg rounded-xl border border-white/10 bg-black/90 shadow-[0_0_60px_rgba(255,255,255,0.08)] overflow-hidden"
        style={{ fontFamily: "'Spline Sans Mono', monospace" }}
      >
        {/* Terminal title bar */}
        <div className="flex items-center gap-2 px-4 py-3 border-b border-white/8 bg-white/[0.03]">
          <div className="w-2.5 h-2.5 rounded-full bg-white/20"></div>
          <div className="w-2.5 h-2.5 rounded-full bg-white/15"></div>
          <div className="w-2.5 h-2.5 rounded-full bg-white/10"></div>
          <span className="ml-3 text-xs text-white/30 tracking-widest uppercase">system — hosting-daemon</span>
        </div>

        {/* Terminal body */}
        <div className="p-6 min-h-[220px] flex flex-col gap-2">
          {phase.kind === "loading" && (
            <>
              <p className="text-white/50 text-xs mb-3">&gt; Checking module dependencies...</p>
              {phase.steps.map((step, i) => {
                const done = i < phase.stepIdx;
                const active = i === phase.stepIdx;
                if (i > phase.stepIdx) return null;
                return (
                  <div key={step} className="flex items-center gap-3 text-sm">
                    {done ? (
                      <span className="text-white/70">✓</span>
                    ) : active ? (
                      <span className="text-white/40 animate-spin inline-block">⟳</span>
                    ) : null}
                    <span className={done ? "text-white/60" : active ? "text-white/90" : "text-white/30"}>
                      {active ? (
                        <>downloading <span className="text-white font-bold">{step}</span>
                          <span
                            className="inline-block ml-1 text-white/70"
                            style={{ animation: "terminal-blink 1s step-end infinite" }}
                          >▌</span>
                        </>
                      ) : (
                        <>downloaded <span className="text-white/80">{step}</span></>
                      )}
                    </span>
                  </div>
                );
              })}
            </>
          )}

          {phase.kind === "success" && (
            <div className="flex flex-col items-center justify-center py-8 gap-4 text-center">
              <div className="text-5xl mb-2" style={{ filter: "drop-shadow(0 0 20px rgba(255,255,255,0.6))" }}>✓</div>
              <p className="text-white text-lg font-bold tracking-wide">Successfully hosted</p>
              <p className="text-white/50 text-sm font-mono bg-white/5 border border-white/10 px-4 py-2 rounded-lg">{phase.fileName}</p>
              <button
                onClick={onDismiss}
                className="mt-4 px-6 py-2 rounded-lg border border-white/20 text-white/70 text-sm hover:border-white/40 hover:text-white transition-colors"
              >
                Close
              </button>
            </div>
          )}

          {phase.kind === "error" && (
            <div className="flex flex-col items-center justify-center py-8 gap-4 text-center">
              <div className="text-4xl text-red-400 mb-2">✗</div>
              <p className="text-red-300 text-base font-bold">Upload failed</p>
              <p className="text-white/40 text-sm">{phase.message}</p>
              <button
                onClick={onDismiss}
                className="mt-4 px-6 py-2 rounded-lg border border-red-400/30 text-red-300/80 text-sm hover:border-red-400/60 transition-colors"
              >
                Close
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ── Live logs viewer (real stdout/stderr/lifecycle output for this bot) ── */
function BotLogsPanel({ botId }: { botId: number }) {
  const { data: logs, isLoading } = useListBotLogs(botId, { query: { refetchInterval: 3000 } as any });
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ block: "end" });
  }, [logs]);

  return (
    <div className="bg-black/60 border border-white/8 rounded-xl overflow-hidden">
      <div className="px-4 py-2 border-b border-white/8 text-xs text-white/40 uppercase tracking-widest font-bold">
        Live Console
      </div>
      <div className="p-3 max-h-56 overflow-y-auto font-mono text-xs space-y-1" style={{ fontFamily: "'Spline Sans Mono', monospace" }}>
        {isLoading ? (
          <div className="text-white/30">Loading logs...</div>
        ) : !logs || logs.length === 0 ? (
          <div className="text-white/30">No output yet. Start the bot to see real console output here.</div>
        ) : (
          logs.map((log) => {
            const isErr = log.message.includes(" ERR]");
            return (
              <div key={log.id} className={isErr ? "text-red-300/90" : "text-white/70"}>
                <span className="text-white/25">{format(new Date(log.createdAt), "HH:mm:ss")}</span>{" "}
                {log.message}
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

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm p-6">
      <Card className="w-full max-w-md glass-panel shadow-[0_8px_60px_rgba(255,255,255,0.07)] animate-in fade-in zoom-in-95 duration-200">
        <CardHeader className="pb-4 border-b border-white/10">
          <div className="flex justify-between items-center">
            <CardTitle className="text-2xl text-white font-bold">Instance Details</CardTitle>
            <button
              onClick={onClose}
              className="h-8 w-8 text-white/40 hover:text-white rounded-full flex items-center justify-center border border-white/10 hover:border-white/30 transition-colors"
            >
              <svg width="14" height="14" viewBox="0 0 15 15" fill="none"><path d="M12.8536 2.85355C13.0488 2.65829 13.0488 2.34171 12.8536 2.14645C12.6583 1.95118 12.3417 1.95118 12.1464 2.14645L7.5 6.79289L2.85355 2.14645C2.65829 1.95118 2.34171 1.95118 2.14645 2.14645C1.95118 2.34171 1.95118 2.65829 2.14645 2.85355L6.79289 7.5L2.14645 12.1464C1.95118 12.3417 1.95118 12.6583 2.14645 12.8536C2.34171 13.0488 2.65829 13.0488 2.85355 12.8536L7.5 8.20711L12.1464 12.8536C12.3417 13.0488 12.6583 13.0488 12.8536 12.8536C13.0488 12.6583 13.0488 12.3417 12.8536 12.1464L8.20711 7.5L12.8536 2.85355Z" fill="currentColor" fillRule="evenodd" clipRule="evenodd"></path></svg>
            </button>
          </div>
        </CardHeader>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="py-8 flex justify-center">
              <div className="w-8 h-8 rounded-full border-2 border-white/10 border-t-white/70 animate-spin"></div>
            </div>
          ) : bot ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                {[
                  { label: "Status", value: (
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${bot.status === 'running' ? 'bg-white shadow-[0_0_8px_rgba(255,255,255,0.8)]' : 'bg-white/20'}`}></div>
                      <span className="capitalize">{bot.status}</span>
                    </div>
                  )},
                  { label: "Language", value: <span className="capitalize">{bot.language}</span> },
                  { label: "RAM",      value: `${bot.ramMb} MB` },
                  { label: "Storage Plan",  value: `${bot.storageMb} MB` },
                  { label: "Source Size",  value: formatBytes(bot.fileSizeBytes) },
                ].map(({ label, value }) => (
                  <div key={label} className="bg-white/4 p-4 rounded-xl border border-white/8">
                    <div className="text-xs text-white/40 uppercase tracking-widest mb-2 font-bold">{label}</div>
                    <div className="text-white font-bold">{value}</div>
                  </div>
                ))}
              </div>
              <div className="bg-white/4 p-4 rounded-xl border border-white/8">
                <div className="text-xs text-white/40 uppercase tracking-widest mb-2 font-bold">Source File</div>
                <div className="text-white/80 font-mono text-sm truncate bg-black/40 p-2 rounded-lg border border-white/8">{bot.fileName || "None"}</div>
              </div>
              <div className="bg-white/4 p-4 rounded-xl border border-white/8">
                <div className="text-xs text-white/40 uppercase tracking-widest mb-2 font-bold">Provisioned</div>
                <div className="text-white/80 font-medium">{format(new Date(bot.createdAt), 'PPP p')}</div>
              </div>
              <BotLogsPanel botId={bot.id} />
            </div>
          ) : (
            <div className="text-center py-8 text-white/40 font-medium">Slot not found</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/* ── Dashboard ── */
export default function Dashboard() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: user, error: userError, isLoading: loadingUser } = useGetCurrentUser();
  // Poll so status/specs reflect real process state (e.g. a bot crashing) without a manual refresh.
  const { data: bots, isLoading: loadingBots } = useListBots({ query: { refetchInterval: 3000 } as any });
  const { data: summary, isLoading: loadingSummary } = useGetBotSummary({ query: { refetchInterval: 3000 } as any });

  const logout   = useLogout();
  const createBot = useCreateBot();
  const startBot  = useStartBot();
  const stopBot   = useStopBot();
  const deleteBot = useDeleteBot();

  const [isDeploying, setIsDeploying] = useState(false);
  const [newBotName, setNewBotName] = useState("");
  const [newBotLanguage, setNewBotLanguage] = useState<BotInputLanguage>(BotInputLanguage.python);
  const [newBotRam, setNewBotRam] = useState<BotInputRamMb>(BotInputRamMb.NUMBER_512);
  const [newBotStorage, setNewBotStorage] = useState<BotInputStorageMb>(BotInputStorageMb.NUMBER_1024);
  const [sourceCode, setSourceCode] = useState("");
  const [detailsBotId, setDetailsBotId] = useState<number | null>(null);

  // Upload animation state
  const [uploadPhase, setUploadPhase] = useState<UploadPhase>({ kind: "idle" });
  const uploadDoneRef = useRef<{ ok: boolean; error?: string } | null>(null);

  useEffect(() => {
    if (userError) setLocation("/login");
  }, [userError, setLocation]);

  // Animate steps one by one; when all steps done, check if upload also resolved
  useEffect(() => {
    if (uploadPhase.kind !== "loading") return;
    const { steps, stepIdx } = uploadPhase;

    if (stepIdx < steps.length - 1) {
      const t = setTimeout(() => {
        setUploadPhase(prev =>
          prev.kind === "loading" ? { ...prev, stepIdx: prev.stepIdx + 1 } : prev
        );
      }, 650);
      return () => clearTimeout(t);
    }

    // All steps done — wait for actual upload to finish
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

  const handleLogout = () => {
    logout.mutate(undefined, { onSuccess: () => setLocation("/") });
  };

  const handleAction = (id: number, action: 'start' | 'stop' | 'delete') => {
    const opts = {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: getListBotsQueryKey() });
        queryClient.invalidateQueries({ queryKey: getGetBotSummaryQueryKey() });
      },
      onError: (err: any) => {
        toast({ title: "Operation failed", description: err.data?.error || "An error occurred", variant: "destructive" });
      }
    };
    if (action === 'start') startBot.mutate({ id }, opts);
    if (action === 'stop')  stopBot.mutate({ id }, opts);
    if (action === 'delete') {
      if (window.confirm("Terminate this slot? This cannot be undone.")) {
        deleteBot.mutate({ id }, opts);
      }
    }
  };

  const handleDeploy = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newBotName || !sourceCode.trim()) {
      toast({ title: "Missing Information", description: "Name and source code are required.", variant: "destructive" });
      return;
    }

    createBot.mutate(
      { data: { name: newBotName, language: newBotLanguage, ramMb: newBotRam, storageMb: newBotStorage } },
      {
        onSuccess: async (createdBot) => {
          const savedLang = newBotLanguage;
          const savedCode = sourceCode;
          setIsDeploying(false);
          setNewBotName("");
          setSourceCode("");

          // Save source code to server
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

          if (uploadError) {
            setUploadPhase({ kind: "error", message: uploadError });
            return;
          }

          // Animate real packages (or fallback defaults if source has no imports)
          const steps = detectedPackages.length > 0
            ? detectedPackages
            : (LANG_MODULES[savedLang] ?? LANG_MODULES.other!);

          uploadDoneRef.current = { ok: true };
          setUploadPhase({ kind: "loading", fileName: `bot.${savedLang === "python" ? "py" : savedLang === "javascript" ? "js" : savedLang === "typescript" ? "ts" : savedLang === "java" ? "java" : "txt"}`, steps, stepIdx: 0 });
        },
        onError: (err) => {
          toast({ title: "Provisioning failed", description: err.data?.error || "Failed to create slot", variant: "destructive" });
        }
      }
    );
  };

  if (loadingUser || loadingBots || loadingSummary) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="w-12 h-12 rounded-full border-2 border-white/10 border-t-white/60 animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-[100dvh] flex flex-col relative">
      {/* Top nav */}
      <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[95%] max-w-7xl">
        <header className="h-14 px-6 flex items-center justify-between glass-panel rounded-full shadow-[0_4px_30px_rgba(255,255,255,0.04)] border border-white/10">
          <div className="flex items-center gap-3">
            <Logo className="w-7 h-7 text-white drop-shadow-sm" />
            <span className="text-base font-bold text-white tracking-tight hidden md:inline-block">Client Portal</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-sm text-white/40 hidden sm:block font-mono">{user?.email}</div>
            <button
              className="btn-3d text-sm h-9 px-5"
              onClick={handleLogout}
            >
              Log out
            </button>
          </div>
        </header>
      </div>

      <main className="flex-1 p-6 lg:p-12 max-w-7xl mx-auto w-full space-y-10 pt-28">

        {/* STATS */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
          {[
            {
              label: "Active Slots",
              value: (
                <span className="text-4xl font-bold text-white">
                  {summary?.runningBots} <span className="text-lg text-white/30 font-normal">/ {summary?.totalBots}</span>
                </span>
              ),
            },
            {
              label: "RAM Allocation",
              value: (
                <span className="text-4xl font-bold text-white">
                  {summary?.totalRamMb}<span className="text-lg text-white/30 font-normal ml-1">MB</span>
                </span>
              ),
            },
            {
              label: "Storage Provisioned",
              value: (
                <span className="text-4xl font-bold text-white">
                  {summary?.totalStorageMb}<span className="text-lg text-white/30 font-normal ml-1">MB</span>
                </span>
              ),
            },
            {
              label: null,
              value: null,
              isAction: true,
            },
          ].map((item, i) =>
            item.isAction ? (
              <Card
                key={i}
                className="glass-panel border-white/10 cursor-pointer group flex flex-col justify-center py-6 hover:border-white/30 transition-all"
                onClick={() => setIsDeploying(!isDeploying)}
              >
                <div className="text-center">
                  <div className="w-11 h-11 mx-auto rounded-full border border-white/20 text-white flex items-center justify-center mb-3 group-hover:border-white/60 group-hover:shadow-[0_0_20px_rgba(255,255,255,0.12)] transition-all">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                  </div>
                  <div className="text-sm font-bold text-white/70 group-hover:text-white transition-colors">Provision Slot</div>
                </div>
              </Card>
            ) : (
              <Card key={i} className="glass-panel border-white/10">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs text-white/40 font-bold uppercase tracking-widest">{item.label}</CardTitle>
                </CardHeader>
                <CardContent>{item.value}</CardContent>
              </Card>
            )
          )}
        </div>

        {/* DEPLOY FORM */}
        {isDeploying && (
          <Card className="glass-panel border-white/12 shadow-[0_8px_60px_rgba(255,255,255,0.05)] overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-white/30 to-transparent"></div>
            <CardHeader className="border-b border-white/8">
              <CardTitle className="text-2xl text-white font-bold">Deploy Application</CardTitle>
              <CardDescription className="text-white/40 font-medium">Configure specs and upload source code</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <form onSubmit={handleDeploy} className="space-y-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <Label htmlFor="botName" className="text-white/70 font-bold">Application Name</Label>
                    <Input
                      id="botName"
                      className="input-3d h-11 px-4"
                      value={newBotName}
                      onChange={e => setNewBotName(e.target.value)}
                      placeholder="e.g. prod-worker-1"
                    />
                  </div>

                  <div className="space-y-3 md:col-span-2">
                    <Label className="text-white/70 font-bold mb-1 block">Runtime Environment</Label>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
                      {LANG_OPTIONS.map(lang => (
                        <button
                          key={lang.id}
                          type="button"
                          onClick={() => setNewBotLanguage(lang.id)}
                          className={`relative flex flex-col items-center justify-center py-5 px-2 rounded-2xl border transition-all duration-200 ${
                            newBotLanguage === lang.id
                              ? "border-white/50 bg-white/10 shadow-[0_0_20px_rgba(255,255,255,0.1)] scale-[1.02]"
                              : "border-white/10 bg-white/[0.03] hover:bg-white/6 hover:border-white/25"
                          }`}
                        >
                          <div className="w-12 h-12 rounded-full mb-3 flex items-center justify-center border border-white/15 bg-white/5">
                            <lang.Icon size={24} color="rgba(255,255,255,0.85)" />
                          </div>
                          <span className="text-sm font-bold text-white/75">{lang.name}</span>
                          {newBotLanguage === lang.id && (
                            <div className="absolute top-3 right-3 w-2 h-2 rounded-full bg-white shadow-[0_0_8px_rgba(255,255,255,0.9)]" />
                          )}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <Label className="text-white/70 font-bold">Dedicated RAM</Label>
                    <div className="relative">
                      <select
                        className="flex h-11 w-full input-3d px-4 py-2 text-sm appearance-none font-medium"
                        value={newBotRam}
                        onChange={e => setNewBotRam(Number(e.target.value) as BotInputRamMb)}
                      >
                        <option value={BotInputRamMb.NUMBER_256}>256 MB</option>
                        <option value={BotInputRamMb.NUMBER_512}>512 MB</option>
                        <option value={BotInputRamMb.NUMBER_1024}>1024 MB (1 GB)</option>
                        <option value={BotInputRamMb.NUMBER_2048}>2048 MB (2 GB)</option>
                        <option value={BotInputRamMb.NUMBER_4096}>4096 MB (4 GB)</option>
                      </select>
                      <div className="absolute inset-y-0 right-4 flex items-center pointer-events-none text-white/30">▾</div>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <Label className="text-white/70 font-bold">NVMe Storage</Label>
                    <div className="relative">
                      <select
                        className="flex h-11 w-full input-3d px-4 py-2 text-sm appearance-none font-medium"
                        value={newBotStorage}
                        onChange={e => setNewBotStorage(Number(e.target.value) as BotInputStorageMb)}
                      >
                        <option value={BotInputStorageMb.NUMBER_256}>256 MB</option>
                        <option value={BotInputStorageMb.NUMBER_512}>512 MB</option>
                        <option value={BotInputStorageMb.NUMBER_1024}>1024 MB (1 GB)</option>
                        <option value={BotInputStorageMb.NUMBER_2048}>2048 MB (2 GB)</option>
                        <option value={BotInputStorageMb.NUMBER_5120}>5120 MB (5 GB)</option>
                      </select>
                      <div className="absolute inset-y-0 right-4 flex items-center pointer-events-none text-white/30">▾</div>
                    </div>
                  </div>

                  <div className="space-y-3 md:col-span-2">
                    <Label className="text-white/70 font-bold">Source Code</Label>
                    <div className="relative rounded-xl border border-white/12 bg-black/40 overflow-hidden focus-within:border-white/30 transition-colors">
                      {/* Fake terminal header */}
                      <div className="flex items-center gap-1.5 px-4 py-2 border-b border-white/8 bg-white/[0.02]">
                        <div className="w-2 h-2 rounded-full bg-white/15" />
                        <div className="w-2 h-2 rounded-full bg-white/10" />
                        <div className="w-2 h-2 rounded-full bg-white/8" />
                        <span className="ml-2 text-[10px] text-white/25 font-mono tracking-widest uppercase">
                          {newBotLanguage === "python" ? "bot.py" : newBotLanguage === "javascript" ? "bot.js" : newBotLanguage === "typescript" ? "bot.ts" : newBotLanguage === "java" ? "Bot.java" : "bot.txt"}
                        </span>
                      </div>
                      <textarea
                        className="w-full bg-transparent text-white/80 font-mono text-sm px-4 py-3 resize-none outline-none placeholder:text-white/20 min-h-[220px]"
                        placeholder={newBotLanguage === "python"
                          ? "import discord\n\nclient = discord.Client()\n\n@client.event\nasync def on_ready():\n    print('Bot is online!')\n\nclient.run('YOUR_TOKEN')"
                          : newBotLanguage === "javascript"
                          ? "const { Client } = require('discord.js');\nconst client = new Client({ intents: [] });\n\nclient.once('ready', () => console.log('Online!'));\nclient.login('YOUR_TOKEN');"
                          : "// Paste your bot source code here"}
                        value={sourceCode}
                        onChange={e => setSourceCode(e.target.value)}
                        spellCheck={false}
                        autoCorrect="off"
                        autoCapitalize="off"
                      />
                      <div className="absolute bottom-2 right-3 text-[10px] text-white/20 font-mono pointer-events-none">
                        {sourceCode.split("\n").length} lines
                      </div>
                    </div>
                    <p className="text-xs text-white/30">Paste your bot code above. Dependencies are auto-detected from your imports.</p>
                  </div>
                </div>

                <div className="flex justify-end gap-3 pt-6 border-t border-white/8">
                  <button type="button" className="btn-3d px-6 py-2 text-sm" onClick={() => setIsDeploying(false)}>Cancel</button>
                  <button type="submit" className="btn-3d btn-3d-primary px-6 py-2 text-sm font-bold" disabled={createBot.isPending}>
                    {createBot.isPending ? "Provisioning..." : "Deploy Application"}
                  </button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* BOTS LIST */}
        <div className="space-y-6">
          <h2 className="text-xl font-bold text-white tracking-tight">Hosted Applications</h2>

          {bots?.length === 0 ? (
            <div className="glass-panel rounded-2xl p-16 text-center border-dashed border-white/10">
              <div className="w-16 h-16 rounded-3xl border border-white/10 flex items-center justify-center mx-auto mb-6 bg-white/[0.03]">
                <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.3)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect><rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line></svg>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">No Slots Provisioned</h3>
              <p className="text-white/40 font-medium mb-8 max-w-md mx-auto">Provision a slot to get started.</p>
              <button className="btn-3d btn-3d-primary px-8 py-3 font-bold" onClick={() => setIsDeploying(true)}>Deploy First App</button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {bots?.map(bot => {
                const LangIcon = LANG_OPTIONS.find(l => l.id === bot.language)?.Icon || BsCodeSlash;
                const hasFile = !!bot.fileName;
                const isRunning = bot.status === 'running';
                return (
                  <Card
                    key={bot.id}
                    className={`relative overflow-hidden transition-all glass-panel ${isRunning ? 'border-white/30 shadow-[0_0_24px_rgba(255,255,255,0.07)]' : 'border-white/10'}`}
                  >
                    {/* Running pulse line */}
                    {isRunning && (
                      <div className="absolute top-0 left-0 w-full h-px bg-white/60 shadow-[0_0_8px_rgba(255,255,255,0.8)]" />
                    )}

                    <CardHeader className="pb-3">
                      <div className="flex justify-between items-start mb-3">
                        {/* Status badge */}
                        <div className={`px-2.5 py-1 rounded-full text-xs font-bold tracking-wider uppercase flex items-center gap-1.5 border ${isRunning ? 'border-white/25 text-white/90 bg-white/5' : 'border-white/10 text-white/35'}`}>
                          <div className={`w-1.5 h-1.5 rounded-full ${isRunning ? 'bg-white shadow-[0_0_6px_rgba(255,255,255,0.9)]' : 'bg-white/25'}`} />
                          {bot.status}
                        </div>
                        <div className="w-8 h-8 rounded-full border border-white/12 flex items-center justify-center bg-white/[0.03]">
                          <LangIcon size={15} color="rgba(255,255,255,0.6)" />
                        </div>
                      </div>
                      <CardTitle className="text-base text-white font-bold truncate">{bot.name}</CardTitle>
                      <CardDescription className="text-xs text-white/35">
                        {format(new Date(bot.createdAt), 'MMM d, yyyy')}
                      </CardDescription>
                    </CardHeader>

                    <CardContent className="pb-3">
                      {/* Resource row */}
                      <div className="flex items-center gap-6 bg-white/[0.03] px-3 py-2.5 rounded-xl border border-white/8 mb-4">
                        <div>
                          <div className="text-[9px] text-white/30 uppercase tracking-widest font-bold mb-0.5">RAM</div>
                          <div className="text-white/80 font-bold text-sm">{bot.ramMb} MB</div>
                        </div>
                        <div>
                          <div className="text-[9px] text-white/30 uppercase tracking-widest font-bold mb-0.5">Src Size</div>
                          <div className="text-white/80 font-bold text-sm">{formatBytes(bot.fileSizeBytes)}</div>
                        </div>
                        <div className="ml-auto">
                          <div className="text-[9px] text-white/30 uppercase tracking-widest font-bold mb-0.5">File</div>
                          <div className={`text-xs font-mono truncate max-w-[90px] ${hasFile ? 'text-white/70' : 'text-white/25 italic'}`}>
                            {hasFile ? bot.fileName : 'none'}
                          </div>
                        </div>
                      </div>

                      {/* No file warning */}
                      {!hasFile && (
                        <div className="text-xs text-amber-400/70 bg-amber-400/5 border border-amber-400/15 rounded-lg px-3 py-2 mb-3 flex items-center gap-2">
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                          Upload a source file before starting
                        </div>
                      )}

                      {/* Action buttons — always visible */}
                      <div className="flex gap-2">
                        {!isRunning ? (
                          <button
                            className="flex-1 btn-3d py-2.5 font-bold text-sm disabled:opacity-40 disabled:cursor-not-allowed"
                            onClick={() => handleAction(bot.id, 'start')}
                            disabled={startBot.isPending || !hasFile}
                            title={!hasFile ? 'Upload a file first' : 'Start bot'}
                          >
                            {startBot.isPending ? '...' : '▶ Start'}
                          </button>
                        ) : (
                          <button
                            className="flex-1 btn-3d py-2.5 font-bold text-sm text-white/70 hover:text-white disabled:opacity-40"
                            onClick={() => handleAction(bot.id, 'stop')}
                            disabled={stopBot.isPending}
                          >
                            {stopBot.isPending ? '...' : '■ Stop'}
                          </button>
                        )}
                        <button
                          className="btn-3d btn-3d-destructive px-4 py-2.5"
                          onClick={() => handleAction(bot.id, 'delete')}
                          disabled={deleteBot.isPending}
                          title="Delete bot"
                        >
                          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                        </button>
                      </div>

                      {/* Info link */}
                      <button
                        className="w-full text-center text-xs text-white/20 hover:text-white/40 mt-2 py-1 transition-colors"
                        onClick={() => setDetailsBotId(bot.id)}
                      >
                        View details
                      </button>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </div>
      </main>

      {/* Upload animation overlay */}
      {uploadPhase.kind !== "idle" && (
        <UploadOverlay
          phase={uploadPhase}
          onDismiss={() => setUploadPhase({ kind: "idle" })}
        />
      )}

      {/* Bot details modal */}
      {detailsBotId !== null && (
        <BotDetailsModal botId={detailsBotId} onClose={() => setDetailsBotId(null)} />
      )}
    </div>
  );
}
