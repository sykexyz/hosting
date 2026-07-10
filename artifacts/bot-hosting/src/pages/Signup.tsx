import { useState } from "react";
import { Logo } from "../components/Logo";
import { Link, useLocation } from "wouter";
import { useSignup } from "@workspace/api-client-react";
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
      <Link href="/" className="flex items-center gap-3 mb-6 hover:scale-105 transition-transform bg-white/50 backdrop-blur-sm p-3 rounded-full shadow-sm border border-white mt-6">
        <Logo className="w-10 h-10 text-blue-600 drop-shadow-sm" />
      </Link>

      <Card className="w-full max-w-md glass-panel p-2 border-white shadow-lg">
        <CardHeader className="text-center pb-6 pt-6">
          <CardTitle className="text-3xl font-bold text-slate-800 drop-shadow-sm">Create Account</CardTitle>
          <CardDescription className="text-slate-600 font-medium mt-1">Deploy your applications on premium infrastructure</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-slate-700 font-bold ml-1">Email</Label>
              <Input 
                id="email" 
                type="email" 
                placeholder="developer@gmail.com" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-3d h-11 px-4 text-base"
              />
              {errors.email && <p className="text-sm text-red-500 font-bold ml-1 mt-1">{errors.email}</p>}
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="username" className="text-slate-700 font-bold ml-1">Username</Label>
              <Input 
                id="username" 
                placeholder="cozydev" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="input-3d h-11 px-4 text-base"
              />
              {errors.username && <p className="text-sm text-red-500 font-bold ml-1 mt-1">{errors.username}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-slate-700 font-bold ml-1">Password</Label>
              <Input 
                id="password" 
                type="password" 
                placeholder="••••••••" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-3d h-11 px-4 text-base"
              />
              {errors.password && <p className="text-sm text-red-500 font-bold ml-1 mt-1">{errors.password}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword" className="text-slate-700 font-bold ml-1">Confirm Password</Label>
              <Input 
                id="confirmPassword" 
                type="password" 
                placeholder="••••••••" 
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="input-3d h-11 px-4 text-base"
              />
              {errors.confirmPassword && <p className="text-sm text-red-500 font-bold ml-1 mt-1">{errors.confirmPassword}</p>}
            </div>

            <button type="submit" className="w-full btn-3d btn-3d-primary h-12 mt-6 text-lg font-bold" disabled={signup.isPending}>
              {signup.isPending ? "Creating..." : "Add Application"}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-slate-600 font-medium bg-white/40 p-4 rounded-xl border border-white shadow-inner">
            Already have an account? <Link href="/login" className="text-blue-600 hover:text-blue-500 font-bold ml-1 hover:underline">Log in</Link>
          </div>
        </CardContent>
      </Card>
      <div className="h-6"></div>
    </div>
  );
}
