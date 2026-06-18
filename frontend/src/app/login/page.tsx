"use client";

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import LoginForm from '@/components/auth/LoginForm';

function LoginContent() {
  const searchParams = useSearchParams();
  const redirectPath = searchParams.get('redirect') || '/dashboard';

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      <div
        className="absolute inset-0"
        style={{ background: 'var(--bg-primary)' }}
      />
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: `
            radial-gradient(ellipse 80% 50% at 50% 0%, rgba(0,80,180,0.15), transparent 60%),
            radial-gradient(ellipse 60% 40% at 80% 100%, rgba(0,160,255,0.08), transparent 50%),
            radial-gradient(ellipse 50% 30% at 10% 80%, rgba(100,0,200,0.06), transparent 50%)
          `,
        }}
      />
      <div
        className="relative w-[400px] rounded-lg p-8"
        style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-card)',
          boxShadow: 'var(--shadow-card)',
        }}
      >
        <div className="text-center mb-8">
          <h1
            className="text-[20px] font-bold tracking-[4px] mb-2"
            style={{ color: 'var(--text-primary)' }}
          >
            农经权二轮延包可视化平台
          </h1>
          <div
            className="w-[60%] h-[1px] mx-auto"
            style={{ background: 'var(--gradient-header-line)' }}
          />
        </div>
        <LoginForm redirectPath={redirectPath} />
        <div className="mt-6 text-center">
          <p className="text-[11px]" style={{ color: 'var(--text-muted)' }}>
            默认账号: admin / admin
          </p>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--bg-primary)' }}>
        <p style={{ color: 'var(--text-muted)' }}>加载中...</p>
      </div>
    }>
      <LoginContent />
    </Suspense>
  );
}