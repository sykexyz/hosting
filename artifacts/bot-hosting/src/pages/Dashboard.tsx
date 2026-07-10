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
  { id: BotInputLanguage.python, name: "Python", Icon: SiPython, color: "#3776AB" },
  { id: BotInputLanguage.javascript, name: "JavaScript", Icon: SiJavascript, color: "#F7DF1E" },
  { id: BotInputLanguage.typescript, name: "TypeScript", Icon: SiTypescript, color: "#3178C6" },
  { id: BotInputLanguage.java, name: "Java", Icon: FaJava, color: "#007396" },
  { id: BotInputLanguage.other, name: "Other", Icon: BsCodeSlash, color: "#64748B" }
];

function BotDetailsModal({ botId, onClose }: { botId: number; onClose: () => void }) {
  const { data: bot, isLoading } = useGetBot(botId);

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/20 backdrop-blur-sm p-6">
      <Card className="w-full max-w-md glass-panel border-white shadow-[0_8px_32px_rgba(0,0,0,0.1)] animate-in fade-in zoom-in-95 duration-200">
        <CardHeader className="pb-4 border-b border-white/50">
          <div className="flex justify-between items-center">
            <CardTitle className="text-2xl text-slate-800 font-bold">Instance Details</CardTitle>
            <button onClick={onClose} className="h-8 w-8 text-slate-500 hover:text-slate-800 rounded-full flex items-center justify-center bg-white/50 hover:bg-white transition-colors">
              <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12.8536 2.85355C13.0488 2.65829 13.0488 2.34171 12.8536 2.14645C12.6583 1.95118 12.3417 1.95118 12.1464 2.14645L7.5 6.79289L2.85355 2.14645C2.65829 1.95118 2.34171 1.95118 2.14645 2.14645C1.95118 2.34171 1.95118 2.65829 2.14645 2.85355L6.79289 7.5L2.14645 12.1464C1.95118 12.3417 1.95118 12.6583 2.14645 12.8536C2.34171 13.0488 2.65829 13.0488 2.85355 12.8536L7.5 8.20711L12.1464 12.8536C12.3417 13.0488 12.6583 13.0488 12.8536 12.8536C13.0488 12.6583 13.0488 12.3417 12.8536 12.1464L8.20711 7.5L12.8536 2.85355Z" fill="currentColor" fillRule="evenodd" clipRule="evenodd"></path></svg>
            </button>
          </div>
        </CardHeader>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="py-8 flex justify-center">
              <div className="w-8 h-8 rounded-full border-2 border-blue-500/20 border-t-blue-500 animate-spin"></div>
            </div>
          ) : bot ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white/60 p-4 rounded-xl border border-white shadow-sm">
                  <div className="text-xs text-slate-500 uppercase tracking-widest mb-1 font-bold">Status</div>
                  <div className="text-slate-800 font-bold capitalize flex items-center gap-2">
                    <div className={`w-2.5 h-2.5 rounded-full ${bot.status === 'running' ? 'bg-green-500 shadow-[0_0_8px_#22c55e]' : 'bg-slate-300'}`}></div>
                    {bot.status}
                  </div>
                </div>
                <div className="bg-white/60 p-4 rounded-xl border border-white shadow-sm">
                  <div className="text-xs text-slate-500 uppercase tracking-widest mb-1 font-bold">Language</div>
                  <div className="text-slate-800 font-bold capitalize">{bot.language}</div>
                </div>
                <div className="bg-white/60 p-4 rounded-xl border border-white shadow-sm">
                  <div className="text-xs text-slate-500 uppercase tracking-widest mb-1 font-bold">RAM</div>
                  <div className="text-slate-800 font-bold">{bot.ramMb} MB</div>
                </div>
                <div className="bg-white/60 p-4 rounded-xl border border-white shadow-sm">
                  <div className="text-xs text-slate-500 uppercase tracking-widest mb-1 font-bold">Storage</div>
                  <div className="text-slate-800 font-bold">{bot.storageMb} MB</div>
                </div>
              </div>
              <div className="bg-white/60 p-4 rounded-xl border border-white shadow-sm">
                <div className="text-xs text-slate-500 uppercase tracking-widest mb-1 font-bold">Source File</div>
                <div className="text-slate-800 font-mono text-sm truncate bg-white p-2 rounded-lg border border-slate-100">{bot.fileName || "None"}</div>
              </div>
              <div className="bg-white/60 p-4 rounded-xl border border-white shadow-sm">
                <div className="text-xs text-slate-500 uppercase tracking-widest mb-1 font-bold">Provisioned Date</div>
                <div className="text-slate-800 font-medium">{format(new Date(bot.createdAt), 'PPP p')}</div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-slate-500 font-medium">Slot not found</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function Dashboard() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: user, error: userError, isLoading: loadingUser } = useGetCurrentUser();
  const { data: bots, isLoading: loadingBots } = useListBots();
  const { data: summary, isLoading: loadingSummary } = useGetBotSummary();

  const logout = useLogout();
  const createBot = useCreateBot();
  const startBot = useStartBot();
  const stopBot = useStopBot();
  const deleteBot = useDeleteBot();

  const [isDeploying, setIsDeploying] = useState(false);
  const [newBotName, setNewBotName] = useState("");
  const [newBotLanguage, setNewBotLanguage] = useState<BotInputLanguage>(BotInputLanguage.python);
  const [newBotRam, setNewBotRam] = useState<BotInputRamMb>(BotInputRamMb.NUMBER_512);
  const [newBotStorage, setNewBotStorage] = useState<BotInputStorageMb>(BotInputStorageMb.NUMBER_1024);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [detailsBotId, setDetailsBotId] = useState<number | null>(null);

  useEffect(() => {
    if (userError) {
      setLocation("/login");
    }
  }, [userError, setLocation]);

  const handleLogout = () => {
    logout.mutate(undefined, {
      onSuccess: () => setLocation("/")
    });
  };

  const handleAction = (id: number, action: 'start' | 'stop' | 'delete') => {
    const opts = {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: getListBotsQueryKey() });
        queryClient.invalidateQueries({ queryKey: getGetBotSummaryQueryKey() });
      },
      onError: (err: any) => {
        toast({ title: "Operation failed", description: err.error || "An error occurred", variant: "destructive" });
      }
    };

    if (action === 'start') startBot.mutate({ id }, opts);
    if (action === 'stop') stopBot.mutate({ id }, opts);
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

    createBot.mutate({
      data: {
        name: newBotName,
        language: newBotLanguage,
        ramMb: newBotRam,
        storageMb: newBotStorage
      }
    }, {
      onSuccess: async (createdBot) => {
        setUploading(true);
        const formData = new FormData();
        formData.append("file", selectedFile);
        
        try {
          const res = await fetch(`${import.meta.env.BASE_URL}api/bots/${createdBot.id}/upload`, {
            method: 'POST',
            body: formData,
            credentials: 'include'
          });

          if (!res.ok) {
            const errBody = await res.json().catch(() => ({}));
            throw new Error(errBody.error || "Upload failed");
          }

          toast({ title: "Slot provisioned", description: "Application deployed successfully." });
          setIsDeploying(false);
          setNewBotName("");
          setSelectedFile(null);
          if (fileInputRef.current) fileInputRef.current.value = "";
          queryClient.invalidateQueries({ queryKey: getListBotsQueryKey() });
          queryClient.invalidateQueries({ queryKey: getGetBotSummaryQueryKey() });
        } catch (error: any) {
          toast({ title: "Upload failed", description: error.message, variant: "destructive" });
        } finally {
          setUploading(false);
        }
      },
      onError: (err) => {
        toast({ title: "Provisioning failed", description: err.error || "Failed to create slot", variant: "destructive" });
      }
    });
  };

  if (loadingUser || loadingBots || loadingSummary) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="w-12 h-12 rounded-full border-4 border-blue-500/20 border-t-blue-500 animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-[100dvh] flex flex-col relative">
      <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[95%] max-w-7xl">
        <header className="h-16 px-6 flex items-center justify-between glass-panel rounded-full shadow-[0_4px_20px_rgba(0,0,0,0.05)] border border-white/80">
          <div className="flex items-center gap-3">
            <Logo className="w-8 h-8 text-blue-600 drop-shadow-sm" />
            <span className="text-lg font-bold text-slate-800 tracking-tight hidden md:inline-block">Client Portal</span>
          </div>
          <div className="flex items-center gap-6">
            <div className="text-sm font-medium text-slate-500 hidden sm:block">
              {user?.email}
            </div>
            <button className="btn-3d text-sm h-9 px-5 inline-flex items-center justify-center rounded-full bg-white/40" onClick={handleLogout}>Log out</button>
          </div>
        </header>
      </div>

      <main className="flex-1 p-6 lg:p-12 max-w-7xl mx-auto w-full space-y-10 pt-28">
        
        {/* STATS */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="glass-panel border-white/80 shadow-sm bg-white/40">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs text-slate-500 font-bold uppercase tracking-widest">Active Slots</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-slate-800 drop-shadow-sm">{summary?.runningBots} <span className="text-lg text-slate-400 font-normal">/ {summary?.totalBots}</span></div>
            </CardContent>
          </Card>
          <Card className="glass-panel border-white/80 shadow-sm bg-white/40">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs text-slate-500 font-bold uppercase tracking-widest">RAM Allocation</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-slate-800 drop-shadow-sm">{summary?.totalRamMb}<span className="text-lg text-slate-400 font-normal ml-1">MB</span></div>
            </CardContent>
          </Card>
          <Card className="glass-panel border-white/80 shadow-sm bg-white/40">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs text-slate-500 font-bold uppercase tracking-widest">Storage Provisioned</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-slate-800 drop-shadow-sm">{summary?.totalStorageMb}<span className="text-lg text-slate-400 font-normal ml-1">MB</span></div>
            </CardContent>
          </Card>
          <Card className="glass-panel border-white/80 shadow-sm bg-blue-50/50 hover:bg-blue-100/50 transition-colors cursor-pointer group flex flex-col justify-center py-6" onClick={() => setIsDeploying(!isDeploying)}>
            <div className="text-center">
              <div className="w-12 h-12 mx-auto rounded-full bg-blue-600 shadow-md text-white flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
              </div>
              <div className="text-sm font-bold text-slate-700">Provision Slot</div>
            </div>
          </Card>
        </div>

        {/* DEPLOY FORM */}
        {isDeploying && (
          <Card className="glass-panel border-white shadow-lg overflow-hidden bg-white/60">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-400 to-purple-500"></div>
            <CardHeader className="border-b border-white/60 bg-white/30">
              <CardTitle className="text-2xl text-slate-800 font-bold">Deploy Application</CardTitle>
              <CardDescription className="text-slate-500 font-medium">Configure infrastructure specs and upload source code</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <form onSubmit={handleDeploy} className="space-y-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <Label htmlFor="botName" className="text-slate-700 font-bold">Application Name</Label>
                    <Input 
                      id="botName" 
                      className="input-3d"
                      value={newBotName}
                      onChange={e => setNewBotName(e.target.value)}
                      placeholder="e.g. prod-worker-1"
                    />
                  </div>

                  <div className="space-y-3 md:col-span-2">
                    <Label className="text-slate-700 font-bold mb-1 block">Runtime Environment</Label>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
                      {LANG_OPTIONS.map(lang => (
                        <button
                          key={lang.id}
                          type="button"
                          onClick={() => setNewBotLanguage(lang.id)}
                          className={`relative flex flex-col items-center justify-center py-5 px-2 rounded-2xl border transition-all duration-300 overflow-hidden ${
                            newBotLanguage === lang.id 
                              ? "bg-white/90 border-blue-400 shadow-[0_8px_16px_rgba(59,130,246,0.15)] scale-[1.02]" 
                              : "bg-white/40 border-white hover:bg-white/70 hover:shadow-md"
                          }`}
                        >
                          <div 
                            className="w-14 h-14 rounded-full mb-3 flex items-center justify-center border border-white"
                            style={{ 
                              background: `linear-gradient(135deg, white, ${lang.color}15)`,
                              boxShadow: `inset 0 2px 5px white, 0 4px 10px ${lang.color}20`
                            }}
                          >
                            <lang.Icon size={28} color={lang.color} style={{ filter: "drop-shadow(0 2px 3px rgba(0,0,0,0.15))" }} />
                          </div>
                          <span className="text-sm font-bold text-slate-700">{lang.name}</span>
                          
                          {newBotLanguage === lang.id && (
                            <div className="absolute top-3 right-3 w-2.5 h-2.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.8)]" />
                          )}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <Label className="text-slate-700 font-bold">Dedicated RAM</Label>
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
                      <div className="absolute inset-y-0 right-4 flex items-center pointer-events-none text-slate-400">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <Label className="text-slate-700 font-bold">NVMe Storage</Label>
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
                      <div className="absolute inset-y-0 right-4 flex items-center pointer-events-none text-slate-400">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-3 md:col-span-2">
                    <Label className="text-slate-700 font-bold">Source Code Package (.zip or single file)</Label>
                    <div className="relative border-2 border-dashed border-blue-200 rounded-2xl p-10 text-center hover:border-blue-400 transition-colors bg-white/50 shadow-inner">
                      <input 
                        type="file" 
                        ref={fileInputRef}
                        onChange={e => setSelectedFile(e.target.files?.[0] || null)}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        required
                      />
                      <div className="flex flex-col items-center justify-center">
                        <div className="w-14 h-14 rounded-full bg-blue-100 flex items-center justify-center mb-4 shadow-sm border border-white">
                          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-600"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
                        </div>
                        {selectedFile ? (
                          <div className="text-slate-800 font-bold bg-white px-4 py-2 rounded-lg shadow-sm border border-slate-100">{selectedFile.name}</div>
                        ) : (
                          <>
                            <p className="text-slate-800 font-bold mb-1">Click to browse or drag and drop</p>
                            <p className="text-sm text-slate-500 font-medium">Any valid source archive (.zip, .py, .js)</p>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flex justify-end gap-3 pt-6 border-t border-white/60">
                  <button type="button" className="btn-3d px-6 py-2" onClick={() => setIsDeploying(false)}>Cancel</button>
                  <button type="submit" className="btn-3d btn-3d-primary px-6 py-2 font-bold" disabled={createBot.isPending || uploading}>
                    {createBot.isPending || uploading ? "Provisioning..." : "Deploy Application"}
                  </button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* BOTS LIST */}
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-slate-800 tracking-tight drop-shadow-sm">Hosted Applications</h2>
          
          {bots?.length === 0 ? (
            <div className="glass-panel rounded-2xl p-16 text-center border-dashed border-white">
              <div className="w-20 h-20 rounded-3xl bg-blue-50 border border-white flex items-center justify-center mx-auto mb-6 shadow-sm">
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-400"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect><rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line></svg>
              </div>
              <h3 className="text-2xl font-bold text-slate-800 mb-3">No Slots Provisioned</h3>
              <p className="text-slate-500 font-medium mb-8 max-w-md mx-auto text-lg">You haven't deployed any applications yet. Provision a slot to get started with premium hosting.</p>
              <button className="btn-3d btn-3d-primary px-8 py-3 text-lg font-bold" onClick={() => setIsDeploying(true)}>Deploy First App</button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {bots?.map(bot => {
                const LangIcon = LANG_OPTIONS.find(l => l.id === bot.language)?.Icon || BsCodeSlash;
                const langColor = LANG_OPTIONS.find(l => l.id === bot.language)?.color || "#64748B";

                return (
                  <Card key={bot.id} className="relative overflow-hidden group hover:border-blue-300 transition-all cursor-pointer glass-panel bg-white/60 hover:bg-white/80 shadow-sm hover:shadow-md" onClick={() => setDetailsBotId(bot.id)}>
                    {bot.status === 'running' && (
                      <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-green-400 to-emerald-500 shadow-[0_0_10px_#34d399]"></div>
                    )}
                    <CardHeader className="pb-4 pointer-events-none">
                      <div className="flex justify-between items-start mb-4">
                        <div className={`px-3 py-1.5 rounded-full text-xs font-bold tracking-wider uppercase flex items-center gap-2 border ${bot.status === 'running' ? 'bg-green-50 text-green-700 border-green-200' : 'bg-slate-100 text-slate-500 border-slate-200'}`}>
                          <div className={`w-2 h-2 rounded-full ${bot.status === 'running' ? 'bg-green-500 shadow-[0_0_6px_#22c55e]' : 'bg-slate-400'}`}></div>
                          {bot.status}
                        </div>
                        <div className="w-8 h-8 rounded-full bg-white shadow-sm flex items-center justify-center border border-slate-100">
                          <LangIcon size={16} color={langColor} />
                        </div>
                      </div>
                      <CardTitle className="text-xl text-slate-800 font-bold truncate" title={bot.name}>{bot.name}</CardTitle>
                      <CardDescription className="text-xs text-slate-500 font-bold">Deployed {format(new Date(bot.createdAt), 'MMM d, yyyy')}</CardDescription>
                    </CardHeader>
                    <CardContent className="pb-6 pointer-events-none border-b border-slate-100/50">
                      <div className="flex items-center gap-8 mt-2 bg-white/50 p-3 rounded-xl border border-white">
                        <div className="flex flex-col">
                          <span className="text-[10px] text-slate-400 uppercase tracking-widest mb-1 font-bold">RAM</span>
                          <span className="text-slate-800 font-bold text-sm">{bot.ramMb} MB</span>
                        </div>
                        <div className="flex flex-col">
                          <span className="text-[10px] text-slate-400 uppercase tracking-widest mb-1 font-bold">Storage</span>
                          <span className="text-slate-800 font-bold text-sm">{bot.storageMb} MB</span>
                        </div>
                      </div>
                    </CardContent>
                    <div className="absolute bottom-0 left-0 w-full p-4 bg-white/80 backdrop-blur-md border-t border-white flex gap-3 translate-y-full group-hover:translate-y-0 transition-transform duration-300 shadow-[0_-4px_10px_rgba(0,0,0,0.02)]" onClick={e => e.stopPropagation()}>
                      {bot.status === 'stopped' ? (
                        <button className="flex-1 btn-3d bg-green-50 text-green-700 border-green-200 hover:bg-green-100 shadow-sm py-2 font-bold text-sm" onClick={() => handleAction(bot.id, 'start')} disabled={startBot.isPending}>
                          Start Slot
                        </button>
                      ) : (
                        <button className="flex-1 btn-3d bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100 shadow-sm py-2 font-bold text-sm" onClick={() => handleAction(bot.id, 'stop')} disabled={stopBot.isPending}>
                          Halt
                        </button>
                      )}
                      <button className="btn-3d btn-3d-destructive px-4 shadow-sm" onClick={() => handleAction(bot.id, 'delete')} disabled={deleteBot.isPending} aria-label="Delete">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"></path><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path></svg>
                      </button>
                    </div>
                  </Card>
                );
              })}
            </div>
          )}
        </div>

      </main>

      {detailsBotId && (
        <BotDetailsModal botId={detailsBotId} onClose={() => setDetailsBotId(null)} />
      )}
    </div>
  );
}
