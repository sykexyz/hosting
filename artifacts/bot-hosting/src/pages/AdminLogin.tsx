import { useState } from "react";
import { Link, useLocation } from "wouter";
import { useAdminLogin } from "@workspace/api-client-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";

export default function AdminLogin() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const adminLogin = useAdminLogin();
  
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    adminLogin.mutate({ data: { identifier, password } }, {
      onSuccess: () => {
        toast({ title: "Authorized", description: "Entering admin terminal" });
        setLocation("/admin");
      },
      onError: (err) => {
        toast({ title: "Access Denied", description: err.error || "Invalid credentials", variant: "destructive" });
      }
    });
  };

  return (
    <div className="min-h-[100dvh] flex flex-col items-center justify-center p-6 bg-black relative">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-red-900/20 blur-[100px] rounded-full pointer-events-none" />

      <Card className="w-full max-w-sm border-white/5 bg-neutral-900/80 backdrop-blur-xl shadow-2xl">
        <CardHeader className="text-center pb-6">
          <div className="mx-auto w-12 h-12 mb-4 border border-white/10 rounded-lg flex items-center justify-center bg-black">
            <div className="w-4 h-4 bg-red-500 rounded-sm shadow-[0_0_15px_rgba(239,68,68,0.8)]"></div>
          </div>
          <CardTitle className="text-xl tracking-widest text-white/80 uppercase font-mono">System Admin</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="identifier" className="text-xs uppercase tracking-wider text-white/50">Identifier</Label>
              <Input 
                id="identifier" 
                placeholder="ROOT_ID" 
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                className="bg-black/50 border-white/10 font-mono focus:border-red-500/50 focus:shadow-[inset_0_2px_4px_rgba(0,0,0,0.6),0_0_8px_rgba(239,68,68,0.3)]"
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password" className="text-xs uppercase tracking-wider text-white/50">Auth Key</Label>
              <Input 
                id="password" 
                type="password" 
                placeholder="••••••••" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="bg-black/50 border-white/10 font-mono focus:border-red-500/50 focus:shadow-[inset_0_2px_4px_rgba(0,0,0,0.6),0_0_8px_rgba(239,68,68,0.3)]"
                required
              />
            </div>

            <Button type="submit" className="w-full mt-6 bg-red-900/50 border-red-500/30 hover:bg-red-800/80 text-red-100 shadow-none hover:shadow-[0_0_15px_rgba(239,68,68,0.4)]" disabled={adminLogin.isPending}>
              {adminLogin.isPending ? "VERIFYING..." : "AUTHORIZE"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
