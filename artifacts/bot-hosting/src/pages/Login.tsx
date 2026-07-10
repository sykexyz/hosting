import { useState } from "react";
import { Link, useLocation } from "wouter";
import { useLogin } from "@workspace/api-client-react";
import { Button } from "@/components/ui/button";
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
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-600/10 blur-[100px] rounded-full pointer-events-none" />
      
      <Link href="/" className="flex items-center gap-3 mb-8 hover:scale-105 transition-transform">
        <div className="w-10 h-10 rounded-lg bg-blue-500 shadow-[0_0_20px_rgba(59,130,246,0.6)] border border-blue-400 flex items-center justify-center">
          <div className="w-3.5 h-3.5 rounded-full bg-white shadow-[0_0_10px_white]"></div>
        </div>
      </Link>

      <Card className="w-full max-w-md">
        <CardHeader className="text-center pb-8">
          <CardTitle className="text-3xl">Client Login</CardTitle>
          <CardDescription>Access your hosting environment</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input 
                id="email" 
                type="email" 
                placeholder="developer@gmail.com" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input 
                id="password" 
                type="password" 
                placeholder="••••••••" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <Button type="submit" className="w-full mt-4" disabled={login.isPending}>
              {login.isPending ? "Authenticating..." : "Authenticate"}
            </Button>
          </form>

          <div className="mt-6 text-center text-sm text-blue-100/60">
            Need an account? <Link href="/signup" className="text-blue-400 hover:text-blue-300 font-medium">Deploy now</Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
