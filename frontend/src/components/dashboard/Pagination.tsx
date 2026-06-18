"use client";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export default function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
  const handlePrev = () => {
    if (currentPage > 1) {
      onPageChange(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (currentPage < totalPages) {
      onPageChange(currentPage + 1);
    }
  };

  const handleGoTo = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      const page = parseInt(e.currentTarget.value);
      if (page >= 1 && page <= totalPages) {
        onPageChange(page);
      }
    }
  };

  // 生成页码显示
  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    const maxVisible = 5;
    
    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (currentPage <= 3) {
        pages.push(1, 2, 3, 4, '...', totalPages);
      } else if (currentPage >= totalPages - 2) {
        pages.push(1, '...', totalPages - 3, totalPages - 2, totalPages - 1, totalPages);
      } else {
        pages.push(1, '...', currentPage - 1, currentPage, currentPage + 1, '...', totalPages);
      }
    }
    
    return pages;
  };

  return (
    <div className="flex items-center justify-center gap-[8px] py-[10px]">
      {/* 上一页 */}
      <button
        onClick={handlePrev}
        disabled={currentPage === 1}
        className="w-[26px] h-[26px] flex items-center justify-center rounded-[4px] transition-colors"
        style={{
          background: 'rgba(10,20,50,0.5)',
          border: '1px solid var(--border-card)',
          color: currentPage === 1 ? 'var(--text-muted)' : 'var(--text-secondary)',
          cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
        }}
      >
        ◄
      </button>

      {/* 页码 */}
      {getPageNumbers().map((page, index) => (
        typeof page === 'number' ? (
          <button
            key={index}
            onClick={() => onPageChange(page)}
            className="w-[26px] h-[26px] flex items-center justify-center rounded-[4px] text-[12px] transition-colors"
            style={{
              background: page === currentPage ? 'var(--accent-cyan)' : 'rgba(10,20,50,0.5)',
              border: '1px solid var(--border-card)',
              color: page === currentPage ? '#fff' : 'var(--text-secondary)',
            }}
          >
            {page}
          </button>
        ) : (
          <span key={index} className="text-[12px]" style={{ color: 'var(--text-secondary)' }}>
            {page}
          </span>
        )
      ))}

      {/* 下一页 */}
      <button
        onClick={handleNext}
        disabled={currentPage === totalPages}
        className="w-[26px] h-[26px] flex items-center justify-center rounded-[4px] transition-colors"
        style={{
          background: 'rgba(10,20,50,0.5)',
          border: '1px solid var(--border-card)',
          color: currentPage === totalPages ? 'var(--text-muted)' : 'var(--text-secondary)',
          cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
        }}
      >
        ►
      </button>

      {/* 前往 */}
      <span className="text-[12px] ml-[8px]" style={{ color: 'var(--text-secondary)' }}>
        前往
      </span>
      <input
        type="text"
        className="w-[30px] h-[26px] text-center rounded-[4px] text-[12px]"
        style={{
          background: 'rgba(10,20,50,0.5)',
          border: '1px solid var(--border-card)',
          color: 'var(--text-secondary)',
        }}
        onKeyDown={handleGoTo}
        placeholder=""
      />
      <span className="text-[12px]" style={{ color: 'var(--text-secondary)' }}>
        页
      </span>
    </div>
  );
}