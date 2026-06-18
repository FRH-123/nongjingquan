"use client";

import { useEffect, useRef, useState } from "react";
import * as echarts from "echarts";
import { fetchApi, api } from "@/lib/api";

interface VillageDetail {
  village_code: string;
  village_name: string;
  total_households: number;
  surveyed_count: number;
  audited_count: number;
  completed_count: number;
  in_progress_count: number;
  survey_rate: number;
  audit_rate: number;
  complete_rate: number;
  land_usage: {
    category: string;
    count: number;
  }[];
  family_members: {
    total: number;
    male: number;
    female: number;
  };
}

interface VillageDetailModalProps {
  villageCode: string;
  villageName: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function VillageDetailModal({
  villageCode,
  villageName,
  isOpen,
  onClose,
}: VillageDetailModalProps) {
  const [detail, setDetail] = useState<VillageDetail | null>(null);
  const pieChartRef = useRef<HTMLDivElement>(null);
  const pieChartInstance = useRef<echarts.ECharts | null>(null);

  // 获取村组详情数据
  useEffect(() => {
    if (!isOpen || !villageCode) {
      return;
    }
    
    let active = true;
    
    const fetchData = async () => {
      try {
        const data = await fetchApi<VillageDetail>(api.villageDetail(villageCode));
        if (active) {
          setDetail(data);
        }
      } catch {
        // 使用模拟数据
        if (active) {
          setDetail({
            village_code: villageCode,
            village_name: villageName,
            total_households: 120,
            surveyed_count: 95,
            audited_count: 80,
            completed_count: 45,
            in_progress_count: 35,
            survey_rate: 79.17,
            audit_rate: 84.21,
            complete_rate: 37.5,
            land_usage: [
              { category: "种植业", count: 380 },
              { category: "林业", count: 15 },
              { category: "畜牧业", count: 8 },
              { category: "渔业", count: 5 },
            ],
            family_members: {
              total: 380,
              male: 195,
              female: 185,
            },
          });
        }
      }
    };
    
    fetchData();
    
    return () => {
      active = false;
    };
  }, [isOpen, villageCode, villageName]);

  // 渲染饼图
  useEffect(() => {
    if (!pieChartRef.current || !detail || !isOpen) return;

    if (!pieChartInstance.current) {
      pieChartInstance.current = echarts.init(pieChartRef.current);
    }

    const pieData = detail.land_usage.map((item) => ({
      name: item.category,
      value: item.count,
    }));

    const option: echarts.EChartsOption = {
      tooltip: {
        trigger: "item",
        backgroundColor: "rgba(10,20,50,0.85)",
        borderColor: "rgba(32,80,160,0.35)",
        textStyle: {
          color: "#e8f0ff",
          fontSize: 12,
        },
        formatter: "{b}: {c} ({d}%)",
      },
      legend: {
        orient: "vertical",
        right: 10,
        top: "center",
        textStyle: {
          color: "rgba(180,200,240,0.75)",
          fontSize: 11,
        },
        itemWidth: 10,
        itemHeight: 10,
      },
      series: [
        {
          type: "pie",
          radius: ["40%", "70%"],
          center: ["35%", "50%"],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 4,
            borderColor: "rgba(32,80,160,0.3)",
            borderWidth: 1,
          },
          label: {
            show: false,
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 12,
              fontWeight: "bold",
              color: "#e8f0ff",
            },
          },
          data: pieData,
          color: ["#4fc3f7", "#81c784", "#ff8a65", "#7986cb"],
        },
      ],
    };

    pieChartInstance.current.setOption(option);

    const handleResize = () => {
      pieChartInstance.current?.resize();
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [detail, isOpen]);

  // 清理图表实例
  useEffect(() => {
    return () => {
      pieChartInstance.current?.dispose();
      pieChartInstance.current = null;
    };
  }, []);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      onClick={onClose}
    >
      {/* 背景遮罩 */}
      <div
        className="absolute inset-0 bg-black/60"
        style={{ backdropFilter: "blur(4px)" }}
      />

      {/* 弹窗内容 */}
      <div
        className="relative w-[600px] max-h-[80vh] overflow-auto rounded-lg"
        style={{
          background: "var(--bg-card)",
          border: "1px solid var(--border-highlight)",
          boxShadow: "var(--glow-cyan)",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div
          className="px-[18px] py-[14px] border-b flex items-center justify-between"
          style={{ borderColor: "var(--border-divider)" }}
        >
          <h2
            className="text-[16px] font-bold tracking-[1px]"
            style={{ color: "var(--accent-cyan)" }}
          >
            {villageName} 详情
          </h2>
          <button
            onClick={onClose}
            className="w-[28px] h-[28px] flex items-center justify-center rounded"
            style={{
              background: "rgba(255,71,87,0.15)",
              border: "1px solid rgba(255,71,87,0.3)",
              color: "#ff4757",
            }}
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div className="p-[18px]">
          {!detail ? (
            <div className="flex items-center justify-center h-[200px]">
              <span style={{ color: "var(--text-muted)" }}>加载中...</span>
            </div>
          ) : (
            <>
              {/* 5 个核心指标 */}
              <div className="grid grid-cols-5 gap-[12px] mb-[20px]">
                <div
                  className="flex flex-col items-center p-[12px] rounded-[6px]"
                  style={{
                    background: "rgba(10,20,50,0.5)",
                    border: "1px solid rgba(32,80,160,0.2)",
                  }}
                >
                  <span className="text-[11px]" style={{ color: "var(--text-secondary)" }}>
                    总户数
                  </span>
                  <span className="text-[20px] font-bold" style={{ color: "#fff" }}>
                    {detail.total_households}
                  </span>
                </div>
                <div
                  className="flex flex-col items-center p-[12px] rounded-[6px]"
                  style={{
                    background: "rgba(10,20,50,0.5)",
                    border: "1px solid rgba(32,80,160,0.2)",
                  }}
                >
                  <span className="text-[11px]" style={{ color: "var(--text-secondary)" }}>
                    已摸底
                  </span>
                  <span className="text-[20px] font-bold" style={{ color: "var(--accent-green)" }}>
                    {detail.surveyed_count}
                  </span>
                </div>
                <div
                  className="flex flex-col items-center p-[12px] rounded-[6px]"
                  style={{
                    background: "rgba(10,20,50,0.5)",
                    border: "1px solid rgba(32,80,160,0.2)",
                  }}
                >
                  <span className="text-[11px]" style={{ color: "var(--text-secondary)" }}>
                    已审核
                  </span>
                  <span className="text-[20px] font-bold" style={{ color: "var(--accent-purple)" }}>
                    {detail.audited_count}
                  </span>
                </div>
                <div
                  className="flex flex-col items-center p-[12px] rounded-[6px]"
                  style={{
                    background: "rgba(10,20,50,0.5)",
                    border: "1px solid rgba(32,80,160,0.2)",
                  }}
                >
                  <span className="text-[11px]" style={{ color: "var(--text-secondary)" }}>
                    已完成
                  </span>
                  <span className="text-[20px] font-bold" style={{ color: "var(--accent-red)" }}>
                    {detail.completed_count}
                  </span>
                </div>
                <div
                  className="flex flex-col items-center p-[12px] rounded-[6px]"
                  style={{
                    background: "rgba(10,20,50,0.5)",
                    border: "1px solid rgba(32,80,160,0.2)",
                  }}
                >
                  <span className="text-[11px]" style={{ color: "var(--text-secondary)" }}>
                    流转中
                  </span>
                  <span className="text-[20px] font-bold" style={{ color: "var(--accent-gold)" }}>
                    {detail.in_progress_count}
                  </span>
                </div>
              </div>

              {/* 3 条进度条 */}
              <div className="mb-[20px]">
                <div className="mb-[12px]">
                  <div className="flex justify-between mb-[4px]">
                    <span className="text-[12px]" style={{ color: "var(--text-secondary)" }}>
                      摸底进度
                    </span>
                    <span className="text-[12px] font-bold" style={{ color: "var(--accent-green)" }}>
                      {detail.survey_rate.toFixed(1)}%
                    </span>
                  </div>
                  <div
                    className="h-[8px] rounded-[4px]"
                    style={{ background: "rgba(32,80,160,0.2)" }}
                  >
                    <div
                      className="h-full rounded-[4px] transition-all duration-500"
                      style={{
                        width: `${detail.survey_rate}%`,
                        background: "var(--gradient-green)",
                      }}
                    />
                  </div>
                </div>

                <div className="mb-[12px]">
                  <div className="flex justify-between mb-[4px]">
                    <span className="text-[12px]" style={{ color: "var(--text-secondary)" }}>
                      审核进度
                    </span>
                    <span className="text-[12px] font-bold" style={{ color: "var(--accent-purple)" }}>
                      {detail.audit_rate.toFixed(1)}%
                    </span>
                  </div>
                  <div
                    className="h-[8px] rounded-[4px]"
                    style={{ background: "rgba(32,80,160,0.2)" }}
                  >
                    <div
                      className="h-full rounded-[4px] transition-all duration-500"
                      style={{
                        width: `${detail.audit_rate}%`,
                        background: "var(--gradient-purple)",
                      }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-[4px]">
                    <span className="text-[12px]" style={{ color: "var(--text-secondary)" }}>
                      完成进度
                    </span>
                    <span className="text-[12px] font-bold" style={{ color: "var(--accent-red)" }}>
                      {detail.complete_rate.toFixed(1)}%
                    </span>
                  </div>
                  <div
                    className="h-[8px] rounded-[4px]"
                    style={{ background: "rgba(32,80,160,0.2)" }}
                  >
                    <div
                      className="h-full rounded-[4px] transition-all duration-500"
                      style={{
                        width: `${detail.complete_rate}%`,
                        background: "var(--gradient-red)",
                      }}
                    />
                  </div>
                </div>
              </div>

              {/* 地块用途分布饼图 + 家庭成员统计 */}
              <div className="grid grid-cols-2 gap-[16px]">
                {/* 饼图 */}
                <div>
                  <h3
                    className="text-[13px] font-semibold mb-[10px]"
                    style={{ color: "var(--accent-cyan)" }}
                  >
                    地块用途分布
                  </h3>
                  <div ref={pieChartRef} className="h-[180px]" />
                </div>

                {/* 家庭成员统计 */}
                <div>
                  <h3
                    className="text-[13px] font-semibold mb-[10px]"
                    style={{ color: "var(--accent-cyan)" }}
                  >
                    家庭成员统计
                  </h3>
                  <div className="flex flex-col gap-[10px]">
                    <div
                      className="flex items-center justify-between p-[12px] rounded-[6px]"
                      style={{
                        background: "rgba(10,20,50,0.5)",
                        border: "1px solid rgba(32,80,160,0.2)",
                      }}
                    >
                      <span className="text-[12px]" style={{ color: "var(--text-secondary)" }}>
                        总成员数
                      </span>
                      <span className="text-[18px] font-bold" style={{ color: "#fff" }}>
                        {detail.family_members.total}
                      </span>
                    </div>
                    <div
                      className="flex items-center justify-between p-[12px] rounded-[6px]"
                      style={{
                        background: "rgba(10,20,50,0.5)",
                        border: "1px solid rgba(32,80,160,0.2)",
                      }}
                    >
                      <span className="text-[12px]" style={{ color: "var(--text-secondary)" }}>
                        男性成员
                      </span>
                      <span className="text-[18px] font-bold" style={{ color: "var(--accent-cyan)" }}>
                        {detail.family_members.male}
                      </span>
                    </div>
                    <div
                      className="flex items-center justify-between p-[12px] rounded-[6px]"
                      style={{
                        background: "rgba(10,20,50,0.5)",
                        border: "1px solid rgba(32,80,160,0.2)",
                      }}
                    >
                      <span className="text-[12px]" style={{ color: "var(--text-secondary)" }}>
                        女性成员
                      </span>
                      <span className="text-[18px] font-bold" style={{ color: "var(--accent-gold)" }}>
                        {detail.family_members.female}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}