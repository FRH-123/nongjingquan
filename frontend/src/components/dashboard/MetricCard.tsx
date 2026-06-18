"use client";

type IconVariant = "cyan" | "gold" | "green" | "purple" | "red";

interface MetricCardProps {
  label: string;
  value: number | string;
  iconVariant?: IconVariant;
  isLoading?: boolean;
}

const variantStyles: Record<IconVariant, { gradient: string; shadow: string }> = {
  cyan: {
    gradient: "var(--gradient-cyan)",
    shadow: "0 4px 12px rgba(0,212,255,0.3)",
  },
  gold: {
    gradient: "var(--gradient-gold)",
    shadow: "0 4px 12px rgba(255,184,48,0.3)",
  },
  green: {
    gradient: "var(--gradient-green)",
    shadow: "0 4px 12px rgba(0,230,118,0.3)",
  },
  purple: {
    gradient: "var(--gradient-purple)",
    shadow: "0 4px 12px rgba(168,85,247,0.3)",
  },
  red: {
    gradient: "var(--gradient-red)",
    shadow: "0 4px 12px rgba(255,71,87,0.3)",
  },
};

// Skeleton 动画组件
function Skeleton({ className }: { className?: string }) {
  return (
    <div 
      className={`${className} animate-pulse`}
      style={{ 
        background: "linear-gradient(90deg, rgba(32,80,160,0.2) 25%, rgba(32,80,160,0.35) 50%, rgba(32,80,160,0.2) 75%)",
        backgroundSize: "200% 100%",
        animation: "shimmer 1.5s infinite",
      }}
    />
  );
}

export default function MetricCard({ label, value, iconVariant = "cyan", isLoading = false }: MetricCardProps) {
  const style = variantStyles[iconVariant];

  if (isLoading) {
    return (
      <div 
        className="flex items-center gap-[14px] p-[14px_18px] rounded-lg border"
        style={{
          background: "var(--bg-card)",
          borderColor: "var(--border-card)",
          boxShadow: "var(--shadow-card)",
        }}
      >
        {/* 图标容器 skeleton */}
        <Skeleton className="w-11 h-11 rounded-[10px]" />
        {/* 文字区域 skeleton */}
        <div className="flex flex-col gap-2">
          <Skeleton className="w-20 h-3 rounded" />
          <Skeleton className="w-16 h-7 rounded" />
        </div>
      </div>
    );
  }

  return (
    <div 
      className="flex items-center gap-[14px] p-[14px_18px] rounded-lg border transition-all duration-300 hover:border-[var(--border-highlight)]"
      style={{
        background: "var(--bg-card)",
        borderColor: "var(--border-card)",
        boxShadow: "var(--shadow-card)",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = "var(--glow-cyan)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = "var(--shadow-card)";
      }}
    >
      {/* 图标容器 */}
      <div 
        className="w-11 h-11 rounded-[10px] flex items-center justify-center"
        style={{
          background: style.gradient,
          boxShadow: style.shadow,
        }}
      >
        {/* 占位图标 */}
        <div className="w-5 h-5 rounded bg-white/30" />
      </div>
      {/* 文字区域 */}
      <div className="flex flex-col">
        <span 
          className="text-[12px] tracking-[1px]"
          style={{ color: "var(--text-secondary)" }}
        >
          {label}
        </span>
        <span 
          className="text-[26px] font-bold tracking-[1px]"
          style={{ color: "var(--text-value)" }}
        >
          {value}
        </span>
      </div>
    </div>
  );
}