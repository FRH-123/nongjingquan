"use client";

import { useEffect, useState } from "react";
import { fetchApi, api } from "@/lib/api";
import Header from "@/components/dashboard/Header";
import Panel from "@/components/dashboard/Panel";

interface SnapshotListItem {
  id: number;
  snapshot_date: string;
  level: string;
  code: string;
  created_at: string;
}

interface SnapshotListResponse {
  items: SnapshotListItem[];
  total_count: number;
}

interface ComparisonItem {
  metric_name: string;
  base_value: number;
  compare_value: number;
  change: number;
  change_percent: number;
}

interface ComparisonResponse {
  base_snapshot_id: number;
  base_date: string;
  compare_snapshot_id: number;
  compare_date: string;
  items: ComparisonItem[];
}

export default function TrendPage() {
  const [snapshots, setSnapshots] = useState<SnapshotListResponse | null>(null);
  const [baseId, setBaseId] = useState<number | null>(null);
  const [compareId, setCompareId] = useState<number | null>(null);
  const [comparison, setComparison] = useState<ComparisonResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // 获取快照列表
  useEffect(() => {
    fetchApi<SnapshotListResponse>(api.snapshots())
      .then((response) => {
        setSnapshots(response);
      })
      .catch(() => {
        // 使用模拟数据
        setSnapshots({
          items: [
            { id: 1, snapshot_date: "2025-07-01", level: "global", code: "", created_at: "2025-07-01T10:00:00" },
            { id: 2, snapshot_date: "2025-07-05", level: "global", code: "", created_at: "2025-07-05T10:00:00" },
            { id: 3, snapshot_date: "2025-07-10", level: "global", code: "", created_at: "2025-07-10T10:00:00" },
          ],
          total_count: 3,
        });
      });
  }, []);

  // 获取对比结果
  useEffect(() => {
    if (!baseId || !compareId || baseId === compareId) {
      return;
    }
    
    let active = true;
    
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const response = await fetchApi<ComparisonResponse>(api.snapshotCompare(baseId, compareId));
        if (active) {
          setComparison(response);
          setIsLoading(false);
        }
      } catch {
        // 使用模拟数据
        if (active) {
          setComparison({
            base_snapshot_id: baseId,
            base_date: "2025-07-01",
            compare_snapshot_id: compareId,
            compare_date: "2025-07-10",
            items: [
              { metric_name: "发包方总数", base_value: 21, compare_value: 21, change: 0, change_percent: 0 },
              { metric_name: "承包方总数", base_value: 600, compare_value: 657, change: 57, change_percent: 9.5 },
              { metric_name: "已摸底户数", base_value: 480, compare_value: 538, change: 58, change_percent: 12.08 },
              { metric_name: "已审核户数", base_value: 280, compare_value: 331, change: 51, change_percent: 18.21 },
              { metric_name: "已完成户数", base_value: 15, compare_value: 26, change: 11, change_percent: 73.33 },
            ],
          });
          setIsLoading(false);
        }
      }
    };
    
    fetchData();
    
    return () => {
      active = false;
    };
  }, [baseId, compareId]);

  // 变化量颜色
  const getChangeColor = (change: number) => {
    if (change > 0) return "var(--accent-green)";
    if (change < 0) return "var(--accent-red)";
    return "var(--text-muted)";
  };

  return (
    <div className="min-h-screen flex flex-col p-[12px_16px] gap-[10px]">
      {/* 顶部标题栏 */}
      <Header />

      {/* 快照选择 */}
      <Panel title="选择对比快照">
        <div className="flex items-center gap-[20px]">
          {/* 基准快照 */}
          <div className="flex items-center gap-[8px]">
            <span className="text-[12px]" style={{ color: "var(--text-secondary)" }}>
              基准快照:
            </span>
            <select
              value={baseId || ""}
              onChange={(e) => setBaseId(Number(e.target.value))}
              className="px-[12px] py-[8px] rounded-[6px] text-[13px] min-w-[200px]"
              style={{
                background: "rgba(10,20,50,0.7)",
                border: "1px solid var(--border-card)",
                color: "var(--text-primary)",
              }}
            >
              <option value="">请选择</option>
              {snapshots?.items.map((snapshot) => (
                <option key={snapshot.id} value={snapshot.id}>
                  {snapshot.snapshot_date} (ID: {snapshot.id})
                </option>
              ))}
            </select>
          </div>

          {/* 对比快照 */}
          <div className="flex items-center gap-[8px]">
            <span className="text-[12px]" style={{ color: "var(--text-secondary)" }}>
              对比快照:
            </span>
            <select
              value={compareId || ""}
              onChange={(e) => setCompareId(Number(e.target.value))}
              className="px-[12px] py-[8px] rounded-[6px] text-[13px] min-w-[200px]"
              style={{
                background: "rgba(10,20,50,0.7)",
                border: "1px solid var(--border-card)",
                color: "var(--text-primary)",
              }}
            >
              <option value="">请选择</option>
              {snapshots?.items.map((snapshot) => (
                <option key={snapshot.id} value={snapshot.id} disabled={snapshot.id === baseId}>
                  {snapshot.snapshot_date} (ID: {snapshot.id})
                </option>
              ))}
            </select>
          </div>

          {/* 提示 */}
          {baseId && compareId && baseId === compareId && (
            <span className="text-[12px]" style={{ color: "var(--accent-red)" }}>
              请选择不同的快照进行对比
            </span>
          )}
        </div>
      </Panel>

      {/* 对比结果 */}
      {comparison && (
        <Panel title="对比结果" className="flex-1">
          {/* 快照信息 */}
          <div className="flex items-center gap-[20px] mb-[16px]">
            <div
              className="px-[12px] py-[8px] rounded-[6px]"
              style={{
                background: "rgba(0,212,255,0.1)",
                border: "1px solid rgba(0,212,255,0.3)",
              }}
            >
              <span className="text-[12px]" style={{ color: "var(--accent-cyan)" }}>
                基准: {comparison.base_date}
              </span>
            </div>
            <div
              className="px-[12px] py-[8px] rounded-[6px]"
              style={{
                background: "rgba(255,184,48,0.1)",
                border: "1px solid rgba(255,184,48,0.3)",
              }}
            >
              <span className="text-[12px]" style={{ color: "var(--accent-gold)" }}>
                对比: {comparison.compare_date}
              </span>
            </div>
          </div>

          {/* 对比表格 */}
          {isLoading ? (
            <div className="flex items-center justify-center h-[200px]">
              <span style={{ color: "var(--text-muted)" }}>加载中...</span>
            </div>
          ) : (
            <div className="overflow-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--border-divider-strong)" }}>
                    <th
                      className="text-[11px] font-semibold px-[6px] py-[8px] text-left"
                      style={{ color: "var(--text-secondary)" }}
                    >
                      指标
                    </th>
                    <th
                      className="text-[11px] font-semibold px-[6px] py-[8px] text-right"
                      style={{ color: "var(--text-secondary)" }}
                    >
                      基准值
                    </th>
                    <th
                      className="text-[11px] font-semibold px-[6px] py-[8px] text-right"
                      style={{ color: "var(--text-secondary)" }}
                    >
                      对比值
                    </th>
                    <th
                      className="text-[11px] font-semibold px-[6px] py-[8px] text-right"
                      style={{ color: "var(--text-secondary)" }}
                    >
                      变化量
                    </th>
                    <th
                      className="text-[11px] font-semibold px-[6px] py-[8px] text-right"
                      style={{ color: "var(--text-secondary)" }}
                    >
                      变化百分比
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {comparison.items.map((item, index) => (
                    <tr
                      key={index}
                      style={{ borderBottom: "1px solid var(--border-divider-light)" }}
                    >
                      <td className="text-[12px] px-[6px] py-[9px]" style={{ color: "var(--text-primary)" }}>
                        {item.metric_name}
                      </td>
                      <td className="text-[12px] px-[6px] py-[9px] text-right" style={{ color: "var(--accent-cyan)" }}>
                        {item.base_value}
                      </td>
                      <td className="text-[12px] px-[6px] py-[9px] text-right" style={{ color: "var(--accent-gold)" }}>
                        {item.compare_value}
                      </td>
                      <td className="text-[12px] px-[6px] py-[9px] text-right" style={{ color: getChangeColor(item.change) }}>
                        {item.change > 0 ? `+${item.change}` : item.change}
                      </td>
                      <td className="text-[12px] px-[6px] py-[9px] text-right" style={{ color: getChangeColor(item.change) }}>
                        {item.change_percent > 0 ? `+${item.change_percent.toFixed(2)}%` : `${item.change_percent.toFixed(2)}%`}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Panel>
      )}

      {/* 无选择时的提示 */}
      {!baseId && !compareId && (
        <Panel title="对比结果" className="flex-1">
          <div className="flex items-center justify-center h-[200px]">
            <span style={{ color: "var(--text-muted)" }}>请选择两个快照进行对比</span>
          </div>
        </Panel>
      )}
    </div>
  );
}