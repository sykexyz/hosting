import { useState, useEffect } from "react";

function formatUptime(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}m ${s}s`;
  }
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return `${h}h ${m}m`;
}

export function UptimeTimer({ createdAt, running }: { createdAt: string; running: boolean }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (!running) { setElapsed(0); return; }
    const start = new Date(createdAt).getTime();
    const tick = () => {
      const diff = Math.floor((Date.now() - start) / 1000);
      setElapsed(Math.max(0, diff));
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [running, createdAt]);

  if (!running) return null;

  return (
    <span className="text-[10px] font-mono text-green-400/80 bg-green-400/8 border border-green-400/15 px-1.5 py-0.5 rounded-md">
      ↑ {formatUptime(elapsed)}
    </span>
  );
}
