"use client";

interface TypeTagProps {
  type: string;
}

export default function TypeTag({ type }: TypeTagProps) {
  return (
    <span
      className="inline-block px-[6px] py-[2px] rounded-[3px] text-[11px] whitespace-nowrap"
      style={{
        background: 'rgba(100,160,255,0.1)',
        color: 'var(--text-secondary)',
        border: '1px solid rgba(100,160,255,0.2)',
      }}
    >
      {type}
    </span>
  );
}