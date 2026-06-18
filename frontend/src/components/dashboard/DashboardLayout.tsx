"use client";

import { useState } from "react";
import Header from "./Header";
import MetricCard from "./MetricCard";
import Panel from "./Panel";
import FilterPanel from "./FilterPanel";
import MapPanel from "./MapPanel";
import SurveyPieChart from "./SurveyPieChart";
import AuditTable from "./AuditTable";
import SurveyBarChart from "./SurveyBarChart";
import CertProgressCards from "./CertProgressCards";
import TrendChart from "./TrendChart";
import VillageDetailModal from "./VillageDetailModal";
import { FilterProvider } from "@/hooks/useFilter";
import { useOverview, useLandUsage } from "@/hooks/useIndicators";

// 大屏主布局组件
function DashboardContent() {
  const { data: overview } = useOverview();
  const { data: landUsage } = useLandUsage();
  const [selectedVillage, setSelectedVillage] = useState<{
    code: string;
    name: string;
  } | null>(null);
  const [showModal, setShowModal] = useState(false);

  // 处理村组点击
  const handleVillageClick = (code: string, name: string) => {
    setSelectedVillage({ code, name });
    setShowModal(true);
  };

  return (
    <div className="min-h-screen flex flex-col p-[12px_16px] gap-[10px]">
      {/* 顶部标题栏 */}
      <Header />

      {/* 指标卡行 */}
      <div className="grid grid-cols-5 gap-[12px]">
        <MetricCard
          label="发包方总数"
          value={overview.issuer_count}
          iconVariant="cyan"
        />
        <MetricCard
          label="承包方总数"
          value={overview.contractor_count}
          iconVariant="gold"
        />
        <MetricCard
          label="已摸底户数"
          value={overview.surveyed_count}
          iconVariant="green"
        />
        <MetricCard
          label="已内业审核数"
          value={overview.audited_count}
          iconVariant="purple"
        />
        <MetricCard
          label="已完成户数"
          value={overview.completed_count}
          iconVariant="red"
        />
      </div>

      {/* 发证进度指标卡 */}
      <CertProgressCards />

      {/* 三栏布局 */}
      <div className="flex-1 grid gap-[12px]" style={{ gridTemplateColumns: "280px 1fr 300px" }}>
        {/* 左侧栏 */}
        <div className="flex flex-col gap-[10px]">
          <Panel title="权属单位筛选">
            <FilterPanel />
          </Panel>
          <Panel title="承包地块用途统计">
            <div className="grid grid-cols-2 gap-[8px]">
              {landUsage.items.slice(0, 4).map((item) => (
                <div
                  key={item.code}
                  className="flex flex-col items-center p-[12px] rounded-[6px]"
                  style={{
                    background: "rgba(10,20,50,0.5)",
                    border: "1px solid rgba(32,80,160,0.2)",
                  }}
                >
                  <span className="text-[11px]" style={{ color: "var(--text-secondary)" }}>
                    {item.category}
                  </span>
                  <span className="text-[20px] font-bold" style={{ color: "var(--accent-cyan)" }}>
                    {item.count}
                  </span>
                </div>
              ))}
            </div>
          </Panel>
          <Panel title="摸底填报情况统计">
            <SurveyBarChart onVillageClick={handleVillageClick} />
          </Panel>
        </div>

        {/* 中央区域 - 天地图 */}
        <div className="flex flex-col gap-[10px]">
          <Panel title="天地图" className="flex-1">
            <MapPanel className="h-[280px]" onVillageClick={handleVillageClick} />
          </Panel>
          <Panel title="进度趋势">
            <TrendChart />
          </Panel>
        </div>

        {/* 右侧栏 */}
        <div className="flex flex-col gap-[10px]">
          <Panel title="摸底填报统计">
            <SurveyPieChart />
          </Panel>
          <Panel title="内业审核">
            <AuditTable />
          </Panel>
        </div>
      </div>

      {/* 村组详情弹窗 */}
      {selectedVillage && (
        <VillageDetailModal
          villageCode={selectedVillage.code}
          villageName={selectedVillage.name}
          isOpen={showModal}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
}

export default function DashboardLayout() {
  return (
    <FilterProvider>
      <DashboardContent />
    </FilterProvider>
  );
}