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
                  { label: "Storage",  value: `${bot.storageMb} MB` },
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
  const { data: bots, isLoading: loadingBots } = useListBots();
  const { data: summary, isLoading: loadingSummary } = useGetBotSummary();

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
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
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
    if (!newBotName || !selectedFile) {
      toast({ title: "Missing Information", description: "Name and source file are required.", variant: "destructive" });
      return;
    }

    createBot.mutate(
      { data: { name: newBotName, language: newBotLanguage, ramMb: newBotRam, storageMb: newBotStorage } },
      {
        onSuccess: async (createdBot) => {
          const fileName = selectedFile.name;
          const steps = LANG_MODULES[newBotLanguage] ?? LANG_MODULES.other!;

          // Start animation
          uploadDoneRef.current = null;
          setUploadPhase({ kind: "loading", fileName, steps, stepIdx: 0 });
          setIsDeploying(false);
          setNewBotName("");
          setSelectedFile(null);
          if (fileInputRef.current) fileInputRef.current.value = "";

          // Upload in background
          const formData = new FormData();
          formData.append("file", selectedFile);
          try {
            const res = await fetch(`${import.meta.env.BASE_URL}api/bots/${createdBot.id}/upload`, {
              method: "POST",
              body: formData,
              credentials: "include",
            });
            if (!res.ok) {
              const body = await res.json().catch(() => ({})) as { error?: string };
              uploadDoneRef.current = { ok: false, error: body.error ?? "Upload failed" };
            } else {
              uploadDoneRef.current = { ok: true };
            }
          } catch (err: any) {
            uploadDoneRef.current = { ok: false, error: err?.message ?? "Upload failed" };
          }
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
                    <Label className="text-white/70 font-bold">Source Code Package</Label>
                    <div className="relative border-2 border-dashed border-white/12 rounded-2xl p-10 text-center hover:border-white/25 transition-colors bg-white/[0.02]">
                      <input
                        type="file"
                        ref={fileInputRef}
                        onChange={e => setSelectedFile(e.target.files?.[0] || null)}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        required
                      />
                      <div className="flex flex-col items-center justify-center pointer-events-none">
                        <div className="w-12 h-12 rounded-full border border-white/15 flex items-center justify-center mb-4 bg-white/4">
                          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.6)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
                        </div>
                        {selectedFile ? (
                          <div className="text-white font-bold bg-white/8 px-4 py-2 rounded-lg border border-white/12">{selectedFile.name}</div>
                        ) : (
                          <>
                            <p className="text-white/70 font-bold mb-1">Click to browse or drag & drop</p>
                            <p className="text-sm text-white/35">Any valid source archive (.zip, .py, .js, .ts)</p>
                          </>
                        )}
                      </div>
                    </div>
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
                return (
                  <Card
                    key={bot.id}
                    className="relative overflow-hidden group hover:border-white/25 transition-all cursor-pointer glass-panel hover:shadow-[0_8px_40px_rgba(255,255,255,0.06)]"
                    onClick={() => setDetailsBotId(bot.id)}
                  >
                    {bot.status === 'running' && (
                      <div className="absolute top-0 left-0 w-full h-px bg-white/60 shadow-[0_0_8px_rgba(255,255,255,0.8)]"></div>
                    )}
                    <CardHeader className="pb-4 pointer-events-none">
                      <div className="flex justify-between items-start mb-4">
                        <div className={`px-3 py-1 rounded-full text-xs font-bold tracking-wider uppercase flex items-center gap-2 border ${bot.status === 'running' ? 'border-white/25 text-white/90' : 'border-white/10 text-white/35'}`}>
                          <div className={`w-1.5 h-1.5 rounded-full ${bot.status === 'running' ? 'bg-white shadow-[0_0_6px_rgba(255,255,255,0.9)]' : 'bg-white/25'}`}></div>
                          {bot.status}
                        </div>
                        <div className="w-8 h-8 rounded-full border border-white/12 flex items-center justify-center bg-white/[0.03]">
                          <LangIcon size={15} color="rgba(255,255,255,0.6)" />
                        </div>
                      </div>
                      <CardTitle className="text-lg text-white font-bold truncate">{bot.name}</CardTitle>
                      <CardDescription className="text-xs text-white/35 font-medium">
                        Deployed {format(new Date(bot.createdAt), 'MMM d, yyyy')}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="pb-6 pointer-events-none border-b border-white/6">
                      <div className="flex items-center gap-8 mt-1 bg-white/[0.03] p-3 rounded-xl border border-white/8">
                        <div className="flex flex-col">
                          <span className="text-[10px] text-white/30 uppercase tracking-widest mb-1 font-bold">RAM</span>
                          <span className="text-white/80 font-bold text-sm">{bot.ramMb} MB</span>
                        </div>
                        <div className="flex flex-col">
                          <span className="text-[10px] text-white/30 uppercase tracking-widest mb-1 font-bold">Storage</span>
                          <span className="text-white/80 font-bold text-sm">{bot.storageMb} MB</span>
                        </div>
                      </div>
                    </CardContent>
                    <div
                      className="absolute bottom-0 left-0 w-full p-4 bg-black/80 backdrop-blur-md border-t border-white/8 flex gap-3 translate-y-full group-hover:translate-y-0 transition-transform duration-300"
                      onClick={e => e.stopPropagation()}
                    >
                      {bot.status === 'stopped' ? (
                        <button
                          className="flex-1 btn-3d py-2 font-bold text-sm text-white/80 hover:text-white"
                          onClick={() => handleAction(bot.id, 'start')}
                          disabled={startBot.isPending}
                        >
                          Start
                        </button>
                      ) : (
                        <button
                          className="flex-1 btn-3d py-2 font-bold text-sm text-white/70 hover:text-white"
                          onClick={() => handleAction(bot.id, 'stop')}
                          disabled={stopBot.isPending}
                        >
                          Halt
                        </button>
                      )}
                      <button
                        className="btn-3d btn-3d-destructive px-4"
                        onClick={() => handleAction(bot.id, 'delete')}
                        disabled={deleteBot.isPending}
                        aria-label="Delete"
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"></path><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path></svg>
                      </button>
                    </div>
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
