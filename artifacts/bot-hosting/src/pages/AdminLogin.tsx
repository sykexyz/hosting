import { useState } from "react";
import { Link, useLocation } from "wouter";
import { useAdminLogin } from "@workspace/api-client-react";
import { Logo } from "../components/Logo";
import { StarField } from "../components/StarField";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

export default function AdminLogin() {
  const [, setLocation] = useLocation();
  const adminLogin = useAdminLogin();

  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [shaking, setShaking] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    adminLogin.mutate({ data: { identifier, password } }, {
      onSuccess: () => {
        toast.success("Access granted", { description: "Welcome to the admin panel" });
        setLocation("/admin");
      },
      onError: (err: unknown) => {
        setShaking(true);
        setTimeout(() => setShaking(false), 600);
        toast.error("Access denied", { description: (err as any)?.data?.error || "Invalid credentials" });
      },
    });
  };

  return (
    <div className="min-h-[100dvh] flex flex-col items-center justify-center p-6 relative">
      <StarField />
      <div className="fixed inset-0 grid-bg pointer-events-none z-[1] opacity-50" />
      <div
        className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] pointer-events-none z-[1]"
        style={{ background: "radial-gradient(circle, rgba(200,60,60,0.06) 0%, transparent 65%)", filter: "blur(50px)" }}
      />

      <div className="relative z-10 w-full max-w-sm flex flex-col items-center">
        <Link href="/login" className="flex items-center gap-3 mb-8 hover:scale-105 transition-transform p-3 rounded-full" style={{ border: "1px solid rgba(255,255,255,0.09)", background: "rgba(255,255,255,0.03)", backdropFilter: "blur(12px)" }}>
          <Logo className="w-10 h-10 text-white" />
        </Link>

        <div className={`w-full glass-panel shadow-[0_8px_60px_rgba(0,0,0,0.8)] ${shaking ? "shake" : ""}`} style={{ borderColor: "rgba(255,50,50,0.15)" }}>
          <div className="text-center pb-5 pt-7 px-6">
            <div className="w-10 h-10 mx-auto mb-4 rounded-full flex items-center justify-center" style={{ background: "rgba(255,50,50,0.08)", border: "1px solid rgba(255,50,50,0.2)" }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="rgba(255,100,100,0.8)" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </div>
            <h1 className="text-2xl font-bold text-white mb-1">Admin Panel</h1>
            <p className="text-white/35 text-sm">Restricted access only</p>
          </div>

          <div className="px-6 pb-7">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="identifier" className="text-white/55 font-bold ml-1 text-sm">Username or email</Label>
                <Input id="identifier" placeholder="admin" value={identifier} onChange={e => setIdentifier(e.target.value)} className="input-3d h-11 px-4" required />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="password" className="text-white/55 font-bold ml-1 text-sm">Password</Label>
                <Input id="password" type="password" placeholder="••••••••" value={password} onChange={e => setPassword(e.target.value)} className="input-3d h-11 px-4" required />
              </div>
              <button type="submit" className="w-full btn-3d h-11 mt-1 text-sm font-bold" disabled={adminLogin.isPending} style={{ borderColor: "rgba(255,50,50,0.3)", color: "rgba(255,130,130,0.9)" }}>
                {adminLogin.isPending ? "Authenticating..." : "Log In →"}
              </button>
            </form>
            <div className="mt-4 text-center text-sm text-white/30 p-3 rounded-xl" style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)" }}>
              Not an admin?{" "}
              <Link href="/login" className="text-white hover:text-white/60 font-bold ml-1 transition-colors">Client login</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
