import { useState, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { Logo } from "../components/Logo";
import { StarField } from "../components/StarField";
import { Link } from "wouter";
import { SiDiscord, SiTelegram, SiPython, SiJavascript, SiTypescript, SiNodedotjs, SiGo } from "react-icons/si";
import { FaJava } from "react-icons/fa";
import { motion, AnimatePresence, useScroll, useTransform } from "framer-motion";

function SplashAnimation({ onComplete }: { onComplete: () => void }) {
  const [progress, setProgress] = useState(1);
  const [phase, setPhase] = useState<"loading" | "done">("loading");

  useEffect(() => {
    const duration = 2800;
    const interval = 25;
    const steps = duration / interval;
    let currentStep = 0;

    const timer = setInterval(() => {
      currentStep++;
      const nextProgress = Math.min(100, Math.floor((currentStep / steps) * 100));
      setProgress(nextProgress);
      if (currentStep >= steps) {
        clearInterval(timer);
        setPhase("done");
        setTimeout(onComplete, 500);
      }
    }, interval);

    return () => clearInterval(timer);
  }, [onComplete]);

  const icons = [
    { Icon: SiPython,     color: "rgba(100,180,255,0.9)" },
    { Icon: SiJavascript, color: "rgba(255,220,80,0.9)" },
    { Icon: SiTypescript, color: "rgba(80,160,255,0.9)" },
    { Icon: SiNodedotjs,  color: "rgba(80,200,100,0.9)" },
    { Icon: FaJava,       color: "rgba(255,140,80,0.9)" },
    { Icon: SiGo,         color: "rgba(80,220,255,0.9)" },
  ];

  return createPortal(
    <AnimatePresence>
      {phase === "loading" && (
        <motion.div
          key="splash"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0, transition: { duration: 0.6 } }}
          className="fixed inset-0 z-[200] overflow-hidden"
          style={{ background: "#050507" }}
        >
          {/* Milky Way canvas behind splash */}
          <StarField />

          {/* Central glow */}
          <div
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full pointer-events-none"
            style={{
              background: "radial-gradient(circle, rgba(120,80,220,0.12) 0%, rgba(60,40,120,0.06) 40%, transparent 70%)",
              filter: "blur(40px)",
            }}
          />

          <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)", zIndex: 10, display: "flex", flexDirection: "column", alignItems: "center", width: "100%" }}>
            {/* Orbit container */}
            <div className="relative w-52 h-52 mb-10 splash-orbit-container">
              {icons.map((item, i) => {
                const angle = (i / icons.length) * 360;
                return (
                  <div
                    key={i}
                    className="absolute top-1/2 left-1/2 w-11 h-11 -ml-[22px] -mt-[22px]"
                    style={{ transform: `rotate(${angle}deg) translateY(-88px)` }}
                  >
                    <div
                      className="w-full h-full splash-orbit-icon flex items-center justify-center rounded-full border"
                      style={{
                        background: "rgba(255,255,255,0.04)",
                        borderColor: "rgba(255,255,255,0.12)",
                        boxShadow: `0 0 14px ${item.color.replace("0.9","0.25")}`,
                      }}
                    >
                      <item.Icon size={20} color={item.color} style={{ filter: `drop-shadow(0 0 5px ${item.color})` }} />
                    </div>
                  </div>
                );
              })}
              {/* Center logo */}
              <div
                className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-20 h-20 rounded-full flex items-center justify-center"
                style={{
                  background: "rgba(255,255,255,0.05)",
                  border: "1px solid rgba(255,255,255,0.15)",
                  boxShadow: "0 0 40px rgba(200,180,255,0.2), inset 0 1px 0 rgba(255,255,255,0.1)",
                }}
              >
                <Logo className="w-12 h-12 text-white" />
              </div>
            </div>

            {/* Title */}
            <h1
              className="text-2xl md:text-4xl font-bold text-white tracking-tight mb-2 text-center px-4 glitch"
              data-text="Welcome to 1999 Bot Hosting"
              style={{ fontFamily: "'Manrope', sans-serif", textShadow: "0 0 30px rgba(200,180,255,0.4)" }}
            >
              Welcome to 1999 Bot Hosting
            </h1>
            <p className="text-white/30 text-sm mb-10 font-mono tracking-widest">INITIALIZING SYSTEMS</p>

            {/* Progress bar */}
            <div className="w-72 md:w-96">
              <div
                className="w-full h-1.5 rounded-full overflow-hidden mb-3"
                style={{ background: "rgba(255,255,255,0.07)", border: "1px solid rgba(255,255,255,0.06)" }}
              >
                <div
                  className="h-full rounded-full transition-all duration-75 ease-out"
                  style={{
                    width: `${progress}%`,
                    background: "linear-gradient(90deg, rgba(120,80,220,0.9), rgba(200,160,255,0.9), rgba(255,255,255,0.9))",
                    boxShadow: "0 0 12px rgba(180,140,255,0.6), 0 0 4px rgba(255,255,255,0.4)",
                  }}
                />
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-white/25 font-mono">boot sequence</span>
                <span
                  className="font-mono text-sm font-bold text-white/70"
                  style={{ fontFamily: "'Orbitron', monospace" }}
                >
                  {progress}%
                </span>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>,
    document.body
  );
}

function ParallaxHero() {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start start", "end start"] });
  const y = useTransform(scrollYProgress, [0, 1], ["0%", "30%"]);
  const opacity = useTransform(scrollYProgress, [0, 0.8], [1, 0]);

  return (
    <section ref={ref} className="relative px-6 lg:px-12 py-28 lg:py-40 flex flex-col items-center text-center overflow-hidden">
      <motion.div style={{ y, opacity }} className="relative z-10 flex flex-col items-center">
        {/* Hero badge */}
        <div
          className="mb-6 inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-bold text-white/60 tracking-wider uppercase"
          style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)" }}
        >
          <div className="w-1.5 h-1.5 rounded-full bg-green-400 shadow-[0_0_6px_rgba(74,222,128,0.8)] animate-pulse" />
          Systems Online
        </div>

        <h1
          className="text-5xl lg:text-7xl font-bold text-white tracking-tighter mb-6 glitch"
          data-text="Premium infrastructure for your applications"
          style={{
            textShadow: "0 0 60px rgba(200,180,255,0.2)",
            fontSize: "clamp(2.2rem, 6vw, 4.5rem)",
          }}
        >
          Premium infrastructure<br className="hidden lg:block" />
          <span className="text-white/70"> for your applications</span>
        </h1>
        <p className="text-base lg:text-lg text-white/45 max-w-2xl mb-10" style={{ fontSize: "clamp(0.95rem, 2.5vw, 1.125rem)" }}>
          Upload your source code and deploy instantly on dedicated, high-performance slots.
          Black-galaxy hosting built for serious developers.
        </p>
        <div className="flex items-center gap-4">
          <Link href="/signup" className="btn-3d btn-3d-primary text-base h-13 px-8 inline-flex items-center justify-center rounded-full" style={{ height: "52px" }}>
            Get Started Free
          </Link>
          <Link href="/login" className="btn-3d text-base h-13 px-8 inline-flex items-center justify-center rounded-full" style={{ height: "52px" }}>
            Sign In
          </Link>
        </div>
      </motion.div>

      {/* Ambient glow */}
      <div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] pointer-events-none"
        style={{
          background: "radial-gradient(ellipse, rgba(120,80,220,0.07) 0%, transparent 70%)",
          filter: "blur(60px)",
        }}
      />
    </section>
  );
}

export default function Landing() {
  const [showSplash, setShowSplash] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const hasSeenSplash = sessionStorage.getItem("hasSeenSplash");
    if (!hasSeenSplash) {
      setShowSplash(true);
    } else {
      setMounted(true);
    }
  }, []);

  const handleSplashComplete = () => {
    setShowSplash(false);
    setMounted(true);
    sessionStorage.setItem("hasSeenSplash", "true");
  };

  return (
    <>
      {showSplash && <SplashAnimation onComplete={handleSplashComplete} />}

      <div
        className={`flex flex-col min-h-[100dvh] transition-opacity duration-700 ${mounted ? "opacity-100" : "opacity-0"}`}
        style={{ background: "transparent" }}
      >
        <StarField />

        {/* Nav */}
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[95%] max-w-5xl">
          <header
            className="h-14 px-6 flex items-center justify-between rounded-full"
            style={{
              background: "rgba(255,255,255,0.04)",
              backdropFilter: "blur(20px)",
              border: "1px solid rgba(255,255,255,0.09)",
              boxShadow: "0 4px 24px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.06)",
            }}
          >
            <div className="flex items-center gap-3">
              <Logo className="w-7 h-7 text-white" />
              <span className="text-base font-bold text-white tracking-tight hidden md:inline-block">1999 Bot Hosting</span>
            </div>
            <nav className="flex items-center gap-3">
              <Link href="/login" className="text-sm font-medium text-white/50 hover:text-white transition-colors px-3">
                Login
              </Link>
              <Link href="/signup" className="btn-3d btn-3d-primary text-sm h-8 px-5 inline-flex items-center justify-center rounded-full">
                Sign Up
              </Link>
            </nav>
          </header>
        </div>

        <main className="flex-1 pt-24 relative z-10">
          <ParallaxHero />

          {/* Features */}
          <section className="px-6 lg:px-12 py-20 relative z-10">
            <div className="max-w-4xl mx-auto glass-panel p-10 text-center rounded-3xl">
              <div
                className="w-14 h-14 mx-auto rounded-2xl flex items-center justify-center mb-5"
                style={{ background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)" }}
              >
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.8)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
              </div>
              <h2 className="text-2xl md:text-3xl font-bold text-white mb-3" style={{ fontSize: "clamp(1.4rem, 4vw, 1.875rem)" }}>100% Free Forever</h2>
              <p className="text-white/40 text-base mb-8 max-w-2xl mx-auto">
                All of our premium infrastructure slots are completely free. No credit card. No hidden fees.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
                {[
                  { title: "Dedicated RAM",  desc: "Resources reserved exclusively for your application's performance." },
                  { title: "NVMe Storage",   desc: "Lightning-fast disk access for databases and temporary files." },
                  { title: "Any Language",   desc: "Python, Node.js, Java, TypeScript, and more supported out of the box." },
                ].map(f => (
                  <div
                    key={f.title}
                    className="p-5 rounded-2xl"
                    style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)" }}
                  >
                    <div className="text-white font-bold mb-2 text-sm">{f.title}</div>
                    <p className="text-xs text-white/40 leading-relaxed">{f.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>
        </main>

        {/* Footer */}
        <footer
          className="mt-auto py-10 px-6 lg:px-12 relative z-10"
          style={{ background: "rgba(255,255,255,0.02)", borderTop: "1px solid rgba(255,255,255,0.07)" }}
        >
          <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-10">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <Logo className="w-6 h-6 text-white" />
                <span className="text-base font-bold text-white tracking-tight">1999 Bot Hosting</span>
              </div>
              <p className="text-sm text-white/30 max-w-sm">
                The flagship standard in code deployment and execution.
              </p>
            </div>
            <div className="md:justify-self-end">
              <h4 className="text-xs font-bold tracking-widest text-white/25 uppercase mb-4">DEVELOPER</h4>
              <div className="space-y-3">
                <a
                  href="https://t.me/cozybalenciaga"
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-3 text-white/50 hover:text-white group transition-colors"
                >
                  <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center transition-all group-hover:shadow-[0_0_14px_rgba(80,160,255,0.4)]"
                    style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)" }}
                  >
                    <SiTelegram size={14} className="text-blue-400 group-hover:text-blue-300" />
                  </div>
                  <span className="font-bold text-sm">@cozybalenciaga</span>
                </a>
                <div className="flex items-center gap-3 text-white/50 group cursor-default hover:text-white transition-colors">
                  <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center transition-all group-hover:shadow-[0_0_14px_rgba(130,100,255,0.4)]"
                    style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)" }}
                  >
                    <SiDiscord size={14} className="text-indigo-400 group-hover:text-indigo-300" />
                  </div>
                  <span className="font-bold text-sm">Discord</span>
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}
