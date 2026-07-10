import { useEffect } from "react";
import { useLocation } from "wouter";
import { 
  useListAdminUsers, 
  useListAdminBots, 
  useListAdminLogs,
  useAdminLogout,
  useDeleteAdminBot,
  getListAdminBotsQueryKey,
  getListAdminLogsQueryKey
} from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { format } from "date-fns";

export default function AdminDashboard() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: users, error: usersError, isLoading: loadingUsers } = useListAdminUsers();
  const { data: bots, isLoading: loadingBots } = useListAdminBots();
  const { data: logs, isLoading: loadingLogs } = useListAdminLogs();
  
  const logout = useAdminLogout();
  const deleteBot = useDeleteAdminBot();

  useEffect(() => {
    if (usersError && (usersError as any).status === 401) {
      setLocation("/admin-login");
    }
  }, [usersError, setLocation]);

  const handleLogout = () => {
    logout.mutate(undefined, {
      onSuccess: () => {
        setLocation("/admin-login");
      }
    });
  };

  const handleDeleteBot = (id: number) => {
    if (!window.confirm("Are you sure you want to delete this slot and all data?")) return;
    deleteBot.mutate({ id }, {
      onSuccess: () => {
        toast({ title: "Slot Terminated", description: "The application slot has been removed." });
        queryClient.invalidateQueries({ queryKey: getListAdminBotsQueryKey() });
        queryClient.invalidateQueries({ queryKey: getListAdminLogsQueryKey() });
      },
      onError: (err) => {
        toast({ title: "Error", description: err.data?.error || "Failed to delete slot", variant: "destructive" });
      }
    });
  };

  if (loadingUsers || loadingBots || loadingLogs) {
    return <div className="min-h-screen flex items-center justify-center text-white/50">Loading...</div>;
  }

  return (
    <div className="min-h-[100dvh] bg-[#050505] text-white p-6 lg:p-10">
      <header className="flex items-center justify-between mb-10 border-b border-white/10 pb-6">
        <div className="flex items-center gap-4">
          <div className="w-3 h-3 bg-cyan-400 rounded-full shadow-[0_0_10px_rgba(34,211,238,0.8)] animate-pulse"></div>
          <h1 className="text-xl font-bold text-white">Admin Dashboard</h1>
        </div>
        <Button variant="outline" size="sm" onClick={handleLogout} className="border-white/10 hover:bg-white/5 text-xs tracking-wider">
          Log out
        </Button>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* USERS */}
        <Card className="!bg-black/50 !border-white/5 shadow-2xl rounded-none col-span-1">
          <CardHeader className="border-b border-white/5">
            <CardTitle className="text-sm tracking-widest text-white/50 uppercase">Registered Clients</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="max-h-[400px] overflow-y-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/5 text-white/30 text-left">
                    <th className="p-4 font-normal uppercase text-xs">Client</th>
                    <th className="p-4 font-normal uppercase text-xs text-right">Slots</th>
                  </tr>
                </thead>
                <tbody>
                  {users?.map(user => (
                    <tr key={user.id} className="border-b border-white/5 hover:bg-white/5">
                      <td className="p-4">
                        <div className="font-bold text-white/90">{user.username}</div>
                        <div className="text-white/40 text-xs">{user.email}</div>
                      </td>
                      <td className="p-4 text-right">
                        <div className="inline-flex items-center justify-center w-6 h-6 rounded bg-white/10 text-xs font-bold">
                          {user.botCount}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* BOTS */}
        <Card className="!bg-black/50 !border-white/5 shadow-2xl rounded-none col-span-1 lg:col-span-2">
          <CardHeader className="border-b border-white/5 flex flex-row items-center justify-between">
            <CardTitle className="text-sm tracking-widest text-white/50 uppercase">Active Slots</CardTitle>
            <div className="text-xs text-white/40">{bots?.length || 0} Total</div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="max-h-[400px] overflow-y-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/5 text-white/30 text-left">
                    <th className="p-4 font-normal uppercase text-xs">Slot ID / App</th>
                    <th className="p-4 font-normal uppercase text-xs">Owner</th>
                    <th className="p-4 font-normal uppercase text-xs">Specs</th>
                    <th className="p-4 font-normal uppercase text-xs">Status</th>
                    <th className="p-4 font-normal uppercase text-xs text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {bots?.map(bot => (
                    <tr key={bot.id} className="border-b border-white/5 hover:bg-white/5">
                      <td className="p-4">
                        <div className="font-bold text-white/90">{bot.name}</div>
                        <div className="text-white/40 text-xs">{bot.language}</div>
                      </td>
                      <td className="p-4">
                        <div className="text-white/70">{bot.ownerUsername}</div>
                      </td>
                      <td className="p-4 text-white/60 text-xs">
                        {bot.ramMb}MB / {bot.storageMb}MB
                      </td>
                      <td className="p-4">
                        <span className={`inline-flex items-center gap-2 px-2 py-1 rounded-sm text-xs font-medium ${bot.status === 'running' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-white/5 text-white/50 border border-white/10'}`}>
                          {bot.status === 'running' && <div className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_5px_#22c55e]"></div>}
                          {bot.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="p-4 text-right space-x-2">
                        {bot.hasFile && (
                          <a 
                            href={`${import.meta.env.BASE_URL}api/admin/bots/${bot.id}/download`} 
                            className="inline-flex items-center justify-center px-3 py-1.5 rounded-sm bg-blue-900/30 text-blue-400 border border-blue-500/30 hover:bg-blue-900/60 text-xs transition-colors"
                          >
                            DL
                          </a>
                        )}
                        <button 
                          onClick={() => handleDeleteBot(bot.id)}
                          className="inline-flex items-center justify-center px-3 py-1.5 rounded-sm bg-red-900/30 text-red-400 border border-red-500/30 hover:bg-red-900/60 text-xs transition-colors"
                        >
                          KILL
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* LOGS */}
        <Card className="!bg-black/50 !border-white/5 shadow-2xl rounded-none col-span-1 lg:col-span-3">
          <CardHeader className="border-b border-white/5">
            <CardTitle className="text-sm tracking-widest text-white/50 uppercase">System Logs</CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <div className="h-[300px] overflow-y-auto font-mono text-xs space-y-2">
              {logs?.map(log => (
                <div key={log.id} className="flex gap-4 group">
                  <span className="text-white/30 shrink-0">{format(new Date(log.createdAt), "HH:mm:ss.SSS")}</span>
                  <span className="text-white/70 group-hover:text-white">{log.message}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
