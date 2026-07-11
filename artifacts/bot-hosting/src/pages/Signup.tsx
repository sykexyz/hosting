import { useState } from "react";
import { Logo } from "../components/Logo";
import { StarField } from "../components/StarField";
import { Link, useLocation } from "wouter";
import { useSignup } from "@workspace/api-client-react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

export default function Signup() {
  const [, setLocation] = useLocation();
  const signup = useSignup();

  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [shaking, setShaking] = useState(false);

  const triggerShake = () => {
    setShaking(true);
    setTimeout(() => setShaking(false), 600);
  };

  const validate = () => {
    const e: Record<string, string> = {};
    if (!email.includes("@gmail.com")) e.email = "Please use a valid Gmail address.";
    if (username.length < 3) e.username = "Username must be at least 3 characters.";
    if (password.length < 6) e.password = "Password must be at least 6 characters.";
    if (password !== confirmPassword) e.confirmPassword = "Passwords do not match.";
    setErrors(e);
    if (Object.keys(e).length > 0) triggerShake();
    return Object.keys(e).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    signup.mutate({ data: { email, username, password, confirmPassword } }, {
      onSuccess: () => {
        toast.success("Account created", { description: "Welcome to 1999 Bot Hosting" });
        setLocation("/dashboard");
      },
      onError: (err: unknown) => {
        triggerShake();
        toast.error("Error", { description: (err as any)?.data?.error || "Failed to create account" });
      },
    });
  };

  const fields = [
    { id: "email",           label: "Email",            type: "email",    placeholder: "developer@gmail.com", val: email,           set: setEmail },
    { id: "username",        label: "Username",         type: "text",     placeholder: "cozydev",             val: username,        set: setUsername },
    { id: "password",        label: "Password",         type: "password", placeholder: "••••••••",            val: password,        set: setPassword },
    { id: "confirmPassword", label: "Confirm Password", type: "password", placeholder: "••••••••",            val: confirmPassword, set: setConfirmPassword },
  ];

  return (
    <div className="min-h-[100dvh] flex flex-col items-center justify-center p-6 relative">
      <StarField />

      {/* Animated grid background */}
      <div className="fixed inset-0 grid-bg pointer-events-none z-[1] opacity-60" />

      {/* Ambient glow */}
      <div
        className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] pointer-events-none z-[1]"
        style={{ background: "radial-gradient(circle, rgba(120,80,220,0.08) 0%, transparent 65%)", filter: "blur(60px)" }}
      />

      <div className="relative z-10 w-full max-w-md flex flex-col items-center my-6">
        <Link href="/" className="flex items-center gap-3 mb-6 hover:scale-105 transition-transform p-3 rounded-full" style={{ border: "1px solid rgba(255,255,255,0.09)", background: "rgba(255,255,255,0.03)", backdropFilter: "blur(12px)" }}>
          <Logo className="w-10 h-10 text-white" />
        </Link>

        <div className={`w-full glass-panel shadow-[0_8px_60px_rgba(0,0,0,0.8)] ${shaking ? "shake" : ""}`} style={{ borderColor: "rgba(255,255,255,0.09)" }}>
          <div className="text-center pb-5 pt-7 px-6">
            <h1 className="text-2xl font-bold text-white mb-1">Create Account</h1>
            <p className="text-white/35 text-sm font-medium">Deploy on premium infrastructure</p>
          </div>

          <div className="px-6 pb-7">
            <form onSubmit={handleSubmit} className="space-y-4">
              {fields.map(({ id, label, type, placeholder, val, set }) => (
                <div key={id} className="space-y-1.5">
                  <Label htmlFor={id} className="text-white/55 font-bold ml-1 text-sm">{label}</Label>
                  <Input
                    id={id}
                    type={type}
                    placeholder={placeholder}
                    value={val}
                    onChange={(e) => set(e.target.value)}
                    className="input-3d h-11 px-4"
                  />
                  {errors[id] && <p className="text-xs text-red-400/90 font-bold ml-1 mt-1">{errors[id]}</p>}
                </div>
              ))}

              <button
                type="submit"
                className="w-full btn-3d btn-3d-primary h-12 mt-2 text-base font-bold"
                disabled={signup.isPending}
              >
                {signup.isPending ? (
                  <span className="flex items-center gap-2 justify-center">
                    <span className="w-4 h-4 rounded-full border-2 border-black/30 border-t-black/70 animate-spin" />
                    Creating...
                  </span>
                ) : "Sign Up"}
              </button>
            </form>

            <div
              className="mt-5 text-center text-sm text-white/35 p-4 rounded-xl"
              style={{ background: "rgba(255,255,255,0.025)", border: "1px solid rgba(255,255,255,0.07)" }}
            >
              Already have an account?{" "}
              <Link href="/login" className="text-white hover:text-white/70 font-bold ml-1 transition-colors">
                Log in
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
