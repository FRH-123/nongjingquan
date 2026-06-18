"use client";

import { useEffect, useState } from "react";
import { fetchApi, api } from "@/lib/api";
import { useFilter } from "@/hooks/useFilter";

interface CertProgressResponse {
  contract_rate: number;
  contract_signed: number;
  total_households: number;
  cert_rate: number;
  cert_issued: number;
  pickup_rate: number;
  cert_picked: number;
}

interface CertProgressCardsProps {
  className?: string;
}

export default function CertProgressCards({ className = "" }: CertProgressCardsProps) {
  const { villageCode } = useFilter();
  const [data, setData] = useState<CertProgressResponse | null>(null);

  // 获取发证进度数据
  useEffect(() => {
    let active = true;
    
    const fetchData = async () => {
      try {
        const response = await fetchApi<CertProgressResponse>(api.certProgress(villageCode || undefined));
        if (active) {
          setData(response);
        }
      } catch {
        // 使用模拟数据
        if (active) {
          setData({
            contract_rate: 50.4,
            contract_signed: 331,
            total_households: 657,
            cert_rate: 7.8,
            cert_issued: 26,
            pickup_rate: 80.0,
            cert_picked: 21,
          });
        }
      }
    };
    
    fetchData();
    
    return () => {
      active = false;
    };
  }, [villageCode]);

  if (!data) {
    return (
      <div className={`grid grid-cols-3 gap-[12px] ${className}`}>
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="p-[14px] rounded-[8px] animate-pulse"
            style={{
              background: "var(--bg-card)",
              border: "1px solid var(--border-card)",
            }}
          >
            <div className="h-[20px] mb-[8px]" style={{ background: "rgba(32,80,160,0.2)" }} />
            <div className="h-[26px]" style={{ background: "rgba(32,80,160,0.2)" }} />
          </div>
        ))}
      </div>
    );
  }

  const cards = [
    {
      label: "合同签订率",
      value: `${data.contract_rate}%`,
      subValue: `${data.contract_signed}/${data.total_households}户`,
      gradient: "var(--gradient-cyan)",
      shadowColor: "rgba(0,212,255,0.3)",
    },
    {
      label: "发证率",
      value: `${data.cert_rate}%`,
      subValue: `${data.cert_issued}户已发证`,
      gradient: "var(--gradient-gold)",
      shadowColor: "rgba(255,184,48,0.3)",
    },
    {
      label: "领证率",
      value: `${data.pickup_rate}%`,
      subValue: `${data.cert_picked}户已领取`,
      gradient: "var(--gradient-green)",
      shadowColor: "rgba(0,230,118,0.3)",
    },
  ];

  return (
    <div className={`grid grid-cols-3 gap-[12px] ${className}`}>
      {cards.map((card) => (
        <div
          key={card.label}
          className="p-[14px] rounded-[8px] flex items-center gap-[14px] transition-all duration-300"
          style={{
            background: "var(--bg-card)",
            border: "1px solid var(--border-card)",
            boxShadow: "var(--shadow-card)",
          }}
        >
          {/* 图标 */}
          <div
            className="w-[44px] h-[44px] rounded-[10px] flex items-center justify-center"
            style={{
              background: card.gradient,
              boxShadow: `0 4px 12px ${card.shadowColor}`,
            }}
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="white"
              strokeWidth="2"
            >
              <path d="M9 12l2 2 4-4" />
              <path d="M21 12c0 4.97-4.03 9-9 9s-9-4.03-9-9 4.03-9 9-9c2.12 0 4.07.74 5.61 1.97" />
            </svg>
          </div>

          {/* 文字 */}
          <div className="flex flex-col">
            <span
              className="text-[12px] tracking-[1px]"
              style={{ color: "var(--text-secondary)" }}
            >
              {card.label}
            </span>
            <span
              className="text-[26px] font-bold tracking-[1px]"
              style={{ color: "#fff" }}
            >
              {card.value}
            </span>
            <span
              className="text-[11px]"
              style={{ color: "var(--text-muted)" }}
            >
              {card.subValue}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}