import { useEffect, useState, useRef } from "react";
import { useLocation } from "wouter";
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
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { format } from "date-fns";

function BotDetailsModal({ botId, onClose }: { botId: number; onClose: () => void }) {
  const { data: bot, isLoading } = useGetBot(botId);

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-6">
      <Card className="w-full max-w-md border-blue-500/30 shadow-[0_0_50px_rgba(59,130,246,0.2)] animate-in fade-in zoom-in-95 duration-200">
        <CardHeader className="pb-4">
          <div className="flex justify-between items-center mb-2">
            <CardTitle className="text-2xl text-white">Instance Details</CardTitle>
            <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8 text-white/50 hover:text-white rounded-full">
              <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12.8536 2.85355C13.0488 2.65829 13.0488 2.34171 12.8536 2.14645C12.6583 1.95118 12.3417 1.95118 12.1464 2.14645L7.5 6.79289L2.85355 2.14645C2.65829 1.95118 2.34171 1.95118 2.14645 2.14645C1.95118 2.34171 1.95118 2.65829 2.14645 2.85355L6.79289 7.5L2.14645 12.1464C1.95118 12.3417 1.95118 12.6583 2.14645 12.8536C2.34171 13.0488 2.65829 13.0488 2.85355 12.8536L7.5 8.20711L12.1464 12.8536C12.3417 13.0488 12.6583 13.0488 12.8536 12.8536C13.0488 12.6583 13.0488 12.3417 12.8536 12.1464L8.20711 7.5L12.8536 2.85355Z" fill="currentColor" fillRule="evenodd" clipRule="evenodd"></path></svg>
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-8 flex justify-center">
              <div className="w-8 h-8 rounded-full border-2 border-blue-500/20 border-t-blue-500 animate-spin"></div>
            </div>
          ) : bot ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white/5 p-3 rounded-lg border border-white/10">
                  <div className="text-xs text-blue-200/50 uppercase tracking-widest mb-1">Status</div>
                  <div className="text-white font-medium capitalize flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${bot.status === 'running' ? 'bg-green-400 shadow-[0_0_8px_#4ade80]' : 'bg-white/40'}`}></div>
                    {bot.status}
                  </div>
                </div>
                <div className="bg-white/5 p-3 rounded-lg border border-white/10">
                  <div className="text-xs text-blue-200/50 uppercase tracking-widest mb-1">Language</div>
                  <div className="text-white font-medium capitalize">{bot.language}</div>
                </div>
                <div className="bg-white/5 p-3 rounded-lg border border-white/10">
                  <div className="text-xs text-blue-200/50 uppercase tracking-widest mb-1">RAM</div>
                  <div className="text-white font-medium">{bot.ramMb} MB</div>
                </div>
                <div className="bg-white/5 p-3 rounded-lg border border-white/10">
                  <div className="text-xs text-blue-200/50 uppercase tracking-widest mb-1">Storage</div>
                  <div className="text-white font-medium">{bot.storageMb} MB</div>
                </div>
              </div>
              <div className="bg-white/5 p-3 rounded-lg border border-white/10">
                <div className="text-xs text-blue-200/50 uppercase tracking-widest mb-1">Source File</div>
                <div className="text-white font-mono text-sm truncate">{bot.fileName || "None"}</div>
              </div>
              <div className="bg-white/5 p-3 rounded-lg border border-white/10">
                <div className="text-xs text-blue-200/50 uppercase tracking-widest mb-1">Provisioned Date</div>
                <div className="text-white font-medium">{format(new Date(bot.createdAt), 'PPP p')}</div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-white/50">Slot not found</div>
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
      <header className="px-6 lg:px-12 h-20 flex items-center justify-between border-b border-white/5 bg-background/50 backdrop-blur-lg sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.6)] border border-blue-400 flex items-center justify-center">
            <div className="w-3 h-3 rounded-full bg-white shadow-[0_0_10px_white]"></div>
          </div>
          <span className="text-xl font-bold text-white tracking-tight hidden md:inline-block">Client Portal</span>
        </div>
        <div className="flex items-center gap-6">
          <div className="text-sm font-medium text-blue-100/70 hidden sm:block">
            {user?.email}
          </div>
          <Button variant="outline" size="sm" onClick={handleLogout}>Log out</Button>
        </div>
      </header>

      <main className="flex-1 p-6 lg:p-12 max-w-7xl mx-auto w-full space-y-10">
        
        {/* STATS */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs text-blue-200/50 uppercase tracking-widest">Active Slots</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-white">{summary?.runningBots} <span className="text-lg text-white/30 font-normal">/ {summary?.totalBots}</span></div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs text-blue-200/50 uppercase tracking-widest">RAM Allocation</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-white">{summary?.totalRamMb}<span className="text-lg text-white/30 font-normal ml-1">MB</span></div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xs text-blue-200/50 uppercase tracking-widest">Storage Provisioned</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-white">{summary?.totalStorageMb}<span className="text-lg text-white/30 font-normal ml-1">MB</span></div>
            </CardContent>
          </Card>
          <Card className="flex items-center justify-center bg-blue-600/10 border-blue-500/20 hover:bg-blue-600/20 transition-colors cursor-pointer group" onClick={() => setIsDeploying(!isDeploying)}>
            <div className="text-center">
              <div className="w-12 h-12 mx-auto rounded-full bg-blue-500/20 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                <div className="w-6 h-6 text-blue-400 text-2xl font-light leading-none flex items-center justify-center">+</div>
              </div>
              <div className="text-sm font-bold text-blue-100">Provision Slot</div>
            </div>
          </Card>
        </div>

        {/* DEPLOY FORM */}
        {isDeploying && (
          <Card className="border-blue-500/30 shadow-[0_0_30px_rgba(59,130,246,0.15)] relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-400 to-blue-600"></div>
            <CardHeader>
              <CardTitle className="text-2xl text-white">Deploy Application</CardTitle>
              <CardDescription>Configure infrastructure specs and upload source code</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleDeploy} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="botName">Application Name</Label>
                    <Input 
                      id="botName" 
                      value={newBotName}
                      onChange={e => setNewBotName(e.target.value)}
                      placeholder="e.g. prod-worker-1"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Runtime Environment</Label>
                    <select 
                      className="flex h-11 w-full input-3d px-3 py-2 text-sm appearance-none"
                      value={newBotLanguage}
                      onChange={e => setNewBotLanguage(e.target.value as BotInputLanguage)}
                    >
                      <option value={BotInputLanguage.python}>Python</option>
                      <option value={BotInputLanguage.javascript}>JavaScript</option>
                      <option value={BotInputLanguage.typescript}>TypeScript</option>
                      <option value={BotInputLanguage.java}>Java</option>
                      <option value={BotInputLanguage.other}>Other</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label>Dedicated RAM</Label>
                    <select 
                      className="flex h-11 w-full input-3d px-3 py-2 text-sm appearance-none"
                      value={newBotRam}
                      onChange={e => setNewBotRam(Number(e.target.value) as BotInputRamMb)}
                    >
                      <option value={BotInputRamMb.NUMBER_256}>256 MB</option>
                      <option value={BotInputRamMb.NUMBER_512}>512 MB</option>
                      <option value={BotInputRamMb.NUMBER_1024}>1024 MB (1 GB)</option>
                      <option value={BotInputRamMb.NUMBER_2048}>2048 MB (2 GB)</option>
                      <option value={BotInputRamMb.NUMBER_4096}>4096 MB (4 GB)</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label>NVMe Storage</Label>
                    <select 
                      className="flex h-11 w-full input-3d px-3 py-2 text-sm appearance-none"
                      value={newBotStorage}
                      onChange={e => setNewBotStorage(Number(e.target.value) as BotInputStorageMb)}
                    >
                      <option value={BotInputStorageMb.NUMBER_256}>256 MB</option>
                      <option value={BotInputStorageMb.NUMBER_512}>512 MB</option>
                      <option value={BotInputStorageMb.NUMBER_1024}>1024 MB (1 GB)</option>
                      <option value={BotInputStorageMb.NUMBER_2048}>2048 MB (2 GB)</option>
                      <option value={BotInputStorageMb.NUMBER_5120}>5120 MB (5 GB)</option>
                    </select>
                  </div>
                  <div className="space-y-2 md:col-span-2">
                    <Label>Source Code Package (.zip or single file)</Label>
                    <div className="relative border-2 border-dashed border-white/10 rounded-xl p-8 text-center hover:border-blue-500/50 transition-colors bg-white/5">
                      <input 
                        type="file" 
                        ref={fileInputRef}
                        onChange={e => setSelectedFile(e.target.files?.[0] || null)}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        required
                      />
                      <div className="flex flex-col items-center justify-center">
                        <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center mb-4">
                          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinelinejoin="round" className="text-blue-400"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
                        </div>
                        {selectedFile ? (
                          <div className="text-white font-medium">{selectedFile.name}</div>
                        ) : (
                          <>
                            <p className="text-white font-medium mb-1">Click to browse or drag and drop</p>
                            <p className="text-sm text-blue-200/50">Any valid source archive</p>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flex justify-end gap-3 pt-4 border-t border-white/10">
                  <Button type="button" variant="outline" onClick={() => setIsDeploying(false)}>Cancel</Button>
                  <Button type="submit" disabled={createBot.isPending || uploading}>
                    {createBot.isPending || uploading ? "Provisioning..." : "Deploy Application"}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* BOTS LIST */}
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-white tracking-tight">Hosted Applications</h2>
          
          {bots?.length === 0 ? (
            <div className="glass-panel rounded-xl p-12 text-center border-dashed border-white/20">
              <div className="w-16 h-16 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mx-auto mb-4">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinelinejoin="round" className="text-blue-400/50"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect><rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line></svg>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">No Slots Provisioned</h3>
              <p className="text-blue-200/60 mb-6 max-w-md mx-auto">You haven't deployed any applications yet. Provision a slot to get started with premium hosting.</p>
              <Button onClick={() => setIsDeploying(true)}>Deploy First App</Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {bots?.map(bot => (
                <Card key={bot.id} className="relative overflow-hidden group hover:border-blue-500/50 transition-colors cursor-pointer" onClick={() => setDetailsBotId(bot.id)}>
                  {bot.status === 'running' && (
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-green-400 to-green-600 shadow-[0_0_10px_#22c55e]"></div>
                  )}
                  <CardHeader className="pb-4 pointer-events-none">
                    <div className="flex justify-between items-start mb-2">
                      <div className={`px-2.5 py-1 rounded text-xs font-bold tracking-wider uppercase flex items-center gap-2 ${bot.status === 'running' ? 'bg-green-500/20 text-green-400' : 'bg-white/10 text-white/50'}`}>
                        <div className={`w-1.5 h-1.5 rounded-full ${bot.status === 'running' ? 'bg-green-400 shadow-[0_0_8px_#4ade80]' : 'bg-white/40'}`}></div>
                        {bot.status}
                      </div>
                      <div className="text-xs text-white/30 bg-white/5 px-2 py-1 rounded">{bot.language}</div>
                    </div>
                    <CardTitle className="text-xl truncate" title={bot.name}>{bot.name}</CardTitle>
                    <CardDescription className="text-xs">Deployed {format(new Date(bot.createdAt), 'MMM d, yyyy')}</CardDescription>
                  </CardHeader>
                  <CardContent className="pb-6 pointer-events-none">
                    <div className="flex items-center gap-6 mt-2">
                      <div className="flex flex-col">
                        <span className="text-xs text-blue-200/40 uppercase tracking-widest mb-1">RAM</span>
                        <span className="text-white font-medium">{bot.ramMb} MB</span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-xs text-blue-200/40 uppercase tracking-widest mb-1">Storage</span>
                        <span className="text-white font-medium">{bot.storageMb} MB</span>
                      </div>
                    </div>
                  </CardContent>
                  <div className="absolute bottom-0 left-0 w-full p-4 bg-white/5 border-t border-white/5 flex gap-2 translate-y-full group-hover:translate-y-0 transition-transform duration-200" onClick={e => e.stopPropagation()}>
                    {bot.status === 'stopped' ? (
                      <Button size="sm" className="flex-1 bg-green-600 hover:bg-green-500 border-green-400 shadow-[inset_0_1px_1px_rgba(255,255,255,0.3),0_4px_0_rgba(21,128,61,0.8)] active:shadow-[inset_0_1px_1px_rgba(255,255,255,0.2),0_2px_0_rgba(21,128,61,0.8)]" onClick={() => handleAction(bot.id, 'start')} disabled={startBot.isPending}>
                        Start Slot
                      </Button>
                    ) : (
                      <Button size="sm" className="flex-1 bg-amber-600 hover:bg-amber-500 border-amber-400 shadow-[inset_0_1px_1px_rgba(255,255,255,0.3),0_4px_0_rgba(180,83,9,0.8)] active:shadow-[inset_0_1px_1px_rgba(255,255,255,0.2),0_2px_0_rgba(180,83,9,0.8)]" onClick={() => handleAction(bot.id, 'stop')} disabled={stopBot.isPending}>
                        Halt
                      </Button>
                    )}
                    <Button size="sm" variant="destructive" className="px-3" onClick={() => handleAction(bot.id, 'delete')} disabled={deleteBot.isPending}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinelinejoin="round"><path d="M3 6h18"></path><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path></svg>
                    </Button>
                  </div>
                </Card>
              ))}
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
