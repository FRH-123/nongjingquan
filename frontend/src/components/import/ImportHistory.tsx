"use client";

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

interface ImportHistoryProps {
  tasks: ImportTask[];
  onViewDetails: (taskId: number) => void;
  isLoading?: boolean;
}

export default function ImportHistory({ tasks, onViewDetails, isLoading = false }: ImportHistoryProps) {
  // 格式化日期
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
  };

  // 状态标签样式
  const getStatusStyle = (status: string) => {
    switch (status) {
      case 'pending':
        return {
          color: 'var(--text-muted)',
          background: 'rgba(140, 165, 210, 0.12)',
          border: 'rgba(140, 165, 210, 0.3)',
          text: '等待处理',
        };
      case 'processing':
        return {
          color: 'var(--accent-cyan)',
          background: 'rgba(0, 212, 255, 0.12)',
          border: 'rgba(0, 212, 255, 0.3)',
          text: '处理中',
        };
      case 'completed':
        return {
          color: 'var(--accent-green)',
          background: 'rgba(0, 230, 118, 0.12)',
          border: 'rgba(0, 230, 118, 0.3)',
          text: '已完成',
        };
      case 'failed':
        return {
          color: 'var(--accent-red)',
          background: 'rgba(255, 71, 87, 0.12)',
          border: 'rgba(255, 71, 87, 0.3)',
          text: '失败',
        };
      default:
        return {
          color: 'var(--text-secondary)',
          background: 'rgba(180, 200, 240, 0.12)',
          border: 'rgba(180, 200, 240, 0.3)',
          text: status,
        };
    }
  };

  if (isLoading) {
    return (
      <div 
        className="w-full p-8 rounded-lg text-center"
        style={{
          background: 'var(--bg-input)',
          border: '1px solid var(--border-card)',
        }}
      >
        <p style={{ color: 'var(--text-muted)' }}>加载中...</p>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div 
        className="w-full p-8 rounded-lg text-center"
        style={{
          background: 'var(--bg-input)',
          border: '1px solid var(--border-card)',
        }}
      >
        <p style={{ color: 'var(--text-muted)' }}>暂无导入历史</p>
      </div>
    );
  }

  return (
    <div 
      className="w-full rounded-lg overflow-hidden"
      style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-card)',
      }}
    >
      {/* 表格 */}
      <table className="w-full">
        {/* 表头 */}
        <thead>
          <tr style={{ borderBottom: '1px solid var(--border-divider-strong)' }}>
            <th 
              className="px-3 py-2 text-left text-[11px] font-semibold whitespace-nowrap"
              style={{ color: 'var(--text-secondary)' }}
            >
              导入时间
            </th>
            <th 
              className="px-3 py-2 text-left text-[11px] font-semibold whitespace-nowrap"
              style={{ color: 'var(--text-secondary)' }}
            >
              文件名
            </th>
            <th 
              className="px-3 py-2 text-left text-[11px] font-semibold whitespace-nowrap"
              style={{ color: 'var(--text-secondary)' }}
            >
              状态
            </th>
            <th 
              className="px-3 py-2 text-center text-[11px] font-semibold whitespace-nowrap"
              style={{ color: 'var(--text-secondary)' }}
            >
              成功数
            </th>
            <th 
              className="px-3 py-2 text-center text-[11px] font-semibold whitespace-nowrap"
              style={{ color: 'var(--text-secondary)' }}
            >
              失败数
            </th>
            <th 
              className="px-3 py-2 text-center text-[11px] font-semibold whitespace-nowrap"
              style={{ color: 'var(--text-secondary)' }}
            >
              操作
            </th>
          </tr>
        </thead>
        {/* 表体 */}
        <tbody>
          {tasks.map((task, index) => {
            const statusStyle = getStatusStyle(task.status);
            return (
              <tr 
                key={task.id}
                className="transition-colors hover:bg-[rgba(0,100,200,0.08)]"
                style={{ 
                  borderBottom: index < tasks.length - 1 
                    ? '1px solid var(--border-divider-light)' 
                    : 'none',
                }}
              >
                <td 
                  className="px-3 py-2 text-[12px] whitespace-nowrap"
                  style={{ color: 'var(--text-primary)' }}
                >
                  {formatDate(task.created_at)}
                </td>
                <td 
                  className="px-3 py-2 text-[12px]"
                  style={{ color: 'var(--text-primary)' }}
                >
                  {task.filename}
                </td>
                <td className="px-3 py-2">
                  <span 
                    className="inline-block px-2 py-1 rounded text-[11px] font-medium whitespace-nowrap"
                    style={{
                      color: statusStyle.color,
                      background: statusStyle.background,
                      border: `1px solid ${statusStyle.border}`,
                    }}
                  >
                    {statusStyle.text}
                  </span>
                </td>
                <td 
                  className="px-3 py-2 text-center text-[12px] font-semibold"
                  style={{ color: 'var(--accent-green)' }}
                >
                  {task.success_count}
                </td>
                <td 
                  className="px-3 py-2 text-center text-[12px] font-semibold"
                  style={{ color: task.error_count > 0 ? 'var(--accent-red)' : 'var(--text-muted)' }}
                >
                  {task.error_count}
                </td>
                <td className="px-3 py-2 text-center">
                  <button
                    onClick={() => onViewDetails(task.id)}
                    className="px-2 py-1 rounded text-[11px] transition-colors"
                    style={{
                      color: 'var(--accent-cyan)',
                      background: 'rgba(0, 212, 255, 0.1)',
                    }}
                  >
                    详情
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}