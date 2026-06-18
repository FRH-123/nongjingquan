"use client";

import { useEffect, useState } from "react";
import { fetchApi, api } from "@/lib/api";
import Header from "@/components/dashboard/Header";
import Panel from "@/components/dashboard/Panel";

interface QualityStatsResponse {
  overlap_count: number;
  area_zero_count: number;
  area_exceed_count: number;
  code_invalid_count: number;
  total_errors: number;
  critical_count: number;
  warning_count: number;
}

interface QualityErrorItem {
  id: number;
  error_type: string;
  severity: string;
  table_name: string;
  record_code: string;
  error_message: string;
  created_at: string;
}

interface QualityErrorListResponse {
  items: QualityErrorItem[];
  total_count: number;
  page: number;
  size: number;
}

export default function QualityPage() {
  const [stats, setStats] = useState<QualityStatsResponse | null>(null);
  const [errors, setErrors] = useState<QualityErrorListResponse | null>(null);
  const [errorType, setErrorType] = useState<string>("");
  const [page, setPage] = useState(1);

  // 获取质量统计
  useEffect(() => {
    fetchApi<QualityStatsResponse>(api.qualityCheck())
      .then((response) => {
        setStats(response);
      })
      .catch(() => {
        // 使用模拟数据
        setStats({
          overlap_count: 0,
          area_zero_count: 5,
          area_exceed_count: 3,
          code_invalid_count: 12,
          total_errors: 20,
          critical_count: 15,
          warning_count: 5,
        });
      });
  }, []);

  // 获取错误列表
  useEffect(() => {
    let active = true;
    
    const fetchData = async () => {
      try {
        const response = await fetchApi<QualityErrorListResponse>(api.qualityErrors(errorType, page, 10));
        if (active) {
          setErrors(response);
        }
      } catch {
        // 使用模拟数据
        if (active) {
          setErrors({
            items: [
              {
                id: 1,
                error_type: "area_zero",
                severity: "critical",
                table_name: "cbdkxx",
                record_code: "370199001001001001",
                error_message: "地块面积为0或空值",
                created_at: "2025-07-11T10:00:00",
              },
              {
                id: 2,
                error_type: "code_invalid",
                severity: "critical",
                table_name: "cbf",
                record_code: "370199001001001",
                error_message: "承包方编码格式异常：应为18位",
                created_at: "2025-07-11T10:00:00",
              },
            ],
            total_count: 20,
            page: 1,
            size: 10,
          });
        }
      }
    };
    
    fetchData();
    
    return () => {
      active = false;
    };
  }, [errorType, page]);

  // 严重程度标签样式
  const getSeverityStyle = (severity: string) => {
    switch (severity) {
      case "critical":
        return {
          background: "rgba(255,71,87,0.12)",
          color: "#ff4757",
          border: "rgba(255,71,87,0.3)",
        };
      case "warning":
        return {
          background: "rgba(255,184,48,0.15)",
          color: "#ffb830",
          border: "rgba(255,184,48,0.3)",
        };
      default:
        return {
          background: "rgba(100,160,255,0.1)",
          color: "var(--text-secondary)",
          border: "rgba(100,160,255,0.2)",
        };
    }
  };

  // 错误类型名称映射
  const errorTypeNames: Record<string, string> = {
    area_zero: "面积为0",
    area_exceed: "面积超阈值",
    code_invalid: "编码异常",
    overlap: "空间重叠",
    import: "导入错误",
  };

  return (
    <div className="min-h-screen flex flex-col p-[12px_16px] gap-[10px]">
      {/* 顶部标题栏 */}
      <Header />

      {/* 统计卡片 */}
      <div className="grid grid-cols-4 gap-[12px]">
        <Panel title="空间重叠异常">
          <div className="flex flex-col items-center py-[10px]">
            <span className="text-[26px] font-bold" style={{ color: "var(--accent-red)" }}>
              {stats?.overlap_count || 0}
            </span>
            <span className="text-[11px]" style={{ color: "var(--text-muted)" }}>
              地块数
            </span>
          </div>
        </Panel>

        <Panel title="面积为0异常">
          <div className="flex flex-col items-center py-[10px]">
            <span className="text-[26px] font-bold" style={{ color: "var(--accent-red)" }}>
              {stats?.area_zero_count || 0}
            </span>
            <span className="text-[11px]" style={{ color: "var(--text-muted)" }}>
              地块数
            </span>
          </div>
        </Panel>

        <Panel title="面积超阈值">
          <div className="flex flex-col items-center py-[10px]">
            <span className="text-[26px] font-bold" style={{ color: "var(--accent-gold)" }}>
              {stats?.area_exceed_count || 0}
            </span>
            <span className="text-[11px]" style={{ color: "var(--text-muted)" }}>
              地块数
            </span>
          </div>
        </Panel>

        <Panel title="编码格式异常">
          <div className="flex flex-col items-center py-[10px]">
            <span className="text-[26px] font-bold" style={{ color: "var(--accent-purple)" }}>
              {stats?.code_invalid_count || 0}
            </span>
            <span className="text-[11px]" style={{ color: "var(--text-muted)" }}>
              记录数
            </span>
          </div>
        </Panel>
      </div>

      {/* 错误明细表格 */}
      <Panel title="异常明细" className="flex-1">
        {/* 筛选器 */}
        <div className="flex items-center gap-[12px] mb-[12px]">
          <span className="text-[12px]" style={{ color: "var(--text-secondary)" }}>
            错误类型:
          </span>
          <select
            value={errorType}
            onChange={(e) => setErrorType(e.target.value)}
            className="px-[8px] py-[4px] rounded-[4px] text-[12px]"
            style={{
              background: "rgba(10,20,50,0.7)",
              border: "1px solid var(--border-card)",
              color: "var(--text-primary)",
            }}
          >
            <option value="">全部</option>
            <option value="area_zero">面积为0</option>
            <option value="area_exceed">面积超阈值</option>
            <option value="code_invalid">编码异常</option>
          </select>

          <span className="text-[12px] ml-[20px]" style={{ color: "var(--text-muted)" }}>
            共 {errors?.total_count || 0} 条异常记录
          </span>
        </div>

        {/* 表格 */}
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
                    错误类型
                  </th>
                  <th
                    className="text-[11px] font-semibold px-[6px] py-[8px] text-left"
                    style={{ color: "var(--text-secondary)" }}
                  >
                    严重程度
                  </th>
                  <th
                    className="text-[11px] font-semibold px-[6px] py-[8px] text-left"
                    style={{ color: "var(--text-secondary)" }}
                  >
                    表名
                  </th>
                  <th
                    className="text-[11px] font-semibold px-[6px] py-[8px] text-left"
                    style={{ color: "var(--text-secondary)" }}
                  >
                    记录编码
                  </th>
                  <th
                    className="text-[11px] font-semibold px-[6px] py-[8px] text-left"
                    style={{ color: "var(--text-secondary)" }}
                  >
                    错误信息
                  </th>
                </tr>
              </thead>
              <tbody>
                {errors?.items.map((error) => (
                  <tr
                    key={error.id}
                    style={{ borderBottom: "1px solid var(--border-divider-light)" }}
                  >
                    <td className="text-[12px] px-[6px] py-[9px]" style={{ color: "var(--text-primary)" }}>
                      {errorTypeNames[error.error_type] || error.error_type}
                    </td>
                    <td className="text-[12px] px-[6px] py-[9px]">
                      <span
                        className="inline-block px-[8px] py-[2px] rounded-[3px] text-[11px] font-medium"
                        style={getSeverityStyle(error.severity)}
                      >
                        {error.severity === "critical" ? "严重" : error.severity === "warning" ? "警告" : "信息"}
                      </span>
                    </td>
                    <td className="text-[12px] px-[6px] py-[9px]" style={{ color: "var(--text-primary)" }}>
                      {error.table_name}
                    </td>
                    <td className="text-[12px] px-[6px] py-[9px]" style={{ color: "var(--text-primary)" }}>
                      {error.record_code}
                    </td>
                    <td className="text-[12px] px-[6px] py-[9px]" style={{ color: "var(--text-primary)" }}>
                      {error.error_message}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* 分页 */}
        <div className="flex items-center justify-center gap-[8px] mt-[12px]">
          <button
            onClick={() => setPage(page - 1)}
            disabled={page <= 1}
            className="w-[26px] h-[26px] flex items-center justify-center rounded-[4px]"
            style={{
              background: "rgba(10,20,50,0.5)",
              border: "1px solid var(--border-card)",
              color: page <= 1 ? "var(--text-muted)" : "var(--text-secondary)",
              opacity: page <= 1 ? 0.5 : 1,
            }}
          >
            ◄
          </button>
          <span className="text-[12px]" style={{ color: "var(--text-secondary)" }}>
            {page} / {Math.ceil((errors?.total_count || 0) / 10)}
          </span>
          <button
            onClick={() => setPage(page + 1)}
            disabled={page >= Math.ceil((errors?.total_count || 0) / 10)}
            className="w-[26px] h-[26px] flex items-center justify-center rounded-[4px]"
            style={{
              background: "rgba(10,20,50,0.5)",
              border: "1px solid var(--border-card)",
              color: page >= Math.ceil((errors?.total_count || 0) / 10) ? "var(--text-muted)" : "var(--text-secondary)",
              opacity: page >= Math.ceil((errors?.total_count || 0) / 10) ? 0.5 : 1,
            }}
          >
            ►
          </button>
        </div>
      </Panel>
    </div>
  );
}