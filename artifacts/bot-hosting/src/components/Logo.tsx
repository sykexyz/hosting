import React from 'react';

export const Logo = ({ className }: { className?: string }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 120 120"
      className={className || "w-8 h-8"}
      fill="none"
    >
      <defs>
        <linearGradient id="botGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#ffffff" />
          <stop offset="100%" stopColor="#888888" />
        </linearGradient>
        <linearGradient id="visorGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#aaaaaa" />
          <stop offset="50%" stopColor="#ffffff" />
          <stop offset="100%" stopColor="#aaaaaa" />
        </linearGradient>
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
        <filter id="innerGlow" x="-10%" y="-10%" width="120%" height="120%">
          <feGaussianBlur in="SourceAlpha" stdDeviation="2" result="blur" />
          <feOffset dy="1" dx="0" />
          <feComposite in2="SourceAlpha" operator="arithmetic" k2="-1" k3="1" result="shadowDiff" />
          <feFlood floodColor="white" floodOpacity="0.6" />
          <feComposite in2="shadowDiff" operator="in" />
          <feComposite in2="SourceGraphic" operator="over" />
        </filter>
      </defs>

      {/* Outer Glow / Halo */}
      <circle cx="60" cy="60" r="50" fill="url(#botGradient)" opacity="0.1" filter="url(#glow)" />

      {/* Bot Head */}
      <rect x="25" y="35" width="70" height="60" rx="16" fill="url(#botGradient)" filter="url(#innerGlow)" stroke="#ffffff" strokeWidth="1.5" strokeOpacity="0.4" />

      {/* Antenna base */}
      <path d="M50 35 L70 35 L65 25 L55 25 Z" fill="#555555" stroke="#ffffff" strokeWidth="1" strokeOpacity="0.5" />

      {/* Antenna stick */}
      <line x1="60" y1="25" x2="60" y2="12" stroke="#ffffff" strokeWidth="2" />

      {/* Antenna ball */}
      <circle cx="60" cy="12" r="4" fill="#ffffff" filter="url(#glow)" />

      {/* Ears / Side nodes */}
      <rect x="18" y="55" width="7" height="20" rx="3" fill="#666666" stroke="#ffffff" strokeWidth="1" />
      <rect x="95" y="55" width="7" height="20" rx="3" fill="#666666" stroke="#ffffff" strokeWidth="1" />

      {/* Visor Background */}
      <rect x="35" y="50" width="50" height="20" rx="10" fill="#111111" stroke="#ffffff" strokeWidth="1" strokeOpacity="0.3" />

      {/* Visor Glow / Eyes */}
      <rect x="40" y="56" width="40" height="8" rx="4" fill="url(#visorGradient)" filter="url(#glow)" />

      {/* Jaw detail */}
      <line x1="45" y1="82" x2="75" y2="82" stroke="#888888" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
};
