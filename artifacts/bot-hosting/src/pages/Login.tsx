import { useState } from "react";
import { Logo } from "../components/Logo";
import { StarField } from "../components/StarField";
import { Link, useLocation } from "wouter";
import { useLogin } from "@workspace/api-client-react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

export default function Login() {
  const [, setLocation] = useLocation();
  const login = useLogin();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [shaking, setShaking] = useState(false);

  const triggerShake = () => {
    setShaking(true);
    setTimeout(() => setShaking(false), 600);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login.mutate({ data: { email, password } }, {
      onSuccess: () => {
        toast.success("Welcome back", { description: "Authenticated successfully" });
        setLocation("/dashboard");
      },
      onError: (err: unknown) => {
        triggerShake();
        toast.error("Login failed", { description: (err as any)?.data?.error || "Invalid credentials" });
      },
    });
  };

  return (
    <div className="min-h-[100dvh] flex flex-col items-center justify-center p-6 relative">
      <StarField />

      {/* Animated grid background */}
      <div className="fixed inset-0 grid-bg pointer-events-none z-[1] opacity-60" />

      {/* Ambient glow center */}
      <div
        className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] pointer-events-none z-[1]"
        style={{ background: "radial-gradient(circle, rgba(120,80,220,0.08) 0%, transparent 65%)", filter: "blur(60px)" }}
      />

      <div className="relative z-10 w-full max-w-md flex flex-col items-center">
        <Link href="/" className="flex items-center gap-3 mb-8 hover:scale-105 transition-transform p-3 rounded-full" style={{ border: "1px solid rgba(255,255,255,0.09)", background: "rgba(255,255,255,0.03)", backdropFilter: "blur(12px)" }}>
          <Logo className="w-10 h-10 text-white" />
        </Link>

        <div className={`w-full glass-panel shadow-[0_8px_60px_rgba(0,0,0,0.8)] ${shaking ? "shake" : ""}`} style={{ borderColor: "rgba(255,255,255,0.09)" }}>
          <div className="text-center pb-6 pt-7 px-6">
            <h1 className="text-2xl font-bold text-white mb-1">Client Login</h1>
            <p className="text-white/35 text-sm font-medium">Access your hosting environment</p>
          </div>

          <div className="px-6 pb-7">
            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-white/55 font-bold ml-1 text-sm">Email</Label>
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
                <Label htmlFor="password" className="text-white/55 font-bold ml-1 text-sm">Password</Label>
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
                className="w-full btn-3d btn-3d-primary h-12 mt-1 text-base font-bold"
                disabled={login.isPending}
              >
                {login.isPending ? (
                  <span className="flex items-center gap-2 justify-center">
                    <span className="w-4 h-4 rounded-full border-2 border-black/30 border-t-black/70 animate-spin" />
                    Authenticating...
                  </span>
                ) : "Sign In"}
              </button>
            </form>

            <div
              className="mt-5 text-center text-sm text-white/35 p-4 rounded-xl"
              style={{ background: "rgba(255,255,255,0.025)", border: "1px solid rgba(255,255,255,0.07)" }}
            >
              Need an account?{" "}
              <Link href="/signup" className="text-white hover:text-white/70 font-bold ml-1 transition-colors">
                Sign up
              </Link>
            </div>

            <div className="mt-3 text-center">
              <Link href="/admin-login" className="text-xs text-white/18 hover:text-white/40 transition-colors">
                Admin access
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
