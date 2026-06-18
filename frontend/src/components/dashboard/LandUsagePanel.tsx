"use client";

import { useLandUsage } from "@/hooks/useIndicators";
import { LandUsageItem } from "@/hooks/useIndicators";

// 用途类别配置（固定4类）
const usageCategories = [
  { name: "种植业", code: "01", icon: "🌾" },
  { name: "林业", code: "02", icon: "🌲" },
  { name: "畜牧业", code: "03", icon: "🐄" },
  { name: "渔业", code: "04", icon: "🐟" },
];

// Skeleton 动画组件
function Skeleton({ className }: { className?: string }) {
  return (
    <div 
      className={`${className} animate-pulse`}
      style={{ 
        background: "linear-gradient(90deg, rgba(32,80,160,0.2) 25%, rgba(32,80,160,0.35) 50%, rgba(32,80,160,0.2) 75%)",
        backgroundSize: "200% 100%",
      }}
    />
  );
}

// 单个用途统计卡片
function UsageCard({ 
  name, 
  count, 
  isLoading 
}: { 
  name: string; 
  count: number; 
  isLoading: boolean;
}) {
  if (isLoading) {
    return (
      <div 
        className="flex flex-col items-center justify-center p-3 rounded-md border"
        style={{
          background: "var(--bg-usage-card)",
          borderColor: "rgba(32,80,160,0.2)",
        }}
      >
        <Skeleton className="w-16 h-3 rounded mb-2" />
        <Skeleton className="w-12 h-6 rounded" />
      </div>
    );
  }
  
  return (
    <div 
      className="flex flex-col items-center justify-center p-3 rounded-md border"
      style={{
        background: "var(--bg-usage-card)",
        borderColor: "rgba(32,80,160,0.2)",
      }}
    >
      <span 
        className="text-[11px] mb-1"
        style={{ color: "var(--text-secondary)" }}
      >
        {name}
      </span>
      <span 
        className="text-[20px] font-bold"
        style={{ color: "var(--accent-cyan)" }}
      >
        {count}
      </span>
    </div>
  );
}

export default function LandUsagePanel() {
  const { data, isLoading, error } = useLandUsage();
  
  // 根据用途编码获取数量
  const getCountByCode = (code: string): number => {
    const item = data.items.find((item: LandUsageItem) => item.code === code);
    return item?.count || 0;
  };
  
  if (error) {
    return (
      <div className="grid grid-cols-2 gap-2">
        {usageCategories.map((cat) => (
          <UsageCard 
            key={cat.code}
            name={cat.name}
            count={0}
            isLoading={false}
          />
        ))}
      </div>
    );
  }
  
  return (
    <div className="grid grid-cols-2 gap-2">
      {usageCategories.map((cat) => (
        <UsageCard 
          key={cat.code}
          name={cat.name}
          count={getCountByCode(cat.code)}
          isLoading={isLoading}
        />
      ))}
    </div>
  );
}