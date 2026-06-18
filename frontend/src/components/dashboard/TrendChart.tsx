"use client";

import { useEffect, useRef, useState } from "react";
import * as echarts from "echarts";
import { fetchApi, api } from "@/lib/api";

interface TrendDataPoint {
  date: string;
  value: number;
}

interface TrendDataResponse {
  metric_type: string;
  period: string;
  data: TrendDataPoint[];
}

interface TrendChartProps {
  className?: string;
}

// ECharts 参数类型
interface EChartsTooltipParam {
  axisValue: string;
  value: number;
}

export default function TrendChart({ className = "" }: TrendChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);
  const [period, setPeriod] = useState<"day" | "week">("day");
  const [metricType, setMetricType] = useState<string>("contractor_count");
  const [data, setData] = useState<TrendDataResponse | null>(null);

  // 获取趋势数据
  useEffect(() => {
    let active = true;
    
    const fetchData = async () => {
      try {
        const response = await fetchApi<TrendDataResponse>(api.trendData(period, metricType));
        if (active) {
          setData(response);
        }
      } catch {
        // 使用模拟数据
        if (active) {
          const mockData: TrendDataPoint[] = [];
          const days = period === "day" ? 30 : 12;
          for (let i = 0; i < days; i++) {
            const date = new Date();
            date.setDate(date.getDate() - (days - i - 1));
            const baseValue = 500;
            const value = baseValue + Math.floor(i * 10 + Math.random() * 20);
            mockData.push({
              date: date.toISOString().split("T")[0],
              value: value,
            });
          }
          setData({
            metric_type: metricType,
            period: period,
            data: mockData,
          });
        }
      }
    };
    
    fetchData();
    
    return () => {
      active = false;
    };
  }, [period, metricType]);

  // 渲染图表
  useEffect(() => {
    if (!chartRef.current || !data) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    const dates = data.data.map((item) => item.date);
    const values = data.data.map((item) => item.value);

    // 指标名称映射
    const metricNames: Record<string, string> = {
      contractor_count: "承包方总数",
      surveyed_count: "已摸底户数",
      audited_count: "已审核户数",
      completed_count: "已完成户数",
      issuer_count: "发包方总数",
    };

    const metricName = metricNames[data.metric_type] || data.metric_type;

    const option: echarts.EChartsOption = {
      tooltip: {
        trigger: "axis",
        backgroundColor: "rgba(10,20,50,0.85)",
        borderColor: "rgba(32,80,160,0.35)",
        textStyle: {
          color: "#e8f0ff",
          fontSize: 12,
        },
        formatter: (params: EChartsTooltipParam[]) => {
          const point = params[0];
          return `${point.axisValue}<br/>${metricName}: <strong style="color:#00d4ff">${point.value}</strong>`;
        },
      },
      legend: {
        data: [metricName],
        top: 0,
        textStyle: {
          color: "rgba(180,200,240,0.75)",
          fontSize: 11,
        },
        itemWidth: 10,
        itemHeight: 10,
      },
      grid: {
        left: "3%",
        right: "4%",
        bottom: "10%",
        top: "15%",
        containLabel: true,
      },
      xAxis: {
        type: "category",
        data: dates,
        axisLabel: {
          color: "rgba(180,200,240,0.75)",
          fontSize: 10,
          interval: period === "day" ? 6 : 0,
          rotate: period === "day" ? 30 : 0,
        },
        axisLine: {
          lineStyle: {
            color: "rgba(32,80,160,0.3)",
          },
        },
        axisTick: {
          show: false,
        },
      },
      yAxis: {
        type: "value",
        name: metricName,
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
          name: metricName,
          type: "line",
          data: values,
          smooth: true,
          symbol: "circle",
          symbolSize: 6,
          lineStyle: {
            color: "#00d4ff",
            width: 2,
          },
          itemStyle: {
            color: "#00d4ff",
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: "rgba(0,212,255,0.3)" },
              { offset: 1, color: "rgba(0,212,255,0.05)" },
            ]),
          },
          emphasis: {
            focus: "series",
            itemStyle: {
              shadowBlur: 10,
              shadowColor: "rgba(0,212,255,0.5)",
            },
          },
        },
      ],
    };

    chartInstance.current.setOption(option);

    const handleResize = () => {
      chartInstance.current?.resize();
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [data, period]);

  // 清理图表实例
  useEffect(() => {
    return () => {
      chartInstance.current?.dispose();
      chartInstance.current = null;
    };
  }, []);

  return (
    <div className={`flex flex-col ${className}`}>
      {/* 控制面板 */}
      <div className="flex items-center gap-[12px] mb-[10px]">
        {/* 周期选择 */}
        <div className="flex items-center gap-[8px]">
          <span className="text-[11px]" style={{ color: "var(--text-secondary)" }}>
            周期:
          </span>
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value as "day" | "week")}
            className="px-[8px] py-[4px] rounded-[4px] text-[12px]"
            style={{
              background: "rgba(10,20,50,0.7)",
              border: "1px solid var(--border-card)",
              color: "var(--text-primary)",
            }}
          >
            <option value="day">按日</option>
            <option value="week">按周</option>
          </select>
        </div>

        {/* 指标选择 */}
        <div className="flex items-center gap-[8px]">
          <span className="text-[11px]" style={{ color: "var(--text-secondary)" }}>
            指标:
          </span>
          <select
            value={metricType}
            onChange={(e) => setMetricType(e.target.value)}
            className="px-[8px] py-[4px] rounded-[4px] text-[12px]"
            style={{
              background: "rgba(10,20,50,0.7)",
              border: "1px solid var(--border-card)",
              color: "var(--text-primary)",
            }}
          >
            <option value="contractor_count">承包方总数</option>
            <option value="surveyed_count">已摸底户数</option>
            <option value="audited_count">已审核户数</option>
            <option value="completed_count">已完成户数</option>
          </select>
        </div>
      </div>

      {/* 图表区域 */}
      {!data ? (
        <div
          className="w-full h-[200px] flex items-center justify-center animate-pulse"
          style={{
            background:
              "linear-gradient(90deg, rgba(32,80,160,0.2) 25%, rgba(32,80,160,0.35) 50%, rgba(32,80,160,0.2) 75%)",
            backgroundSize: "200% 100%",
          }}
        >
          <span style={{ color: "var(--text-muted)" }}>加载中...</span>
        </div>
      ) : (
        <div ref={chartRef} className="w-full h-[200px]" />
      )}
    </div>
  );
}