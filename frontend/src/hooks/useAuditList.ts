"use client";

import useSWR from 'swr';
import { fetchApi, api } from '@/lib/api';
import { useFilter } from './useFilter';

interface AuditItem {
  id: string;
 承包方名称: string;
  村组: string;
  上报类型: string;
  当前状态: '待公示' | '村干部审核' | '未调查' | '待审核';
}

interface AuditListResponse {
  items: AuditItem[];
  total: number;
  page: number;
  size: number;
  totalPages: number;
}

export function useAuditList(page: number, size: number = 10) {
  const { villageCode } = useFilter();
  
  const { data, error, isLoading, mutate } = useSWR<AuditListResponse>(
    api.auditList(page, size, villageCode || undefined),
    fetchApi,
    {
      refreshInterval: 30000,
      revalidateOnFocus: false,
    }
  );

  return {
    data: data || { items: [], total: 0, page: 1, size: 10, totalPages: 0 },
    isLoading,
    error,
    mutate,
  };
}