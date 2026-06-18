"use client";

export type StatusType = '待公示' | '村干部审核' | '未调查' | '待审核';

interface StatusTagProps {
  status: StatusType;
}

const statusStyles: Record<StatusType, { bg: string; text: string; border: string }> = {
  '待公示': {
    bg: 'rgba(0,230,118,0.12)',
    text: '#00e676',
    border: 'rgba(0,230,118,0.3)',
  },
  '村干部审核': {
    bg: 'rgba(0,212,255,0.12)',
    text: '#00d4ff',
    border: 'rgba(0,212,255,0.3)',
  },
  '未调查': {
    bg: 'rgba(255,71,87,0.12)',
    text: '#ff6b7a',
    border: 'rgba(255,71,87,0.3)',
  },
  '待审核': {
    bg: 'rgba(255,184,48,0.15)',
    text: '#ffb830',
    border: 'rgba(255,184,48,0.3)',
  },
};

export default function StatusTag({ status }: StatusTagProps) {
  const styles = statusStyles[status];

  return (
    <span
      className="inline-block px-[8px] py-[2px] rounded-[3px] text-[11px] font-medium whitespace-nowrap"
      style={{
        background: styles.bg,
        color: styles.text,
        border: `1px solid ${styles.border}`,
      }}
    >
      {status}
    </span>
  );
}