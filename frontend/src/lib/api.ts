const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

// API endpoints
export const api = {
  // 指标概览
  indicatorsOverview: (villageCode?: string) => 
    `/api/indicators/overview${villageCode ? `?village_code=${villageCode}` : ''}`,
  
  // 村组坐标列表
  villages: (villageCode?: string) => 
    `/api/indicators/villages${villageCode ? `?village_code=${villageCode}` : ''}`,
  
  // 饼图分类数据
  surveyCategories: (villageCode?: string) => 
    `/api/indicators/survey-categories${villageCode ? `?village_code=${villageCode}` : ''}`,
  
  // 审核列表
  auditList: (page: number, size: number, villageCode?: string) => 
    `/api/audit/list?page=${page}&size=${size}${villageCode ? `&village_code=${villageCode}` : ''}`,
  
  // 行政区划树
  adminDivisionsTree: () => '/api/admin-divisions/tree',
  
  // 地块用途统计
  landUsage: (villageCode?: string) => 
    `/api/indicators/land-usage${villageCode ? `?village_code=${villageCode}` : ''}`,
  
  // 摸底填报统计
  surveyStats: (villageCode?: string) => 
    `/api/indicators/survey-stats${villageCode ? `?village_code=${villageCode}` : ''}`,
  
  // 导入相关接口
  importUpload: () => '/api/import/upload',
  importTasks: (page: number = 1, pageSize: number = 10) => 
    `/api/import/tasks?page=${page}&page_size=${pageSize}`,
  importTaskStatus: (taskId: number) => `/api/import/tasks/${taskId}`,
  importTaskErrors: (taskId: number, page: number = 1, pageSize: number = 20) => 
    `/api/import/tasks/${taskId}/errors?page=${page}&page_size=${pageSize}`,
  
  // 认证相关接口
  authLogin: () => '/api/auth/login',
  authLogout: () => '/api/auth/logout',
  authVerify: () => '/api/auth/verify',
  
  // P1 增强功能接口
  // 村组详情
  villageDetail: (villageCode: string) => `/api/indicators/village-detail/${villageCode}`,
  
  // 发证进度
  certProgress: (villageCode?: string) => 
    `/api/cert/progress${villageCode ? `?village_code=${villageCode}` : ''}`,
  
  // 趋势数据
  trendData: (period: 'day' | 'week' = 'day', metricType?: string) => 
    `/api/snapshot/trend?period=${period}${metricType ? `&metric_type=${metricType}` : ''}`,
  
  // 快照列表
  snapshots: () => '/api/snapshot/list',
  
  // 快照对比
  snapshotCompare: (baseId: number, compareId: number) => 
    `/api/snapshot/compare?base_id=${baseId}&compare_id=${compareId}`,
  
  // 数据质量检测
  qualityCheck: () => '/api/quality/check',
  qualityErrors: (errorType?: string, page: number = 1, size: number = 20) => 
    `/api/quality/errors?page=${page}&size=${size}${errorType ? `&error_type=${errorType}` : ''}`,
};