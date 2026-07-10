import { useState } from "react";
import { Logo } from "../components/Logo";
import { Link, useLocation } from "wouter";
import { useLogin } from "@workspace/api-client-react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";

export default function Login() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const login = useLogin();
  
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login.mutate({ data: { email, password } }, {
      onSuccess: () => {
        toast({ title: "Welcome back", description: "Authenticated successfully" });
        setLocation("/dashboard");
      },
      onError: (err) => {
        toast({ title: "Login failed", description: err.data?.error || "Invalid credentials", variant: "destructive" });
      }
    });
  };

  return (
    <div className="min-h-[100dvh] flex flex-col items-center justify-center p-6 relative">
      <Link href="/" className="flex items-center gap-3 mb-8 hover:scale-105 transition-transform p-3 rounded-full border border-white/10 bg-white/[0.03] backdrop-blur-sm">
        <Logo className="w-10 h-10 text-white" />
      </Link>

      <Card className="w-full max-w-md glass-panel border-white/10 shadow-[0_8px_60px_rgba(255,255,255,0.05)]">
        <CardHeader className="text-center pb-8 pt-6">
          <CardTitle className="text-3xl font-bold text-white">Client Login</CardTitle>
          <CardDescription className="text-white/40 font-medium mt-1">Access your hosting environment</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-white/60 font-bold ml-1">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="developer@gmail.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="input-3d h-12 px-4 text-base"
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
                required
                className="input-3d h-12 px-4 text-base"
              />
            </div>
            <button
              type="submit"
              className="w-full btn-3d btn-3d-primary h-12 mt-2 text-base font-bold"
              disabled={login.isPending}
            >
              {login.isPending ? "Authenticating..." : "Sign In"}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-white/40 bg-white/[0.03] p-4 rounded-xl border border-white/8">
            Need an account?{" "}
            <Link href="/signup" className="text-white hover:text-white/70 font-bold ml-1 transition-colors">
              Sign up
            </Link>
          </div>

          <div className="mt-3 text-center">
            <Link href="/admin-login" className="text-xs text-white/20 hover:text-white/50 transition-colors">
              Admin access
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
