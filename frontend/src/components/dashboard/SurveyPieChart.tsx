"use client";

import { useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { useSurveyCategories } from '@/hooks/useSurveyCategories';

// 饼图分类色（符合 UI 规范）
const PIE_COLORS = {
  '分户-保留户': '#4fc3f7',
  '分户-新增户': '#ffd54f',
  '地块转': '#81c784',
  '有变化': '#ff8a65',
  '无变化': '#7986cb',
};

// 模拟数据组（当API不可用时）
const mockDataGroups = [
  {
    total: 657,
    categories: [
      { name: '分户-保留户', value: 320, color: '#4fc3f7' },
      { name: '分户-新增户', value: 85, color: '#ffd54f' },
      { name: '地块转', value: 42, color: '#81c784' },
      { name: '有变化', value: 120, color: '#ff8a65' },
      { name: '无变化', value: 90, color: '#7986cb' },
    ],
  },
  {
    total: 538,
    categories: [
      { name: '分户-保留户', value: 280, color: '#4fc3f7' },
      { name: '分户-新增户', value: 70, color: '#ffd54f' },
      { name: '地块转', value: 35, color: '#81c784' },
      { name: '有变化', value: 98, color: '#ff8a65' },
      { name: '无变化', value: 55, color: '#7986cb' },
    ],
  },
  {
    total: 331,
    categories: [
      { name: '分户-保留户', value: 180, color: '#4fc3f7' },
      { name: '分户-新增户', value: 45, color: '#ffd54f' },
      { name: '地块转', value: 28, color: '#81c784' },
      { name: '有变化', value: 65, color: '#ff8a65' },
      { name: '无变化', value: 13, color: '#7986cb' },
    ],
  },
];

interface SurveyPieChartProps {
  className?: string;
}

export default function SurveyPieChart({ className = '' }: SurveyPieChartProps) {
  const { data, isLoading, error } = useSurveyCategories();
  const [currentPage, setCurrentPage] = useState(0);
  
  // 使用模拟数据或真实数据
  const dataGroups = error || data.categories.length === 0 ? mockDataGroups : [data];
  const totalPages = dataGroups.length;
  const currentData = dataGroups[currentPage] || mockDataGroups[0];
  
  // ECharts 配置
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
      backgroundColor: 'rgba(13, 25, 65, 0.9)',
      borderColor: 'rgba(32, 80, 160, 0.35)',
      textStyle: {
        color: '#e8f0ff',
        fontSize: 12,
      },
    },
    legend: {
      orient: 'horizontal',
      bottom: '5%',
      itemWidth: 10,
      itemHeight: 10,
      itemGap: 16,
      textStyle: {
        color: 'rgba(180, 200, 240, 0.75)',
        fontSize: 11,
      },
      data: currentData.categories.map(c => c.name),
    },
    series: [
      {
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 3,
          borderColor: 'rgba(32, 80, 160, 0.2)',
          borderWidth: 1,
        },
        label: {
          show: false,
        },
        emphasis: {
          label: {
            show: false,
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 212, 255, 0.5)',
          },
        },
        data: currentData.categories.map(c => ({
          value: c.value,
          name: c.name,
          itemStyle: {
            color: PIE_COLORS[c.name as keyof typeof PIE_COLORS] || c.color,
          },
        })),
      },
    ],
    graphic: [
      {
        type: 'text',
        left: 'center',
        top: '38%',
        style: {
          text: currentData.total.toString(),
          textAlign: 'center',
          fill: '#ffffff',
          fontSize: 16,
          fontWeight: 700,
        },
      },
      {
        type: 'text',
        left: 'center',
        top: '46%',
        style: {
          text: '总户数',
          textAlign: 'center',
          fill: 'rgba(180, 200, 240, 0.75)',
          fontSize: 9,
        },
      },
    ],
  };
  
  // 分页指示器点击
  const handlePageClick = (index: number) => {
    setCurrentPage(index);
  };
  
  return (
    <div className={`flex flex-col ${className}`}>
      {/* 饼图区域 */}
      <div className="flex-1 min-h-[180px]">
        {isLoading ? (
          <div 
            className="flex items-center justify-center h-full"
            style={{ color: 'var(--text-muted)' }}
          >
            数据加载中...
          </div>
        ) : (
          <ReactECharts
            option={option}
            style={{ height: '100%', width: '100%' }}
            opts={{ renderer: 'canvas' }}
          />
        )}
      </div>
      
      {/* 分页指示器 */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-[6px] pb-[4px]">
          {Array.from({ length: totalPages }, (_, index) => (
            <button
              key={index}
              onClick={() => handlePageClick(index)}
              className="transition-all duration-200"
              style={{
                width: index === currentPage ? '16px' : '6px',
                height: '6px',
                borderRadius: index === currentPage ? '3px' : '50%',
                background: index === currentPage 
                  ? 'var(--accent-cyan)' 
                  : 'rgba(100,160,255,0.3)',
                cursor: 'pointer',
              }}
            />
          ))}
          <span 
            className="text-[11px] ml-[8px]"
            style={{ color: 'var(--text-secondary)' }}
          >
            {currentPage + 1}/{totalPages}
          </span>
        </div>
      )}
    </div>
  );
}