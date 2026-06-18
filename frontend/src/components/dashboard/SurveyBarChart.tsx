"use client";

import { useEffect, useRef } from "react";
import * as echarts from "echarts";
import { useSurveyStats } from "@/hooks/useIndicators";

// Skeleton 动画组件
function ChartSkeleton() {
  return (
    <div 
      className="w-full h-[200px] flex items-center justify-center animate-pulse"
      style={{ 
        background: "linear-gradient(90deg, rgba(32,80,160,0.2) 25%, rgba(32,80,160,0.35) 50%, rgba(32,80,160,0.2) 75%)",
        backgroundSize: "200% 100%",
      }}
    >
      <span style={{ color: "var(--text-muted)" }}>加载中...</span>
    </div>
  );
}

interface SurveyBarChartProps {
  onVillageClick?: (code: string, name: string) => void;
}

export default function SurveyBarChart({ onVillageClick }: SurveyBarChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);
  const { data, isLoading, error } = useSurveyStats();
  
  useEffect(() => {
    if (!chartRef.current || isLoading || error) return;
    
    // 初始化图表
    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }
    
    // 准备数据
    const villageNames = data.items.map(item => item.village_name);
    const villageCodes = data.items.map(item => item.village_code);
    const reportedCounts = data.items.map(item => item.reported_count);
    const auditedCounts = data.items.map(item => item.audited_count);
    
    // 配置图表
    const option: echarts.EChartsOption = {
      tooltip: {
        trigger: "axis",
        axisPointer: {
          type: "shadow",
        },
        backgroundColor: "rgba(10,20,50,0.85)",
        borderColor: "rgba(32,80,160,0.35)",
        textStyle: {
          color: "#e8f0ff",
          fontSize: 12,
        },
      },
      legend: {
        data: ["已上报", "已审核"],
        top: 0,
        textStyle: {
          color: "rgba(180,200,240,0.75)",
          fontSize: 11,
        },
        itemWidth: 10,
        itemHeight: 10,
        itemGap: 16,
      },
      grid: {
        left: "3%",
        right: "4%",
        bottom: "15%",
        top: "15%",
        containLabel: true,
      },
      xAxis: {
        type: "category",
        data: villageNames,
        axisLabel: {
          color: "rgba(180,200,240,0.75)",
          fontSize: 9,
          interval: 0,
          rotate: villageNames.length > 5 ? 30 : 0,
        },
        axisLine: {
          lineStyle: {
            color: "rgba(32,80,160,0.3)",
          },
        },
        axisTick: {
          show: false,
        },
        triggerEvent: true,
      },
      yAxis: {
        type: "value",
        name: "户数",
        nameTextStyle: {
          color: "rgba(180,200,240,0.75)",
          fontSize: 11,
        },
        axisLabel: {
          color: "rgba(180,200,240,0.75)",
          fontSize: 11,
        },
        axisLine: {
          show: false,
        },
        splitLine: {
          lineStyle: {
            color: "rgba(32,80,160,0.1)",
          },
        },
      },
      series: [
        {
          name: "已上报",
          type: "bar",
          data: reportedCounts,
          barWidth: "35%",
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: "#ffb830" },
              { offset: 1, color: "#e09500" },
            ]),
            borderRadius: [3, 3, 0, 0],
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: "rgba(255,184,48,0.3)",
            },
          },
        },
        {
          name: "已审核",
          type: "bar",
          data: auditedCounts,
          barWidth: "35%",
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: "#0090ff" },
              { offset: 1, color: "#0050cc" },
            ]),
            borderRadius: [3, 3, 0, 0],
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: "rgba(0,144,255,0.3)",
            },
          },
        },
      ],
    };
    
    chartInstance.current.setOption(option);
    
    // 点击事件处理
    if (onVillageClick) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      chartInstance.current.on("click", (params: any) => {
        if (params.componentType === "xAxis") {
          const index = params.value ? villageNames.indexOf(String(params.value)) : -1;
          if (index >= 0 && villageCodes[index]) {
            onVillageClick(villageCodes[index], villageNames[index]);
          }
        }
      });
    }
    
    // 窗口大小变化时重新调整
    const handleResize = () => {
      chartInstance.current?.resize();
    };
    window.addEventListener("resize", handleResize);
    
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [data, isLoading, error, onVillageClick]);
  
  // 清理图表实例
  useEffect(() => {
    return () => {
      chartInstance.current?.dispose();
      chartInstance.current = null;
    };
  }, []);
  
  if (isLoading) {
    return <ChartSkeleton />;
  }
  
  if (error) {
    return (
      <div 
        className="w-full h-[200px] flex items-center justify-center"
        style={{ color: "var(--text-muted)" }}
      >
        加载失败
      </div>
    );
  }
  
  if (data.items.length === 0) {
    return (
      <div 
        className="w-full h-[200px] flex items-center justify-center"
        style={{ color: "var(--text-muted)" }}
      >
        暂无数据
      </div>
    );
  }
  
  return (
    <div 
      ref={chartRef}
      className="w-full h-[200px]"
    />
  );
}