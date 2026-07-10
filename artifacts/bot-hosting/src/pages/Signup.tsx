import { useState } from "react";
import { Logo } from "../components/Logo";
import { Link, useLocation } from "wouter";
import { useSignup } from "@workspace/api-client-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";

export default function Signup() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const signup = useSignup();
  
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!email.includes("@gmail.com")) {
      newErrors.email = "Please use a valid Gmail address.";
    }
    if (username.length < 3) {
      newErrors.username = "Username must be at least 3 characters.";
    }
    if (password.length < 6) {
      newErrors.password = "Password must be at least 6 characters.";
    }
    if (password !== confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match.";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    signup.mutate({ data: { email, username, password, confirmPassword } }, {
      onSuccess: () => {
        toast({ title: "Account created", description: "Welcome to 1999 Bot Hosting" });
        setLocation("/dashboard");
      },
      onError: (err) => {
        toast({ title: "Error", description: err.error || "Failed to create account", variant: "destructive" });
      }
    });
  };

  return (
    <div className="min-h-[100dvh] flex flex-col items-center justify-center p-6 relative">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-600/10 blur-[100px] rounded-full pointer-events-none" />
      
      <Link href="/" className="flex items-center gap-3 mb-8 hover:scale-105 transition-transform">
        <Logo className="w-12 h-12 drop-shadow-[0_0_20px_rgba(59,130,246,0.6)]" />
      </Link>

      <Card className="w-full max-w-md">
        <CardHeader className="text-center pb-8">
          <CardTitle className="text-3xl">Create Account</CardTitle>
          <CardDescription>Deploy your applications on premium infrastructure</CardDescription>
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
              />
              {errors.email && <p className="text-sm text-red-400 font-medium">{errors.email}</p>}
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input 
                id="username" 
                placeholder="cozydev" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
              {errors.username && <p className="text-sm text-red-400 font-medium">{errors.username}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input 
                id="password" 
                type="password" 
                placeholder="••••••••" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              {errors.password && <p className="text-sm text-red-400 font-medium">{errors.password}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input 
                id="confirmPassword" 
                type="password" 
                placeholder="••••••••" 
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
              {errors.confirmPassword && <p className="text-sm text-red-400 font-medium">{errors.confirmPassword}</p>}
            </div>

            <Button type="submit" className="w-full mt-4" disabled={signup.isPending}>
              {signup.isPending ? "Creating..." : "Create Account"}
            </Button>
          </form>

          <div className="mt-6 text-center text-sm text-blue-100/60">
            Already have an account? <Link href="/login" className="text-blue-400 hover:text-blue-300 font-medium">Log in</Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
