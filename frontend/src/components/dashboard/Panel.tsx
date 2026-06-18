"use client";

interface PanelProps {
  title: string;
  children: React.ReactNode;
  className?: string;
}

export default function Panel({ title, children, className = "" }: PanelProps) {
  return (
    <div 
      className={`flex flex-col rounded-lg border ${className}`}
      style={{
        background: "var(--bg-card)",
        borderColor: "var(--border-card)",
        boxShadow: "var(--shadow-card)",
      }}
    >
      {/* Header */}
      <div 
        className="px-[14px] py-[10px] border-b"
        style={{ borderColor: "var(--border-divider)" }}
      >
        <span 
          className="text-[13px] font-semibold tracking-[1px]"
          style={{ color: "var(--accent-cyan)" }}
        >
          ▶ {title}
        </span>
      </div>
      {/* Body */}
      <div className="p-[12px_14px] flex-1">
        {children}
      </div>
    </div>
  );
}