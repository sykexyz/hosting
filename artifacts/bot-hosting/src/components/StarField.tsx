import { useEffect, useRef } from "react";

interface Star {
  x: number;
  y: number;
  size: number;
  opacity: number;
  speed: number;
  twinkleOffset: number;
  color: string;
  isBand: boolean;
}

const STAR_COLORS = [
  "255,255,255",
  "200,210,255",
  "255,220,200",
  "180,200,255",
  "240,230,255",
  "255,255,220",
];

export function StarField() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>(0);
  const starsRef = useRef<Star[]>([]);
  const timeRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      buildStars();
    };

    function buildStars() {
      const w = canvas!.width;
      const h = canvas!.height;
      const stars: Star[] = [];
      const total = Math.floor((w * h) / 1400);

      for (let i = 0; i < total; i++) {
        // Band probability: stars denser along a diagonal stripe (Milky Way)
        const bandAngle = 0.42; // radians tilt
        const bandCenter = 0.52;
        const bandWidth = 0.28;

        let x: number, y: number, isBand: boolean;

        if (Math.random() < 0.55) {
          // place in milky way band
          const t = Math.random();
          const bandT = Math.random() * bandWidth - bandWidth / 2;
          const along = t * (w + h);
          const across = (bandCenter + bandT) * h;
          x = along * Math.cos(bandAngle) - across * Math.sin(bandAngle);
          y = along * Math.sin(bandAngle) + across * Math.cos(bandAngle);
          x = ((x % w) + w) % w;
          y = ((y % h) + h) % h;
          isBand = true;
        } else {
          x = Math.random() * w;
          y = Math.random() * h;
          isBand = false;
        }

        const size = isBand
          ? Math.random() < 0.07 ? 1.5 + Math.random() : 0.4 + Math.random() * 0.8
          : Math.random() < 0.04 ? 1.8 + Math.random() * 0.8 : 0.3 + Math.random() * 0.9;

        const colorIdx = isBand
          ? Math.floor(Math.random() * STAR_COLORS.length)
          : Math.random() < 0.8 ? 0 : Math.floor(Math.random() * STAR_COLORS.length);

        stars.push({
          x, y, size,
          opacity: isBand ? 0.3 + Math.random() * 0.65 : 0.15 + Math.random() * 0.55,
          speed: 0.3 + Math.random() * 1.2,
          twinkleOffset: Math.random() * Math.PI * 2,
          color: STAR_COLORS[colorIdx]!,
          isBand,
        });
      }

      starsRef.current = stars;
    }

    function draw(t: number) {
      const w = canvas!.width;
      const h = canvas!.height;
      ctx!.clearRect(0, 0, w, h);

      // Milky Way nebula glow — soft diagonal band
      const bandGrad = ctx!.createLinearGradient(0, h * 0.1, w, h * 0.9);
      bandGrad.addColorStop(0, "rgba(0,0,0,0)");
      bandGrad.addColorStop(0.3, "rgba(80,60,120,0.04)");
      bandGrad.addColorStop(0.45, "rgba(120,100,180,0.07)");
      bandGrad.addColorStop(0.55, "rgba(100,80,160,0.06)");
      bandGrad.addColorStop(0.7, "rgba(60,50,100,0.03)");
      bandGrad.addColorStop(1, "rgba(0,0,0,0)");
      ctx!.fillStyle = bandGrad;
      ctx!.fillRect(0, 0, w, h);

      // Secondary nebula pockets
      const neb1 = ctx!.createRadialGradient(w * 0.3, h * 0.35, 0, w * 0.3, h * 0.35, w * 0.25);
      neb1.addColorStop(0, "rgba(100,80,200,0.04)");
      neb1.addColorStop(1, "rgba(0,0,0,0)");
      ctx!.fillStyle = neb1;
      ctx!.fillRect(0, 0, w, h);

      const neb2 = ctx!.createRadialGradient(w * 0.7, h * 0.65, 0, w * 0.7, h * 0.65, w * 0.2);
      neb2.addColorStop(0, "rgba(80,120,200,0.035)");
      neb2.addColorStop(1, "rgba(0,0,0,0)");
      ctx!.fillStyle = neb2;
      ctx!.fillRect(0, 0, w, h);

      // Draw stars
      for (const star of starsRef.current) {
        const twinkle = 0.6 + 0.4 * Math.sin(t * star.speed * 0.001 + star.twinkleOffset);
        const alpha = star.opacity * twinkle;

        ctx!.beginPath();
        ctx!.arc(star.x, star.y, star.size, 0, Math.PI * 2);
        ctx!.fillStyle = `rgba(${star.color},${alpha.toFixed(3)})`;
        ctx!.fill();

        // Glow on bright stars
        if (star.size > 1.2) {
          const glow = ctx!.createRadialGradient(star.x, star.y, 0, star.x, star.y, star.size * 3.5);
          glow.addColorStop(0, `rgba(${star.color},${(alpha * 0.4).toFixed(3)})`);
          glow.addColorStop(1, "rgba(0,0,0,0)");
          ctx!.beginPath();
          ctx!.arc(star.x, star.y, star.size * 3.5, 0, Math.PI * 2);
          ctx!.fillStyle = glow;
          ctx!.fill();
        }
      }
    }

    function loop(t: number) {
      timeRef.current = t;
      draw(t);
      animRef.current = requestAnimationFrame(loop);
    }

    resize();
    window.addEventListener("resize", resize);
    animRef.current = requestAnimationFrame(loop);

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(animRef.current);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{ background: "#050507" }}
    />
  );
}
