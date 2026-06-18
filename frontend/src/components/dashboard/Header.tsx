"use client";

import Link from 'next/link';

export default function Header() {
  const currentDate = new Date();
  const formattedDate = `${currentDate.getFullYear()}年${String(currentDate.getMonth() + 1).padStart(2, "0")}月${String(currentDate.getDate()).padStart(2, "0")}日`;

  return (
    <header className="relative py-2 px-5 bg-[var(--gradient-header-bg)] border-b border-[var(--border-highlight)]">
      <div className="flex items-center justify-between">
        {/* 左侧导航 */}
        <div className="flex-1 flex items-center gap-4">
          <Link 
            href="/import"
            className="flex items-center gap-2 px-3 py-1.5 rounded-md transition-colors text-[12px]"
            style={{
              color: 'var(--accent-cyan)',
              background: 'rgba(0, 212, 255, 0.1)',
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
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            数据导入
          </Link>
        </div>
        
        {/* 标题 */}
        <h1 
          className="text-[22px] font-bold tracking-[6px] text-transparent bg-clip-text"
          style={{ backgroundImage: "var(--gradient-title)" }}
        >
          农经权二轮延包可视化平台
        </h1>
        
        {/* 右侧日期 */}
        <div className="flex-1 flex justify-end">
          <span className="text-[13px] text-[var(--text-secondary)] tracking-[1px]">
            {formattedDate}
          </span>
        </div>
      </div>
      {/* 渐变装饰线 */}
      <div 
        className="absolute bottom-[-1px] left-[10%] right-[10%] h-[1px]"
        style={{ background: "var(--gradient-header-line)" }}
      />
    </header>
  );
}