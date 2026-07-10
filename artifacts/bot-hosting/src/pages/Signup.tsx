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
    const e: Record<string, string> = {};
    if (!email.includes("@gmail.com")) e.email = "Please use a valid Gmail address.";
    if (username.length < 3) e.username = "Username must be at least 3 characters.";
    if (password.length < 6) e.password = "Password must be at least 6 characters.";
    if (password !== confirmPassword) e.confirmPassword = "Passwords do not match.";
    setErrors(e);
    return Object.keys(e).length === 0;
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
        toast({ title: "Error", description: err.data?.error || "Failed to create account", variant: "destructive" });
      }
    });
  };

  return (
    <div className="min-h-[100dvh] flex flex-col items-center justify-center p-6 relative">
      <Link href="/" className="flex items-center gap-3 mb-6 hover:scale-105 transition-transform p-3 rounded-full border border-white/10 bg-white/[0.03] backdrop-blur-sm mt-6">
        <Logo className="w-10 h-10 text-white" />
      </Link>

      <Card className="w-full max-w-md glass-panel border-white/10 shadow-[0_8px_60px_rgba(255,255,255,0.05)]">
        <CardHeader className="text-center pb-6 pt-6">
          <CardTitle className="text-3xl font-bold text-white">Create Account</CardTitle>
          <CardDescription className="text-white/40 font-medium mt-1">Deploy your applications on premium infrastructure</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">
            {[
              { id: "email",           label: "Email",            type: "email",    placeholder: "developer@gmail.com", val: email,           set: setEmail },
              { id: "username",        label: "Username",         type: "text",     placeholder: "cozydev",             val: username,        set: setUsername },
              { id: "password",        label: "Password",         type: "password", placeholder: "••••••••",            val: password,        set: setPassword },
              { id: "confirmPassword", label: "Confirm Password", type: "password", placeholder: "••••••••",            val: confirmPassword, set: setConfirmPassword },
            ].map(({ id, label, type, placeholder, val, set }) => (
              <div key={id} className="space-y-2">
                <Label htmlFor={id} className="text-white/60 font-bold ml-1">{label}</Label>
                <Input
                  id={id}
                  type={type}
                  placeholder={placeholder}
                  value={val}
                  onChange={(e) => set(e.target.value)}
                  className="input-3d h-11 px-4 text-base"
                />
                {errors[id] && <p className="text-sm text-red-400 font-bold ml-1 mt-1">{errors[id]}</p>}
              </div>
            ))}

            <button
              type="submit"
              className="w-full btn-3d btn-3d-primary h-12 mt-4 text-base font-bold"
              disabled={signup.isPending}
            >
              {signup.isPending ? "Creating..." : "Sign Up"}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-white/40 bg-white/[0.03] p-4 rounded-xl border border-white/8">
            Already have an account?{" "}
            <Link href="/login" className="text-white hover:text-white/70 font-bold ml-1 transition-colors">
              Log in
            </Link>
          </div>
        </CardContent>
      </Card>
      <div className="h-6"></div>
    </div>
  );
}
