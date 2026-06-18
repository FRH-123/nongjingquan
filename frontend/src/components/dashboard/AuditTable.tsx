"use client";

import { useState } from 'react';
import { useAuditList } from '@/hooks/useAuditList';
import StatusTag, { StatusType } from './StatusTag';
import TypeTag from './TypeTag';
import Pagination from './Pagination';

// 模拟数据（当API不可用时）
const mockAuditItems = [
  { id: '1', 承包方名称: '张三家庭农场', 村组: '张家庄村一组', 上报类型: '分户-保留户', 当前状态: '待公示' },
  { id: '2', 承包方名称: '李四农业合作社', 村组: '李家沟村二组', 上报类型: '分户-新增户', 当前状态: '村干部审核' },
  { id: '3', 承包方名称: '王五种植户', 村组: '王家屯村三组', 上报类型: '地块转', 当前状态: '未调查' },
  { id: '4', 承包方名称: '赵六家庭农场', 村组: '赵家湾村一组', 上报类型: '有变化', 当前状态: '待审核' },
  { id: '5', 承包方名称: '刘七农业合作社', 村组: '刘家坡村二组', 上报类型: '无变化', 当前状态: '待公示' },
  { id: '6', 承包方名称: '孙八种植户', 村组: '张家庄村二组', 上报类型: '分户-保留户', 当前状态: '村干部审核' },
  { id: '7', 承包方名称: '周九家庭农场', 村组: '李家沟村一组', 上报类型: '分户-新增户', 当前状态: '待审核' },
  { id: '8', 承包方名称: '吴十农业合作社', 村组: '王家屯村一组', 上报类型: '地块转', 当前状态: '待公示' },
  { id: '9', 承包方名称: '郑十一种植户', 村组: '赵家湾村二组', 上报类型: '有变化', 当前状态: '未调查' },
  { id: '10', 承包方名称: '钱十二家庭农场', 村组: '刘家坡村一组', 上报类型: '无变化', 当前状态: '村干部审核' },
];

interface AuditTableProps {
  className?: string;
}

export default function AuditTable({ className = '' }: AuditTableProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;
  
  const { data, isLoading, error } = useAuditList(currentPage, pageSize);
  
  // 使用模拟数据或真实数据
  const displayData = error || data.items.length === 0 
    ? { 
        items: mockAuditItems.slice((currentPage - 1) * pageSize, currentPage * pageSize), 
        total: mockAuditItems.length, 
        page: currentPage, 
        size: pageSize, 
        totalPages: Math.ceil(mockAuditItems.length / pageSize) 
      }
    : data;
  
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };
  
  return (
    <div className={`flex flex-col ${className}`}>
      {/* 表格区域 */}
      <div className="flex-1 overflow-auto">
        {isLoading ? (
          <div 
            className="flex items-center justify-center h-full"
            style={{ color: 'var(--text-muted)' }}
          >
            数据加载中...
          </div>
        ) : (
          <table className="w-full border-collapse">
            {/* 表头 */}
            <thead>
              <tr 
                style={{ 
                  borderBottom: '1px solid rgba(32,80,160,0.3)',
                }}
              >
                <th 
                  className="px-[6px] py-[8px] text-left text-[11px] font-semibold whitespace-nowrap"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  承包方名称
                </th>
                <th 
                  className="px-[6px] py-[8px] text-left text-[11px] font-semibold whitespace-nowrap"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  村组
                </th>
                <th 
                  className="px-[6px] py-[8px] text-left text-[11px] font-semibold whitespace-nowrap"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  上报类型
                </th>
                <th 
                  className="px-[6px] py-[8px] text-left text-[11px] font-semibold whitespace-nowrap"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  当前状态
                </th>
              </tr>
            </thead>
            {/* 表体 */}
            <tbody>
              {displayData.items.map((item, index) => (
                <tr 
                  key={item.id || index}
                  className="transition-colors"
                  style={{ 
                    borderBottom: '1px solid rgba(32,80,160,0.1)',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'rgba(0,100,200,0.08)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'transparent';
                  }}
                >
                  <td 
                    className="px-[6px] py-[9px] text-[12px] whitespace-nowrap"
                    style={{ color: 'var(--text-primary)' }}
                  >
                    {item.承包方名称}
                  </td>
                  <td 
                    className="px-[6px] py-[9px] text-[12px] whitespace-nowrap"
                    style={{ color: 'var(--text-primary)' }}
                  >
                    {item.村组}
                  </td>
                  <td className="px-[6px] py-[9px]">
                    <TypeTag type={item.上报类型} />
                  </td>
                  <td className="px-[6px] py-[9px]">
                    <StatusTag status={item.当前状态 as StatusType} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      
      {/* 分页控件 */}
      <Pagination 
        currentPage={displayData.page} 
        totalPages={displayData.totalPages} 
        onPageChange={handlePageChange} 
      />
    </div>
  );
}