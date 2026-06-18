"use client";

import MetricCard from "./MetricCard";
import { useOverview, OverviewIndicator } from "@/hooks/useIndicators";

// 指标卡配置
const metricConfig: Array<{
  label: string;
  key: keyof OverviewIndicator;
  variant: "cyan" | "gold" | "green" | "purple" | "red";
}> = [
  { label: "发包方总数", key: "issuer_count", variant: "cyan" },
  { label: "承包方总数", key: "contractor_count", variant: "gold" },
  { label: "已摸底户数", key: "surveyed_count", variant: "green" },
  { label: "已内业审核数", key: "audited_count", variant: "purple" },
  { label: "已完成户数", key: "completed_count", variant: "red" },
];

export default function MetricRow() {
  const { data, isLoading, error } = useOverview();

  if (error) {
    return (
      <div className="grid grid-cols-5 gap-[12px]">
        {metricConfig.map((config) => (
          <MetricCard
            key={config.key}
            label={config.label}
            value={0}
            iconVariant={config.variant}
          />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-5 gap-[12px]">
      {metricConfig.map((config) => (
        <MetricCard
          key={config.key}
          label={config.label}
          value={isLoading ? 0 : (data[config.key] ?? 0)}
          iconVariant={config.variant}
          isLoading={isLoading}
        />
      ))}
    </div>
  );
}