import { useState, useEffect } from "react";
import { Logo } from "../components/Logo";
import { ThemeToggle } from "../components/ThemeToggle";
import { Link } from "wouter";
import { SiDiscord, SiTelegram, SiPython, SiJavascript, SiTypescript, SiNodedotjs, SiGo } from "react-icons/si";
import { FaJava } from "react-icons/fa";

function SplashAnimation({ onComplete }: { onComplete: () => void }) {
  const [progress, setProgress] = useState(1);

  useEffect(() => {
    const duration = 2500;
    const interval = 25;
    const steps = duration / interval;
    let currentStep = 0;

    const timer = setInterval(() => {
      currentStep++;
      const nextProgress = Math.min(100, Math.floor((currentStep / steps) * 100));
      setProgress(nextProgress);
      
      if (currentStep >= steps) {
        clearInterval(timer);
        setTimeout(onComplete, 300);
      }
    }, interval);

    return () => clearInterval(timer);
  }, [onComplete]);

  const icons = [
    { Icon: SiPython, color: "#3776AB" },
    { Icon: SiJavascript, color: "#F7DF1E" },
    { Icon: SiTypescript, color: "#3178C6" },
    { Icon: SiNodedotjs, color: "#339933" },
    { Icon: FaJava, color: "#007396" },
    { Icon: SiGo, color: "#00ADD8" }
  ];

  return (
    <div className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-white/40 backdrop-blur-2xl transition-opacity duration-500">
      <div className="relative w-48 h-48 mb-8 splash-orbit-container">
        {icons.map((item, i) => {
          const angle = (i / icons.length) * 360;
          return (
            <div 
              key={i} 
              className="absolute top-1/2 left-1/2 w-12 h-12 -ml-6 -mt-6"
              style={{ transform: `rotate(${angle}deg) translateY(-80px)` }}
            >
              <div
                className="w-full h-full splash-orbit-icon flex items-center justify-center bg-white rounded-full shadow-lg border border-white/80"
                style={{
                  color: item.color,
                  boxShadow: `0 0 18px 4px ${item.color}70, 0 8px 16px ${item.color}50, inset 0 2px 4px rgba(255,255,255,1)`
                }}
              >
                <item.Icon size={24} color={item.color} style={{ filter: `drop-shadow(0 0 6px ${item.color})` }} />
              </div>
            </div>
          );
        })}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-xl">
          <Logo className="w-10 h-10 text-blue-500 drop-shadow-md" />
        </div>
      </div>
      
      <h1 className="text-3xl md:text-5xl font-bold text-slate-800 tracking-tight mb-8 text-center px-4 drop-shadow-sm">
        Welcome To 1999 Bot Hosting
      </h1>

      <div className="w-64 md:w-96 flex flex-col items-center">
        <div className="w-full h-4 bg-white/60 rounded-full overflow-hidden border border-white/80 shadow-inner mb-2">
          <div 
            className="h-full bg-gradient-to-r from-white via-sky-100 to-white transition-all duration-75 ease-out shadow-[0_0_18px_6px_rgba(255,255,255,0.9)]"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="font-digital text-blue-600 text-xl font-bold drop-shadow-sm">
          {progress}%
        </div>
      </div>
    </div>
  );
}

export default function Landing() {
  const [showSplash, setShowSplash] = useState(false);

  useEffect(() => {
    const hasSeenSplash = sessionStorage.getItem("hasSeenSplash");
    if (!hasSeenSplash) {
      setShowSplash(true);
    }
  }, []);

  const handleSplashComplete = () => {
    setShowSplash(false);
    sessionStorage.setItem("hasSeenSplash", "true");
  };

  return (
    <>
      {showSplash && <SplashAnimation onComplete={handleSplashComplete} />}
      <div className={`flex flex-col min-h-[100dvh] transition-opacity duration-1000 ${showSplash ? 'opacity-0 h-0 overflow-hidden' : 'opacity-100'}`}>
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[95%] max-w-5xl">
          <header className="h-16 px-6 flex items-center justify-between glass-panel rounded-full shadow-[0_4px_20px_rgba(0,0,0,0.05)] border border-white/80">
            <div className="flex items-center gap-3">
              <Logo className="w-8 h-8 text-blue-600 drop-shadow-sm" />
              <span className="text-lg font-bold text-slate-800 tracking-tight">1999 Bot Hosting</span>
            </div>
            <nav className="flex items-center gap-3">
              <ThemeToggle />
              <Link href="/login" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-cyan-300 transition-colors">
                Login
              </Link>
              <Link href="/signup" className="btn-3d btn-3d-primary text-sm h-9 px-5 inline-flex items-center justify-center rounded-full">
                Sign Up
              </Link>
            </nav>
          </header>
        </div>

        <main className="flex-1 pt-32">
          <section className="px-6 lg:px-12 py-24 lg:py-32 flex flex-col items-center text-center relative">
            <h1 className="text-5xl lg:text-7xl font-bold text-slate-800 tracking-tighter mb-6 relative drop-shadow-sm">
              Premium infrastructure <br className="hidden lg:block"/> for your applications
            </h1>
            <p className="text-lg lg:text-xl text-slate-600 max-w-2xl mb-10 relative">
              Upload your source code and deploy instantly on dedicated, high-performance slots. Experience light, airy, liquid glass hosting built for serious developers.
            </p>
            <div className="flex items-center gap-4 relative">
              <Link href="/signup" className="btn-3d btn-3d-primary text-base h-14 px-8 inline-flex items-center justify-center rounded-full">
                Get Started
              </Link>
              <Link href="/login" className="btn-3d text-slate-700 dark:text-slate-200 text-base h-14 px-8 inline-flex items-center justify-center rounded-full bg-white/40 dark:bg-transparent">
                Sign in Now!
              </Link>
            </div>
          </section>

          <section className="px-6 lg:px-12 py-24 mt-12 relative z-10">
            <div className="max-w-4xl mx-auto glass-panel p-12 text-center rounded-3xl">
              <div className="w-16 h-16 mx-auto bg-blue-100 rounded-2xl flex items-center justify-center mb-6 shadow-inner border border-white">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-600"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
              </div>
              <h2 className="text-3xl font-bold text-slate-800 mb-4">100% Free Forever</h2>
              <p className="text-slate-600 text-lg mb-8 max-w-2xl mx-auto">We believe in making deployment accessible. All of our premium infrastructure slots are completely free to use. No credit card required. No hidden fees.</p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
                <div className="bg-white/50 p-6 rounded-2xl border border-white shadow-sm">
                  <div className="text-blue-600 font-bold mb-2">Dedicated RAM</div>
                  <p className="text-sm text-slate-600">Resources reserved exclusively for your application's performance.</p>
                </div>
                <div className="bg-white/50 p-6 rounded-2xl border border-white shadow-sm">
                  <div className="text-blue-600 font-bold mb-2">NVMe Storage</div>
                  <p className="text-sm text-slate-600">Lightning fast disk access for databases and temporary files.</p>
                </div>
                <div className="bg-white/50 p-6 rounded-2xl border border-white shadow-sm">
                  <div className="text-blue-600 font-bold mb-2">Any Language</div>
                  <p className="text-sm text-slate-600">Python, Node.js, Java, TypeScript, and more supported out of the box.</p>
                </div>
              </div>
            </div>
          </section>
        </main>

        <footer className="mt-auto py-12 px-6 lg:px-12 relative z-10 glass-panel border-x-0 border-b-0 rounded-none rounded-t-3xl shadow-[0_-8px_30px_rgba(0,0,0,0.02)]">
          <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12">
            <div>
              <div className="flex items-center gap-3 mb-6">
                <Logo className="w-7 h-7 text-blue-600" />
                <span className="text-lg font-bold text-slate-800 tracking-tight">1999 Bot Hosting</span>
              </div>
              <p className="text-sm text-slate-500 max-w-sm font-medium">
                The flagship standard in code deployment and execution. Light, airy, and deeply reliable.
              </p>
            </div>
            <div className="md:justify-self-end">
              <h4 className="text-sm font-bold tracking-widest text-slate-400 uppercase mb-6">DEVELOPER</h4>
              <div className="space-y-4">
                <a href="https://t.me/cozybalenciaga" target="_blank" rel="noreferrer" className="flex items-center gap-3 text-slate-600 hover:text-blue-600 group transition-colors">
                  <div className="w-8 h-8 rounded-lg bg-white shadow-sm border border-white flex items-center justify-center group-hover:scale-105 transition-transform">
                    <SiTelegram className="text-blue-500" />
                  </div>
                  <span className="font-bold text-sm">@cozybalenciaga</span>
                </a>
                <div className="flex items-center gap-3 text-slate-600">
                  <div className="w-8 h-8 rounded-lg bg-white shadow-sm border border-white flex items-center justify-center">
                    <SiDiscord className="text-indigo-500" />
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
