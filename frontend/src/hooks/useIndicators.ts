"use client";

import useSWR from 'swr';
import { fetchApi, api } from '@/lib/api';
import { useFilter } from './useFilter';

// 核心指标概览响应类型
export interface OverviewIndicator {
  issuer_count: number;
  contractor_count: number;
  surveyed_count: number;
  audited_count: number;
  completed_count: number;
  code?: string;
  name?: string;
}

// 地块用途统计项
export interface LandUsageItem {
  category: string;
  code: string;
  count: number;
  area?: number;
}

// 地块用途统计响应
export interface LandUsageResponse {
  items: LandUsageItem[];
  total_count: number;
  total_area?: number;
}

// 摸底填报统计项
export interface SurveyStatsItem {
  village_code: string;
  village_name: string;
  reported_count: number;
  audited_count: number;
}

// 摸底填报统计响应
export interface SurveyStatsResponse {
  items: SurveyStatsItem[];
  total_reported: number;
  total_audited: number;
}

// 行政区划树节点
export interface AdminDivisionNode {
  code: string;
  name: string;
  level: number;
  parent_code?: string;
  children: AdminDivisionNode[];
}

// 行政区划树响应
export interface AdminDivisionTreeResponse {
  nodes: AdminDivisionNode[];
  total_count: number;
}

// 获取核心指标概览
export function useOverview() {
  const { villageCode, groupCode } = useFilter();
  // 如果选择了组，使用组编码；否则使用村编码
  const filterCode = groupCode || villageCode;
  
  const { data, error, isLoading } = useSWR<OverviewIndicator>(
    api.indicatorsOverview(filterCode || undefined),
    fetchApi,
    {
      refreshInterval: 30000,
      revalidateOnFocus: false,
    }
  );

  return {
    data: data || {
      issuer_count: 0,
      contractor_count: 0,
      surveyed_count: 0,
      audited_count: 0,
      completed_count: 0,
    },
    isLoading,
    error,
  };
}

// 获取地块用途统计
export function useLandUsage() {
  const { villageCode, groupCode } = useFilter();
  const filterCode = groupCode || villageCode;
  
  const { data, error, isLoading } = useSWR<LandUsageResponse>(
    api.landUsage(filterCode || undefined),
    fetchApi,
    {
      refreshInterval: 30000,
      revalidateOnFocus: false,
    }
  );

  return {
    data: data || { items: [], total_count: 0 },
    isLoading,
    error,
  };
}

// 获取摸底填报统计
export function useSurveyStats() {
  const { villageCode, groupCode } = useFilter();
  const filterCode = groupCode || villageCode;
  
  const { data, error, isLoading } = useSWR<SurveyStatsResponse>(
    api.surveyStats(filterCode || undefined),
    fetchApi,
    {
      refreshInterval: 30000,
      revalidateOnFocus: false,
    }
  );

  return {
    data: data || { items: [], total_reported: 0, total_audited: 0 },
    isLoading,
    error,
  };
}

// 获取行政区划树
export function useAdminDivisionsTree() {
  const { data, error, isLoading } = useSWR<AdminDivisionTreeResponse>(
    api.adminDivisionsTree(),
    fetchApi,
    {
      refreshInterval: 60000,
      revalidateOnFocus: false,
    }
  );

  return {
    data: data || { nodes: [], total_count: 0 },
    isLoading,
    error,
  };
}