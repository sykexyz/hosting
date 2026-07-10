import { useState } from "react";
import { Link, useLocation } from "wouter";
import { useAdminLogin } from "@workspace/api-client-react";
import { Logo } from "../components/Logo";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
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
        toast({ title: "Access granted", description: "Welcome to the admin panel" });
        setLocation("/admin");
      },
      onError: (err) => {
        toast({ title: "Access denied", description: err.data?.error || "Invalid credentials", variant: "destructive" });
      }
    });
  };

  return (
    <div className="min-h-[100dvh] flex flex-col items-center justify-center p-6 relative">
      <Link href="/login" className="flex items-center gap-3 mb-8 hover:scale-105 transition-transform p-3 rounded-full border border-white/10 bg-white/[0.03] backdrop-blur-sm">
        <Logo className="w-10 h-10 text-white" />
      </Link>

      <Card className="w-full max-w-sm glass-panel border-white/10 shadow-[0_8px_60px_rgba(255,255,255,0.05)]">
        <CardHeader className="text-center pb-6 pt-6">
          <CardTitle className="text-2xl font-bold text-white">Admin Panel</CardTitle>
          <CardDescription className="text-white/40 font-medium mt-1">Restricted access only</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="identifier" className="text-white/60 font-bold ml-1">Username or email</Label>
              <Input
                id="identifier"
                placeholder="admin"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                className="input-3d h-11 px-4 text-base"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-white/60 font-bold ml-1">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-3d h-11 px-4 text-base"
                required
              />
            </div>

            <button
              type="submit"
              className="w-full btn-3d btn-3d-primary h-12 mt-4 text-base font-bold"
              disabled={adminLogin.isPending}
            >
              {adminLogin.isPending ? "Authenticating..." : "Log In"}
            </button>
          </form>

          <div className="mt-5 text-center text-sm text-white/40 bg-white/[0.03] p-3 rounded-xl border border-white/8">
            Not an admin?{" "}
            <Link href="/login" className="text-white hover:text-white/70 font-bold ml-1 transition-colors">
              Client login
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
