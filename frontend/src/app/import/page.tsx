"use client";

import { useState, useEffect, useRef } from 'react';
import useSWR from 'swr';
import Link from 'next/link';
import DropZone from '@/components/import/DropZone';
import ImportProgress from '@/components/import/ImportProgress';
import ImportHistory from '@/components/import/ImportHistory';
import ErrorDetail from '@/components/import/ErrorDetail';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ImportTask {
  id: number;
  filename: string;
  status: string;
  total_count: number;
  success_count: number;
  error_count: number;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

interface ImportError {
  id: number;
  task_id: number;
  table_name: string;
  code: string | null;
  row_number: number | null;
  error_message: string;
  created_at: string;
}

interface ImportStatusResponse {
  task_id: number;
  status: string;
  progress: number;
  message: string;
  total_count: number;
  success_count: number;
  error_count: number;
  errors: ImportError[];
}

interface ImportTasksResponse {
  tasks: ImportTask[];
  total: number;
  page: number;
  page_size: number;
}

// SWR fetcher
const fetcher = async (url: string) => {
  const response = await fetch(url);
  return response.json();
};

export default function ImportPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [currentTaskId, setCurrentTaskId] = useState<number | null>(null);
  const [importStatus, setImportStatus] = useState<ImportStatusResponse | null>(null);
  const [errorDetailOpen, setErrorDetailOpen] = useState(false);
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);
  const [selectedTaskErrors, setSelectedTaskErrors] = useState<ImportError[]>([]);
  const [isLoadingErrors, setIsLoadingErrors] = useState(false);
  
  // 使用 ref 来存储轮询 interval
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // 使用 SWR 获取任务列表
  const { data: tasksData, isLoading: isLoadingTasks, mutate: mutateTasks } = useSWR<ImportTasksResponse>(
    `${API_BASE_URL}/api/import/tasks?page=1&page_size=10`,
    fetcher,
    { refreshInterval: 0, revalidateOnFocus: false }
  );

  const tasks = tasksData?.tasks || [];

  // 获取任务状态 - 不使用 SWR，手动管理
  const fetchTaskStatus = async (taskId: number): Promise<ImportStatusResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/import/tasks/${taskId}`);
    return response.json();
  };

  // 获取任务错误详情
  const fetchTaskErrors = async (taskId: number) => {
    setIsLoadingErrors(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/import/tasks/${taskId}/errors?page=1&page_size=50`);
      const data = await response.json();
      setSelectedTaskErrors(data.errors || []);
    } catch (error) {
      console.error('获取错误详情失败:', error);
      setSelectedTaskErrors([]);
    } finally {
      setIsLoadingErrors(false);
    }
  };

  // 轮询任务状态
  useEffect(() => {
    if (currentTaskId) {
      // 定义轮询函数
      const poll = async () => {
        try {
          const data = await fetchTaskStatus(currentTaskId);
          setImportStatus(data);
          
          // 如果任务完成或失败，停止轮询并刷新任务列表
          if (data.status === 'completed' || data.status === 'failed') {
            setCurrentTaskId(null);
            if (pollingIntervalRef.current) {
              clearInterval(pollingIntervalRef.current);
              pollingIntervalRef.current = null;
            }
            // 刷新任务列表
            mutateTasks();
          }
        } catch (error) {
          console.error('获取任务状态失败:', error);
        }
      };

      // 立即获取一次
      poll();
      
      // 每2秒轮询
      pollingIntervalRef.current = setInterval(poll, 2000);
      
      return () => {
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
      };
    }
  }, [currentTaskId, mutateTasks]);

  // 处理文件选择
  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
  };

  // 开始导入
  const handleStartImport = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setImportStatus(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch(`${API_BASE_URL}/api/import/upload`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setCurrentTaskId(data.task_id);
        setSelectedFile(null);
      } else {
        alert(data.detail || '上传失败');
      }
    } catch (error) {
      console.error('上传失败:', error);
      alert('上传失败，请检查网络连接');
    } finally {
      setIsUploading(false);
    }
  };

  // 查看详情
  const handleViewDetails = (taskId: number) => {
    setSelectedTaskId(taskId);
    setErrorDetailOpen(true);
    fetchTaskErrors(taskId);
  };

  // 关闭详情弹窗
  const handleCloseErrorDetail = () => {
    setErrorDetailOpen(false);
    setSelectedTaskId(null);
    setSelectedTaskErrors([]);
  };

  return (
    <div className="min-h-screen relative">
      {/* 深色背景 */}
      <div 
        className="absolute inset-0"
        style={{ background: 'var(--bg-primary)' }}
      />

      {/* 氛围光效 */}
      <div 
        className="absolute inset-0 pointer-events-none"
        style={{
          background: `
            radial-gradient(ellipse 80% 50% at 50% 0%, rgba(0,80,180,0.12), transparent 60%),
            radial-gradient(ellipse 60% 40% at 80% 100%, rgba(0,160,255,0.06), transparent 50%),
            radial-gradient(ellipse 50% 30% at 10% 80%, rgba(100,0,200,0.05), transparent 50%)
          `,
        }}
      />

      {/* 内容区域 */}
      <div className="relative min-h-screen p-6">
        {/* 顶部导航 */}
        <div className="flex items-center justify-between mb-6">
          <Link 
            href="/dashboard"
            className="flex items-center gap-2 px-3 py-2 rounded-md transition-colors"
            style={{
              color: 'var(--accent-cyan)',
              background: 'rgba(0, 212, 255, 0.1)',
            }}
          >
            <svg 
              width="16" 
              height="16" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2"
            >
              <polyline points="15 18 9 12 15 6" />
            </svg>
            <span className="text-[13px]">返回大屏</span>
          </Link>
          <h1 
            className="text-[20px] font-bold tracking-[4px]"
            style={{ color: 'var(--text-primary)' }}
          >
            数据导入管理
          </h1>
          <div className="w-[100px]" />
        </div>

        {/* 主内容区 */}
        <div className="max-w-[900px] mx-auto">
          {/* 上传区域 */}
          <div 
            className="mb-6 p-5 rounded-lg"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-card)',
              boxShadow: 'var(--shadow-card)',
            }}
          >
            <div className="mb-4">
              <span 
                className="text-[13px] font-semibold tracking-[1px]"
                style={{ color: 'var(--accent-cyan)' }}
              >
                ▶ 文件上传
              </span>
            </div>
            
            <DropZone 
              onFileSelect={handleFileSelect} 
              disabled={isUploading || currentTaskId !== null}
            />

            {/* 开始导入按钮 */}
            {selectedFile && !currentTaskId && (
              <button
                onClick={handleStartImport}
                disabled={isUploading}
                className="mt-4 w-full py-3 rounded-md text-[14px] font-semibold tracking-[1px] transition-all duration-200"
                style={{
                  background: isUploading 
                    ? 'rgba(32, 80, 160, 0.35)' 
                    : 'var(--gradient-cyan)',
                  color: '#fff',
                  cursor: isUploading ? 'not-allowed' : 'pointer',
                  opacity: isUploading ? 0.7 : 1,
                }}
              >
                {isUploading ? '上传中...' : '开始导入'}
              </button>
            )}
          </div>

          {/* 导入进度 */}
          {importStatus && (
            <div 
              className="mb-6 p-5 rounded-lg"
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-card)',
                boxShadow: 'var(--shadow-card)',
              }}
            >
              <div className="mb-4">
                <span 
                  className="text-[13px] font-semibold tracking-[1px]"
                  style={{ color: 'var(--accent-cyan)' }}
                >
                  ▶ 导入进度
                </span>
              </div>
              <ImportProgress
                progress={importStatus.progress}
                status={importStatus.status}
                message={importStatus.message}
                successCount={importStatus.success_count}
                errorCount={importStatus.error_count}
                totalCount={importStatus.total_count}
              />
            </div>
          )}

          {/* 导入历史 */}
          <div 
            className="p-5 rounded-lg"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-card)',
              boxShadow: 'var(--shadow-card)',
            }}
          >
            <div className="mb-4">
              <span 
                className="text-[13px] font-semibold tracking-[1px]"
                style={{ color: 'var(--accent-cyan)' }}
              >
                ▶ 导入历史
              </span>
            </div>
            <ImportHistory
              tasks={tasks}
              onViewDetails={handleViewDetails}
              isLoading={isLoadingTasks}
            />
          </div>
        </div>
      </div>

      {/* 错误详情弹窗 */}
      <ErrorDetail
        isOpen={errorDetailOpen}
        onClose={handleCloseErrorDetail}
        errors={selectedTaskErrors}
        taskId={selectedTaskId || 0}
        isLoading={isLoadingErrors}
      />
    </div>
  );
}