import { useRef, useState, useCallback } from "react";

interface CodeInputProps {
  value: string;
  onChange: (v: string) => void;
  height?: string;
}

export default function CodeInput({ value, onChange, height = "260px" }: CodeInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const lineNumRef  = useRef<HTMLDivElement>(null);

  const lines = value.split("\n");
  const lineCount = Math.max(lines.length, 1);

  // Keep line-number gutter scroll in sync with textarea scroll
  const handleScroll = useCallback(() => {
    if (lineNumRef.current && textareaRef.current) {
      lineNumRef.current.scrollTop = textareaRef.current.scrollTop;
    }
  }, []);

  // Tab key inserts 4 spaces instead of focusing the next element
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Tab") {
      e.preventDefault();
      const el = e.currentTarget;
      const start = el.selectionStart;
      const end   = el.selectionEnd;
      const next  = value.substring(0, start) + "    " + value.substring(end);
      onChange(next);
      // restore cursor after state update
      requestAnimationFrame(() => {
        el.selectionStart = el.selectionEnd = start + 4;
      });
    }
  }, [value, onChange]);

  return (
    <div
      className="flex font-mono text-sm rounded-xl overflow-hidden"
      style={{ height, background: "#0a0a0d", border: "1px solid rgba(255,255,255,0.08)" }}
    >
      {/* Line numbers */}
      <div
        ref={lineNumRef}
        aria-hidden="true"
        className="select-none overflow-hidden flex-shrink-0"
        style={{
          width: "3rem",
          paddingTop: "10px",
          paddingBottom: "10px",
          background: "rgba(255,255,255,0.02)",
          borderRight: "1px solid rgba(255,255,255,0.06)",
          textAlign: "right",
          lineHeight: "1.6",
          color: "rgba(255,255,255,0.2)",
          fontSize: "12px",
          overflowY: "hidden",
        }}
      >
        {Array.from({ length: lineCount }, (_, i) => (
          <div key={i} style={{ paddingRight: "10px" }}>{i + 1}</div>
        ))}
      </div>

      {/* Actual textarea */}
      <textarea
        ref={textareaRef}
        value={value}
        onChange={e => onChange(e.target.value)}
        onScroll={handleScroll}
        onKeyDown={handleKeyDown}
        spellCheck={false}
        autoCorrect="off"
        autoCapitalize="off"
        className="flex-1 resize-none outline-none bg-transparent text-white/85 placeholder-white/20"
        style={{
          padding: "10px 14px",
          lineHeight: "1.6",
          fontSize: "13px",
          fontFamily: "'Spline Sans Mono', 'Fira Code', 'Courier New', monospace",
          overflowY: "auto",
          whiteSpace: "pre",
          overflowX: "auto",
          tabSize: 4,
        }}
        placeholder="# Paste your code here"
      />
    </div>
  );
}
