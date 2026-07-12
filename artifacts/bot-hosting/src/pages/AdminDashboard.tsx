import { useEffect, useState } from "react";
import { useLocation } from "wouter";
import {
  useListAdminUsers,
  useListAdminBots,
  useListAdminLogs,
  useAdminLogout,
  useDeleteAdminBot,
  useViewAdminBotSource,
  getListAdminBotsQueryKey,
  getListAdminLogsQueryKey,
} from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StarField } from "../components/StarField";
import { Logo } from "../components/Logo";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { format } from "date-fns";
import { AnimatedCounter } from "../components/AnimatedCounter";

function formatBytes(bytes: number | null | undefined): string {
  if (bytes === null || bytes === undefined) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function Skeleton({ className }: { className?: string }) {
  return <div className={`skeleton ${className ?? ""}`} style={{}} />;
}

/* ── Source viewer modal ── */
function SourceViewerModal({ botId, botName, onClose }: { botId: number; botName: string; onClose: () => void }) {
  const { data, isLoading, error } = useViewAdminBotSource(botId);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!data?.content) return;
    try {
      await navigator.clipboard.writeText(data.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
      toast.success("Copied!", { description: "Source code copied to clipboard" });
    } catch {
      toast.error("Copy failed", { description: "Could not access the clipboard." });
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[200] flex items-center justify-center p-6"
      style={{ background: "rgba(0,0,0,0.8)", backdropFilter: "blur(16px)" }}
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95, y: 10 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.95, y: 10, opacity: 0 }}
        onClick={e => e.stopPropagation()}
        className="w-full max-w-3xl max-h-[85vh] flex flex-col rounded-xl overflow-hidden"
        style={{ background: "#070709", border: "1px solid rgba(255,255,255,0.1)", boxShadow: "0 0 80px rgba(0,0,0,0.9)" }}
      >
        <div className="flex items-center justify-between px-5 py-3 border-b border-white/8" style={{ background: "rgba(255,255,255,0.02)" }}>
          <div>
            <div className="text-sm font-bold text-white">{botName}</div>
            <div className="text-xs text-white/35 font-mono">{data?.fileName ?? (isLoading ? "loading…" : "")}</div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              disabled={!data?.content}
              className="px-3 py-1.5 rounded-lg text-xs font-bold transition-colors"
              style={{ background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.12)", color: "rgba(255,255,255,0.7)" }}
            >
              {copied ? "✓ Copied" : "Copy"}
            </button>
            <a
              href={`${import.meta.env.BASE_URL}api/admin/bots/${botId}/download`}
              className="px-3 py-1.5 rounded-lg text-xs font-bold transition-colors"
              style={{ background: "rgba(80,120,255,0.08)", border: "1px solid rgba(80,120,255,0.2)", color: "rgba(120,160,255,0.9)" }}
            >
              Download
            </a>
            <button
              onClick={onClose}
              className="px-3 py-1.5 rounded-lg text-xs font-bold text-white/50 hover:text-white transition-colors"
              style={{ border: "1px solid rgba(255,255,255,0.1)" }}
            >
              Close
            </button>
          </div>
        </div>
        <div className="flex-1 overflow-auto p-4 crt-overlay">
          {isLoading ? (
            <div className="space-y-2 p-2">
              {[...Array(8)].map((_, i) => <Skeleton key={i} className="h-4" />)}
            </div>
          ) : error ? (
            <div className="text-red-400/80 text-sm p-2">Could not load source — the file may be missing on disk.</div>
          ) : (
            <pre className="text-xs text-white/75 font-mono whitespace-pre-wrap break-words leading-relaxed">{data?.content}</pre>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}

/* ── Expandable bot row ── */
function BotRow({
  bot,
  onViewSource,
  onDelete,
}: {
  bot: any;
  onViewSource: (id: number, name: string) => void;
  onDelete: (id: number) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const isRunning = bot.status === "running";
  const isError   = bot.status === "error";

  return (
    <>
      <tr
        className="border-b border-white/5 cursor-pointer transition-colors hover:bg-white/[0.04] group"
        style={isRunning ? { background: "rgba(74,222,128,0.025)" } : isError ? { background: "rgba(248,113,113,0.02)" } : {}}
        onClick={() => setExpanded(v => !v)}
      >
        <td className="p-3 md:p-4">
          <div className="font-bold text-white/90 text-sm">{bot.name}</div>
          <div className="text-white/35 text-xs font-mono">{bot.language}</div>
        </td>
        <td className="p-3 md:p-4">
          <div className="text-white/65 text-sm">{bot.ownerUsername}</div>
        </td>
        <td className="p-3 md:p-4 hidden md:table-cell">
          <div className="text-white/55 text-xs">{bot.ramMb}MB RAM</div>
          <div className="text-white/30 text-xs">{formatBytes(bot.fileSizeBytes)}</div>
        </td>
        <td className="p-3 md:p-4">
          <span
            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border ${
              isRunning
                ? "border-green-400/30 text-green-400/90"
                : isError
                ? "border-red-400/30 text-red-400/90"
                : "border-white/10 text-white/40"
            }`}
            style={{
              background: isRunning ? "rgba(74,222,128,0.07)" : isError ? "rgba(248,113,113,0.07)" : "rgba(255,255,255,0.03)",
            }}
          >
            {isRunning && <div className="w-1.5 h-1.5 rounded-full bg-green-400 shadow-[0_0_6px_rgba(74,222,128,0.9)]" />}
            {isError   && <div className="w-1.5 h-1.5 rounded-full bg-red-400 shadow-[0_0_6px_rgba(248,113,113,0.8)]" />}
            {!isRunning && !isError && <div className="w-1.5 h-1.5 rounded-full bg-white/20" />}
            {bot.status.toUpperCase()}
          </span>
        </td>
        <td className="p-3 md:p-4 text-right">
          <div className="flex items-center justify-end gap-1.5" onClick={e => e.stopPropagation()}>
            {bot.hasFile && (
              <button
                onClick={() => onViewSource(bot.id, bot.name)}
                className="px-2.5 py-1.5 rounded-lg text-xs font-bold transition-colors"
                style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.12)", color: "rgba(255,255,255,0.6)" }}
              >
                VIEW
              </button>
            )}
            <button
              onClick={() => onDelete(bot.id)}
              className="px-2.5 py-1.5 rounded-lg text-xs font-bold transition-colors"
              style={{ background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.25)", color: "rgba(252,165,165,0.9)" }}
            >
              KILL
            </button>
            <button className="text-white/25 hover:text-white/60 px-1 transition-colors text-sm">{expanded ? "▲" : "▼"}</button>
          </div>
        </td>
      </tr>
      <AnimatePresence>
        {expanded && (
          <tr>
            <td colSpan={5} className="p-0">
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
                style={{ overflow: "hidden" }}
              >
                <div className="px-4 py-3 border-b border-white/5" style={{ background: "rgba(255,255,255,0.015)" }}>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                    {[
                      { label: "Slot ID",   value: `#${bot.id}` },
                      { label: "Storage",   value: `${bot.storageMb} MB` },
                      { label: "File",      value: bot.fileName ?? "None" },
                      { label: "Created",   value: format(new Date(bot.createdAt ?? Date.now()), "PPP") },
                    ].map(({ label, value }) => (
                      <div key={label} className="p-2 rounded-lg" style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)" }}>
                        <div className="text-white/30 uppercase tracking-widest text-[9px] font-bold mb-1">{label}</div>
                        <div className="text-white/75 font-mono truncate">{value}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            </td>
          </tr>
        )}
      </AnimatePresence>
    </>
  );
}

/* ── Admin Dashboard ── */
export default function AdminDashboard() {
  const [, setLocation] = useLocation();
  const queryClient = useQueryClient();

  const { data: users, error: usersError, isLoading: loadingUsers } = useListAdminUsers();
  const { data: bots, isLoading: loadingBots } = useListAdminBots({ query: { refetchInterval: 3000 } as any });
  const { data: logs, isLoading: loadingLogs } = useListAdminLogs({ query: { refetchInterval: 3000 } as any });

  const [viewingSource, setViewingSource] = useState<{ id: number; name: string } | null>(null);
  const [logSearch, setLogSearch] = useState("");
  const logout    = useAdminLogout();
  const deleteBot = useDeleteAdminBot();

  useEffect(() => {
    if (usersError && (usersError as any).status === 401) setLocation("/admin-login");
  }, [usersError, setLocation]);

  const handleLogout = () => logout.mutate(undefined, { onSuccess: () => setLocation("/admin-login") });

  const handleDeleteBot = (id: number) => {
    if (!window.confirm("Delete this slot and all data?")) return;
    deleteBot.mutate({ id }, {
      onSuccess: () => {
        toast.success("Slot terminated");
        queryClient.invalidateQueries({ queryKey: getListAdminBotsQueryKey() });
        queryClient.invalidateQueries({ queryKey: getListAdminLogsQueryKey() });
      },
      onError: (err: unknown) => toast.error("Error", { description: (err as any)?.data?.error || "Failed to delete slot" }),
    });
  };

  const runningCount = bots?.filter((b: any) => b.status === "running").length ?? 0;
  const totalRam     = bots?.reduce((s: number, b: any) => s + b.ramMb, 0) ?? 0;

  const getLogLevel = (msg: string): "err" | "warn" | "info" => {
    if (msg.includes("[ERR]") || msg.toLowerCase().includes("error")) return "err";
    if (msg.includes("[WARN]") || msg.toLowerCase().includes("warn")) return "warn";
    return "info";
  };
  const getLogColor = (level: "err" | "warn" | "info") => {
    if (level === "err")  return "text-red-400/85";
    if (level === "warn") return "text-yellow-400/75";
    return "text-white/60";
  };

  const filteredLogs = logs?.filter((l: any) =>
    !logSearch || l.message.toLowerCase().includes(logSearch.toLowerCase())
  );

  return (
    <div className="min-h-[100dvh] relative">
      <StarField />
      <div className="relative z-10 p-4 md:p-6 lg:p-8 max-w-7xl mx-auto">

        {/* Header */}
        <header className="flex items-center justify-between mb-6 md:mb-8 pb-5 border-b border-white/8">
          <div className="flex items-center gap-3 md:gap-4">
            <Logo className="w-7 h-7 text-white hidden md:block" />
            <div className="flex flex-col">
              {/* Breadcrumb */}
              <div className="flex items-center gap-2 text-xs text-white/30 mb-1">
                <span>1999 Bot Hosting</span>
                <span>/</span>
                <span className="text-white/60 font-bold">Admin</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-2.5 h-2.5 rounded-full bg-red-400 shadow-[0_0_8px_rgba(248,113,113,0.8)] animate-pulse" />
                <h1 className="text-lg md:text-xl font-bold text-white">Admin Dashboard</h1>
              </div>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="btn-3d text-xs px-4 py-2"
            style={{ borderColor: "rgba(255,255,255,0.12)", color: "rgba(255,255,255,0.55)" }}
          >
            Log out
          </button>
        </header>

        {/* Stats row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          {[
            { label: "Total Users",    value: loadingUsers ? "—" : <AnimatedCounter value={users?.length} className="text-2xl font-bold text-white" /> },
            { label: "Total Bots",     value: loadingBots  ? "—" : <AnimatedCounter value={bots?.length} className="text-2xl font-bold text-white" /> },
            { label: "Running",        value: loadingBots  ? "—" : <AnimatedCounter value={runningCount} className="text-2xl font-bold text-green-400/90" /> },
            { label: "RAM In Use",     value: loadingBots  ? "—" : <><AnimatedCounter value={totalRam} className="text-2xl font-bold text-white" /><span className="text-sm text-white/35 ml-1">MB</span></> },
          ].map(item => (
            <Card key={item.label} className="glass-panel" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
              <CardContent className="pt-4 pb-4 px-4">
                <div className="text-[10px] text-white/30 uppercase tracking-widest font-bold mb-1">{item.label}</div>
                <div>{item.value}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 md:gap-6">

          {/* USERS */}
          <Card className="glass-panel lg:col-span-1" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
            <CardHeader className="pb-0 px-4 pt-4 border-b border-white/7">
              <CardTitle className="text-xs tracking-widest text-white/35 uppercase pb-3">Registered Clients</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="max-h-[420px] overflow-y-auto">
                {loadingUsers ? (
                  <div className="p-4 space-y-2">{[...Array(4)].map((_, i) => <Skeleton key={i} className="h-12 rounded-xl" />)}</div>
                ) : (
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/5">
                        <th className="p-3 md:p-4 font-normal uppercase text-[10px] text-white/25 text-left tracking-widest">Client</th>
                        <th className="p-3 md:p-4 font-normal uppercase text-[10px] text-white/25 text-right tracking-widest">Slots</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users?.map((user: any) => (
                        <tr key={user.id} className="border-b border-white/5 hover:bg-white/[0.035] transition-colors group">
                          <td className="p-3 md:p-4">
                            <div className="flex items-center gap-2.5">
                              <div
                                className="w-7 h-7 rounded-full flex items-center justify-center text-[11px] font-bold text-black shrink-0"
                                style={{ background: "rgba(255,255,255,0.75)" }}
                              >
                                {user.username?.slice(0, 2).toUpperCase() ?? "??"}
                              </div>
                              <div>
                                <div className="font-bold text-white/85 text-sm">{user.username}</div>
                                <div className="text-white/35 text-[11px] truncate max-w-[140px]">{user.email}</div>
                              </div>
                            </div>
                          </td>
                          <td className="p-3 md:p-4 text-right">
                            <div
                              className="inline-flex items-center justify-center w-6 h-6 rounded-lg text-xs font-bold"
                              style={{ background: "rgba(255,255,255,0.08)", color: "rgba(255,255,255,0.7)" }}
                            >
                              {user.botCount}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </CardContent>
          </Card>

          {/* BOTS */}
          <Card className="glass-panel lg:col-span-2" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
            <CardHeader className="pb-0 px-4 pt-4 border-b border-white/7">
              <div className="flex items-center justify-between pb-3">
                <CardTitle className="text-xs tracking-widest text-white/35 uppercase">Active Slots</CardTitle>
                <div className="text-[11px] text-white/30">{bots?.length ?? 0} total</div>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="max-h-[420px] overflow-y-auto">
                {loadingBots ? (
                  <div className="p-4 space-y-2">{[...Array(5)].map((_, i) => <Skeleton key={i} className="h-14 rounded-xl" />)}</div>
                ) : bots?.length === 0 ? (
                  <div className="p-8 text-center text-white/30 text-sm">No bots deployed yet.</div>
                ) : (
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/5">
                        {["Slot / App", "Owner", "Specs", "Status", "Actions"].map((h, i) => (
                          <th key={h} className={`p-3 md:p-4 font-normal uppercase text-[10px] text-white/25 tracking-widest ${i === 4 ? "text-right" : "text-left"} ${i === 2 ? "hidden md:table-cell" : ""}`}>{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {bots?.map((bot: any) => (
                        <BotRow
                          key={bot.id}
                          bot={bot}
                          onViewSource={(id, name) => setViewingSource({ id, name })}
                          onDelete={handleDeleteBot}
                        />
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </CardContent>
          </Card>

          {/* LOGS */}
          <Card className="glass-panel lg:col-span-3" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
            <CardHeader className="pb-0 px-4 pt-4 border-b border-white/7">
              <div className="flex items-center justify-between pb-3">
                <CardTitle className="text-xs tracking-widest text-white/35 uppercase">Activity Logs</CardTitle>
                <input
                  type="text"
                  value={logSearch}
                  onChange={e => setLogSearch(e.target.value)}
                  placeholder="Search logs..."
                  className="bg-transparent text-white/55 text-xs font-mono outline-none placeholder:text-white/20 border-b border-white/10 focus:border-white/30 pb-0.5 w-40 transition-colors"
                />
              </div>
            </CardHeader>
            <CardContent className="p-3 md:p-4">
              <div className="h-[260px] overflow-y-auto font-mono text-xs space-y-1 crt-overlay rounded-lg p-2" style={{ background: "rgba(0,0,0,0.35)" }}>
                {loadingLogs ? (
                  <div className="space-y-1.5 p-1">{[...Array(6)].map((_, i) => <Skeleton key={i} className="h-4" />)}</div>
                ) : !filteredLogs?.length ? (
                  <div className="text-white/25 p-2">{logSearch ? "No matching logs." : "No activity logs yet."}</div>
                ) : (
                  filteredLogs.map((log: any) => {
                    const level = getLogLevel(log.message);
                    return (
                      <div key={log.id} className="flex gap-3 group leading-relaxed">
                        <span className="text-white/22 shrink-0">{format(new Date(log.createdAt), "HH:mm:ss.SSS")}</span>
                        <span className={`${getLogColor(level)} group-hover:text-white/80 transition-colors break-all`}>{log.message}</span>
                      </div>
                    );
                  })
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Source viewer */}
      <AnimatePresence>
        {viewingSource && (
          <SourceViewerModal
            botId={viewingSource.id}
            botName={viewingSource.name}
            onClose={() => setViewingSource(null)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
