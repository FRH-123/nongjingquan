"use client";

import useSWR from 'swr';
import { fetchApi, api } from '@/lib/api';
import { useFilter } from './useFilter';

interface SurveyCategory {
  name: string;
  value: number;
  color: string;
}

interface SurveyCategoriesResponse {
  total: number;
  categories: SurveyCategory[];
}

export function useSurveyCategories() {
  const { villageCode } = useFilter();
  
  const { data, error, isLoading } = useSWR<SurveyCategoriesResponse>(
    api.surveyCategories(villageCode || undefined),
    fetchApi,
    {
      refreshInterval: 30000,
      revalidateOnFocus: false,
    }
  );

  return {
    data: data || { total: 0, categories: [] },
    isLoading,
    error,
  };
}