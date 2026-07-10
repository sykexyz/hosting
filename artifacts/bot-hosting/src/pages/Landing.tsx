import { Link } from "wouter";
import { SiDiscord, SiTelegram } from "react-icons/si";

export default function Landing() {
  return (
    <div className="flex flex-col min-h-[100dvh]">
      <header className="px-6 lg:px-12 h-20 flex items-center justify-between border-b border-white/5 bg-background/50 backdrop-blur-lg sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.6)] border border-blue-400 flex items-center justify-center">
            <div className="w-3 h-3 rounded-full bg-white shadow-[0_0_10px_white]"></div>
          </div>
          <span className="text-xl font-bold text-white tracking-tight">1999 Bot Hosting</span>
        </div>
        <nav className="flex items-center gap-4">
          <Link href="/login" className="text-sm font-medium text-white/70 hover:text-white transition-colors">
            Login
          </Link>
          <Link href="/signup" className="btn-3d btn-3d-primary text-sm h-10 px-5 inline-flex items-center justify-center rounded-lg">
            Deploy Now
          </Link>
        </nav>
      </header>

      <main className="flex-1">
        <section className="px-6 lg:px-12 py-24 lg:py-32 flex flex-col items-center text-center relative">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-600/20 blur-[120px] rounded-full pointer-events-none" />
          
          <h1 className="text-5xl lg:text-7xl font-bold text-white tracking-tighter mb-6 relative">
            Premium infrastructure <br className="hidden lg:block"/> for your applications
          </h1>
          <p className="text-lg lg:text-xl text-blue-200/70 max-w-2xl mb-10 relative">
            Upload your source code and deploy instantly on dedicated, high-performance slots. Experience glossy, deep, three-dimensional hosting built for serious developers.
          </p>
          <div className="flex items-center gap-4 relative">
            <Link href="/signup" className="btn-3d btn-3d-primary text-base h-12 px-8 inline-flex items-center justify-center rounded-lg shadow-[0_0_30px_rgba(59,130,246,0.4)]">
              Get Started
            </Link>
            <Link href="/login" className="btn-3d border border-white/10 bg-white/5 hover:bg-white/10 text-white text-base h-12 px-8 inline-flex items-center justify-center rounded-lg shadow-[inset_0_1px_1px_rgba(255,255,255,0.1),0_4px_0_rgba(0,0,0,0.4)]">
              Client Portal
            </Link>
          </div>
        </section>

        <section className="px-6 lg:px-12 py-24 bg-black/20 border-y border-white/5">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold text-white mb-4">Dedicated Performance Slots</h2>
              <p className="text-blue-200/60">Choose the perfect tier for your specific language and workload.</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                { name: "Starter", ram: "512MB", storage: "1GB", price: "$5" },
                { name: "Pro", ram: "2048MB", storage: "2GB", price: "$15", popular: true },
                { name: "Ultra", ram: "4096MB", storage: "5GB", price: "$30" }
              ].map((plan, i) => (
                <div key={i} className={`glass-panel p-8 rounded-2xl flex flex-col ${plan.popular ? 'ring-2 ring-blue-500 shadow-[0_0_30px_rgba(59,130,246,0.2)] scale-105 z-10' : ''}`}>
                  {plan.popular && <div className="text-xs font-bold text-blue-400 tracking-wider uppercase mb-2">Most Popular</div>}
                  <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                  <div className="text-4xl font-bold text-white mb-6">{plan.price}<span className="text-lg text-white/50 font-normal">/mo</span></div>
                  <ul className="space-y-4 mb-8 flex-1">
                    <li className="flex items-center text-blue-100/80">
                      <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mr-3 shadow-[0_0_8px_#3b82f6]"></div>
                      {plan.ram} Dedicated RAM
                    </li>
                    <li className="flex items-center text-blue-100/80">
                      <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mr-3 shadow-[0_0_8px_#3b82f6]"></div>
                      {plan.storage} NVMe Storage
                    </li>
                    <li className="flex items-center text-blue-100/80">
                      <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mr-3 shadow-[0_0_8px_#3b82f6]"></div>
                      Any Language Support
                    </li>
                  </ul>
                  <Link href="/signup" className={`btn-3d w-full h-11 inline-flex items-center justify-center rounded-lg ${plan.popular ? 'btn-3d-primary' : 'bg-white/10 text-white border border-white/20 shadow-[inset_0_1px_1px_rgba(255,255,255,0.1),0_4px_0_rgba(0,0,0,0.4)]'}`}>
                    Select Plan
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-white/5 bg-background/80 py-12 px-6 lg:px-12">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12">
          <div>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-6 h-6 rounded-md bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.6)] border border-blue-400 flex items-center justify-center">
                <div className="w-2 h-2 rounded-full bg-white"></div>
              </div>
              <span className="text-lg font-bold text-white tracking-tight">1999 Bot Hosting</span>
            </div>
            <p className="text-sm text-blue-200/50 max-w-sm">
              The flagship standard in code deployment and execution. Glossy, powerful, and deeply reliable.
            </p>
          </div>
          <div className="md:justify-self-end">
            <h4 className="text-sm font-bold tracking-widest text-white/40 uppercase mb-6">DEVELOPER</h4>
            <div className="space-y-4">
              <a href="https://t.me/cozybalenciaga" target="_blank" rel="noreferrer" className="flex items-center gap-3 text-blue-100 hover:text-white group transition-colors">
                <div className="w-8 h-8 rounded-lg bg-blue-500/20 border border-blue-500/30 flex items-center justify-center group-hover:bg-blue-500/40 transition-colors">
                  <SiTelegram className="text-blue-400" />
                </div>
                <span className="font-medium">@cozybalenciaga</span>
              </a>
              <div className="flex items-center gap-3 text-blue-100/70">
                <div className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center">
                  <SiDiscord className="text-indigo-400" />
                </div>
                <span className="font-medium">Discord</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
