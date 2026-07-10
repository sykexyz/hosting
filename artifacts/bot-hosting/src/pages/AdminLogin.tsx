import { useState } from "react";
import { Link, useLocation } from "wouter";
import { useAdminLogin } from "@workspace/api-client-react";
import { Logo } from "../components/Logo";
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
        toast({ title: "Welcome back", description: "Logged in to the admin panel" });
        setLocation("/admin");
      },
      onError: (err) => {
        toast({ title: "Login failed", description: err.error || "Invalid credentials", variant: "destructive" });
      }
    });
  };

  return (
    <div className="min-h-[100dvh] flex flex-col items-center justify-center p-6 bg-[#05050f] relative">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-cyan-500/10 blur-[100px] rounded-full pointer-events-none" />

      <Card className="w-full max-w-sm !bg-neutral-900/90 !border-white/10 backdrop-blur-xl shadow-2xl">
        <CardHeader className="text-center pb-6">
          <Logo className="mx-auto w-12 h-12 mb-4 drop-shadow-[0_0_15px_rgba(34,211,238,0.35)]" />
          <CardTitle className="text-xl text-white">Admin Login</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="identifier" className="text-sm text-white/60">Username or email</Label>
              <Input 
                id="identifier" 
                placeholder="admin" 
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                className="bg-black/40 border-white/10 text-white focus:border-cyan-400/50 focus:shadow-[inset_0_2px_4px_rgba(0,0,0,0.6),0_0_8px_rgba(34,211,238,0.3)]"
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm text-white/60">Password</Label>
              <Input 
                id="password" 
                type="password" 
                placeholder="••••••••" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="bg-black/40 border-white/10 text-white focus:border-cyan-400/50 focus:shadow-[inset_0_2px_4px_rgba(0,0,0,0.6),0_0_8px_rgba(34,211,238,0.3)]"
                required
              />
            </div>

            <Button type="submit" className="w-full mt-6 bg-cyan-500/15 border border-cyan-400/40 hover:bg-cyan-500/25 text-cyan-100 shadow-none hover:shadow-[0_0_15px_rgba(34,211,238,0.4)]" disabled={adminLogin.isPending}>
              {adminLogin.isPending ? "Logging in..." : "Log In"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
