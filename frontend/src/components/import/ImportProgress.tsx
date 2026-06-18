"use client";

interface ImportProgressProps {
  progress: number;
  status: string;
  message?: string;
  successCount?: number;
  errorCount?: number;
  totalCount?: number;
}

export default function ImportProgress({
  progress,
  status,
  message,
  successCount = 0,
  errorCount = 0,
  totalCount = 0,
}: ImportProgressProps) {
  // 状态颜色映射
  const getStatusColor = () => {
    switch (status) {
      case 'pending':
        return 'var(--text-muted)';
      case 'processing':
        return 'var(--accent-cyan)';
      case 'completed':
        return 'var(--accent-green)';
      case 'failed':
        return 'var(--accent-red)';
      default:
        return 'var(--text-secondary)';
    }
  };

  // 状态文字映射
  const getStatusText = () => {
    switch (status) {
      case 'pending':
        return '等待处理';
      case 'processing':
        return '处理中';
      case 'completed':
        return '已完成';
      case 'failed':
        return '失败';
      default:
        return status;
    }
  };

  return (
    <div 
      className="w-full p-4 rounded-lg"
      style={{
        background: 'var(--bg-input)',
        border: '1px solid var(--border-card)',
      }}
    >
      {/* 状态标签 */}
      <div className="flex items-center justify-between mb-3">
        <span 
          className="text-[12px] font-semibold px-2 py-1 rounded"
          style={{
            color: getStatusColor(),
            background: `${getStatusColor()}20`,
          }}
        >
          {getStatusText()}
        </span>
        <span 
          className="text-[13px] font-bold"
          style={{ color: 'var(--text-value)' }}
        >
          {Math.round(progress)}%
        </span>
      </div>

      {/* 进度条 */}
      <div 
        className="w-full h-[8px] rounded-full overflow-hidden"
        style={{ background: 'rgba(32, 80, 160, 0.2)' }}
      >
        <div 
          className="h-full rounded-full transition-all duration-300"
          style={{
            width: `${progress}%`,
            background: status === 'failed' 
              ? 'var(--gradient-red)' 
              : 'var(--gradient-cyan)',
          }}
        />
      </div>

      {/* 统计信息 */}
      {totalCount > 0 && (
        <div className="mt-3 flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span 
              className="text-[11px]"
              style={{ color: 'var(--text-muted)' }}
            >
              总数:
            </span>
            <span 
              className="text-[12px] font-semibold"
              style={{ color: 'var(--text-primary)' }}
            >
              {totalCount}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span 
              className="text-[11px]"
              style={{ color: 'var(--text-muted)' }}
            >
              成功:
            </span>
            <span 
              className="text-[12px] font-semibold"
              style={{ color: 'var(--accent-green)' }}
            >
              {successCount}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span 
              className="text-[11px]"
              style={{ color: 'var(--text-muted)' }}
            >
              失败:
            </span>
            <span 
              className="text-[12px] font-semibold"
              style={{ color: 'var(--accent-red)' }}
            >
              {errorCount}
            </span>
          </div>
        </div>
      )}

      {/* 消息 */}
      {message && (
        <p 
          className="mt-2 text-[12px]"
          style={{ color: 'var(--text-secondary)' }}
        >
          {message}
        </p>
      )}
    </div>
  );
}