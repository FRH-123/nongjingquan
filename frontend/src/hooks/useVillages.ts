"use client";

import useSWR from 'swr';
import { fetchApi, api } from '@/lib/api';
import { useFilter } from './useFilter';

interface Village {
  code: string;
  name: string;
  lat: number;
  lng: number;
}

export function useVillages() {
  const { villageCode } = useFilter();
  
  const { data, error, isLoading } = useSWR<Village[]>(
    api.villages(villageCode || undefined),
    fetchApi,
    {
      refreshInterval: 30000,
      revalidateOnFocus: false,
    }
  );

  return {
    villages: data || [],
    isLoading,
    error,
  };
}