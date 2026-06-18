"use client";

import { useState, useMemo } from 'react';
import useSWR from 'swr';
import { fetchApi, api } from '@/lib/api';
import { useFilter } from '@/hooks/useFilter';

interface AdminDivisionNode {
  code: string;
  name: string;
  level: number;
  children?: AdminDivisionNode[];
}

interface AdminDivisionTreeResponse {
  nodes: AdminDivisionNode[];
  total_count: number;
}

// 模拟行政区划数据
const mockAdminDivisions: AdminDivisionNode[] = [
  {
    code: '370199001',
    name: '张家庄村',
    level: 5,
    children: [
      { code: '370199001001', name: '一组', level: 6 },
      { code: '370199001002', name: '二组', level: 6 },
      { code: '370199001003', name: '三组', level: 6 },
    ],
  },
  {
    code: '370199002',
    name: '李家沟村',
    level: 5,
    children: [
      { code: '370199002001', name: '一组', level: 6 },
      { code: '370199002002', name: '二组', level: 6 },
    ],
  },
  {
    code: '370199003',
    name: '王家屯村',
    level: 5,
    children: [
      { code: '370199003001', name: '一组', level: 6 },
      { code: '370199003002', name: '二组', level: 6 },
      { code: '370199003003', name: '三组', level: 6 },
    ],
  },
  {
    code: '370199004',
    name: '赵家湾村',
    level: 5,
    children: [
      { code: '370199004001', name: '一组', level: 6 },
      { code: '370199004002', name: '二组', level: 6 },
    ],
  },
  {
    code: '370199005',
    name: '刘家坡村',
    level: 5,
    children: [
      { code: '370199005001', name: '一组', level: 6 },
      { code: '370199005002', name: '二组', level: 6 },
    ],
  },
];

// 从树中提取村级节点
function extractVillages(nodes: AdminDivisionNode[]): AdminDivisionNode[] {
  const villages: AdminDivisionNode[] = [];
  
  function traverse(nodeList: AdminDivisionNode[]) {
    for (const node of nodeList) {
      if (node.level === 5) {
        villages.push(node);
      }
      if (node.children) {
        traverse(node.children);
      }
    }
  }
  
  traverse(nodes);
  return villages;
}

export default function FilterPanel() {
  const { villageCode, setVillageCode, groupCode, setGroupCode } = useFilter();
  const [localVillage, setLocalVillage] = useState<string>(villageCode || '');
  const [localGroup, setLocalGroup] = useState<string>(groupCode || '');
  
  // 获取行政区划数据
  const { data, error } = useSWR<AdminDivisionTreeResponse>(
    api.adminDivisionsTree(),
    fetchApi,
    {
      refreshInterval: 60000,
      revalidateOnFocus: false,
    }
  );
  
  // 使用模拟数据或真实数据
  const adminDivisions = useMemo(() => {
    if (error || !data || !data.nodes) {
      return mockAdminDivisions;
    }
    return extractVillages(data.nodes);
  }, [data, error]);
  
  // 获取当前选中村的组列表
  const currentVillage = useMemo(() => {
    return adminDivisions.find(v => v.code === localVillage);
  }, [adminDivisions, localVillage]);
  
  const groupList = currentVillage?.children || [];
  
  // 处理村选择变化
  const handleVillageChange = (newVillage: string) => {
    setLocalVillage(newVillage);
    setLocalGroup('');
    setVillageCode(newVillage || null);
    setGroupCode(null);
  };
  
  // 处理组选择变化
  const handleGroupChange = (newGroup: string) => {
    setLocalGroup(newGroup);
    setGroupCode(newGroup || null);
  };
  
  return (
    <div className="flex flex-col gap-[10px]">
      {/* 村选择 */}
      <div className="flex flex-col gap-[4px]">
        <label 
          className="text-[11px] font-medium"
          style={{ color: 'var(--text-secondary)', letterSpacing: '1px' }}
        >
          村
        </label>
        <select
          value={localVillage}
          onChange={(e) => handleVillageChange(e.target.value)}
          className="w-full px-[12px] py-[8px] rounded-[6px] text-[13px] appearance-none cursor-pointer transition-colors focus:outline-none"
          style={{
            background: 'rgba(10,20,50,0.7)',
            border: '1px solid var(--border-card)',
            color: 'var(--text-primary)',
            backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2300d4ff' d='M3 4l3 4 3-4'/%3E%3C/svg%3E")`,
            backgroundRepeat: 'no-repeat',
            backgroundPosition: 'right 10px center',
          }}
        >
          <option value="">全部村</option>
          {adminDivisions.map((village) => (
            <option key={village.code} value={village.code}>
              {village.name}
            </option>
          ))}
        </select>
      </div>
      
      {/* 组选择 */}
      <div className="flex flex-col gap-[4px]">
        <label 
          className="text-[11px] font-medium"
          style={{ color: 'var(--text-secondary)', letterSpacing: '1px' }}
        >
          组
        </label>
        <select
          value={localGroup}
          onChange={(e) => handleGroupChange(e.target.value)}
          disabled={!localVillage}
          className="w-full px-[12px] py-[8px] rounded-[6px] text-[13px] appearance-none cursor-pointer transition-colors focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            background: 'rgba(10,20,50,0.7)',
            border: '1px solid var(--border-card)',
            color: 'var(--text-primary)',
            backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2300d4ff' d='M3 4l3 4 3-4'/%3E%3C/svg%3E")`,
            backgroundRepeat: 'no-repeat',
            backgroundPosition: 'right 10px center',
          }}
        >
          <option value="">全部组</option>
          {groupList.map((group) => (
            <option key={group.code} value={group.code}>
              {group.name}
            </option>
          ))}
        </select>
      </div>
      
      {/* 当前筛选状态提示 */}
      {(villageCode || groupCode) && (
        <div 
          className="text-[11px] px-[8px] py-[4px] rounded-[4px]"
          style={{
            background: 'rgba(0,212,255,0.1)',
            color: 'var(--accent-cyan)',
            border: '1px solid rgba(0,212,255,0.2)',
          }}
        >
          已筛选: {currentVillage?.name || '全部村'}
          {groupCode && ` / ${groupList.find(g => g.code === groupCode)?.name || ''}`}
        </div>
      )}
    </div>
  );
}