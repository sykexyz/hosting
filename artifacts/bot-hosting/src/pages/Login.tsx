import { useState } from "react";
import { Logo } from "../components/Logo";
import { ThemeToggle } from "../components/ThemeToggle";
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
        toast({ title: "Login failed", description: err.error || "Invalid credentials", variant: "destructive" });
      }
    });
  };

  return (
    <div className="min-h-[100dvh] flex flex-col items-center justify-center p-6 relative">
      <div className="fixed top-4 right-4 z-50">
        <ThemeToggle />
      </div>
      <Link href="/" className="flex items-center gap-3 mb-8 hover:scale-105 transition-transform bg-white/50 dark:bg-white/5 backdrop-blur-sm p-4 rounded-full shadow-sm border border-white dark:border-white/10">
        <Logo className="w-12 h-12 text-blue-600 drop-shadow-sm" />
      </Link>

      <Card className="w-full max-w-md glass-panel p-2 border-white shadow-lg">
        <CardHeader className="text-center pb-8 pt-6">
          <CardTitle className="text-3xl font-bold text-slate-800 drop-shadow-sm">Client Login</CardTitle>
          <CardDescription className="text-slate-600 font-medium mt-1">Access your hosting environment</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-3">
              <Label htmlFor="email" className="text-slate-700 font-bold ml-1">Email</Label>
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
            
            <div className="space-y-3">
              <Label htmlFor="password" className="text-slate-700 font-bold ml-1">Password</Label>
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

            <button type="submit" className="w-full btn-3d btn-3d-primary h-12 mt-4 text-lg font-bold" disabled={login.isPending}>
              {login.isPending ? "Authenticating..." : "Sign in Now!"}
            </button>
          </form>

          <div className="mt-8 text-center text-sm text-slate-600 font-medium bg-white/40 p-4 rounded-xl border border-white shadow-inner">
            Need an account? <Link href="/signup" className="text-blue-600 hover:text-blue-500 font-bold ml-1 hover:underline">Deploy now</Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
