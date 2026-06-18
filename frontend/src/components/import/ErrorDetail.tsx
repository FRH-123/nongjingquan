"use client";

interface ImportError {
  id: number;
  task_id: number;
  table_name: string;
  code: string | null;
  row_number: number | null;
  error_message: string;
  created_at: string;
}

interface ErrorDetailProps {
  isOpen: boolean;
  onClose: () => void;
  errors: ImportError[];
  taskId: number;
  isLoading?: boolean;
}

export default function ErrorDetail({
  isOpen,
  onClose,
  errors,
  taskId,
  isLoading = false,
}: ErrorDetailProps) {
  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ background: 'rgba(0, 0, 0, 0.6)' }}
    >
      {/* 弹窗内容 */}
      <div 
        className="w-[600px] max-h-[70vh] rounded-lg overflow-hidden"
        style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-card)',
          boxShadow: 'var(--shadow-card)',
        }}
      >
        {/* 头部 */}
        <div 
          className="px-4 py-3 flex items-center justify-between border-b"
          style={{ borderColor: 'var(--border-divider)' }}
        >
          <div>
            <span 
              className="text-[13px] font-semibold"
              style={{ color: 'var(--accent-cyan)' }}
            >
              ▶ 导入错误详情
            </span>
            <span 
              className="ml-2 text-[12px]"
              style={{ color: 'var(--text-muted)' }}
            >
              任务 #{taskId}
            </span>
          </div>
          <button
            onClick={onClose}
            className="w-6 h-6 flex items-center justify-center rounded transition-colors"
            style={{
              color: 'var(--text-secondary)',
              background: 'rgba(180, 200, 240, 0.1)',
            }}
          >
            <svg 
              width="14" 
              height="14" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2"
            >
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* 内容区域 */}
        <div className="p-4 overflow-y-auto max-h-[calc(70vh - 60px)]">
          {isLoading ? (
            <div className="text-center py-8">
              <p style={{ color: 'var(--text-muted)' }}>加载中...</p>
            </div>
          ) : errors.length === 0 ? (
            <div className="text-center py-8">
              <p style={{ color: 'var(--text-muted)' }}>暂无错误记录</p>
            </div>
          ) : (
            <div className="space-y-2">
              {/* 统计信息 */}
              <div 
                className="mb-4 px-3 py-2 rounded-md"
                style={{
                  background: 'rgba(255, 71, 87, 0.08)',
                  border: '1px solid rgba(255, 71, 87, 0.2)',
                }}
              >
                <span 
                  className="text-[12px]"
                  style={{ color: 'var(--accent-red)' }}
                >
                  共 {errors.length} 条错误记录
                </span>
              </div>

              {/* 错误列表 */}
              {errors.map((error) => (
                <div 
                  key={error.id}
                  className="px-3 py-2 rounded-md"
                  style={{
                    background: 'var(--bg-input)',
                    border: '1px solid var(--border-divider)',
                  }}
                >
                  {/* 表名和编码 */}
                  <div className="flex items-center gap-3 mb-1">
                    <span 
                      className="text-[11px] px-2 py-0.5 rounded"
                      style={{
                        color: 'var(--accent-cyan)',
                        background: 'rgba(0, 212, 255, 0.1)',
                      }}
                    >
                      {error.table_name}
                    </span>
                    {error.code && (
                      <span 
                        className="text-[11px]"
                        style={{ color: 'var(--text-muted)' }}
                      >
                        编码: {error.code}
                      </span>
                    )}
                    {error.row_number && (
                      <span 
                        className="text-[11px]"
                        style={{ color: 'var(--text-muted)' }}
                      >
                        行号: {error.row_number}
                      </span>
                    )}
                  </div>
                  {/* 错误信息 */}
                  <p 
                    className="text-[12px]"
                    style={{ color: 'var(--accent-red)' }}
                  >
                    {error.error_message}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 底部 */}
        <div 
          className="px-4 py-3 border-t flex justify-end"
          style={{ borderColor: 'var(--border-divider)' }}
        >
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-md text-[12px] transition-colors"
            style={{
              background: 'var(--gradient-cyan)',
              color: '#fff',
            }}
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  );
}