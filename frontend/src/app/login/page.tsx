"use client";

import { useSearchParams } from 'next/navigation';
import LoginForm from '@/components/auth/LoginForm';

export default function LoginPage() {
  const searchParams = useSearchParams();
  const redirectPath = searchParams.get('redirect') || '/dashboard';

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
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
            radial-gradient(ellipse 80% 50% at 50% 0%, rgba(0,80,180,0.15), transparent 60%),
            radial-gradient(ellipse 60% 40% at 80% 100%, rgba(0,160,255,0.08), transparent 50%),
            radial-gradient(ellipse 50% 30% at 10% 80%, rgba(100,0,200,0.06), transparent 50%)
          `,
        }}
      />

      {/* 登录卡片 */}
      <div 
        className="relative w-[400px] rounded-lg p-8"
        style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-card)',
          boxShadow: 'var(--shadow-card)',
        }}
      >
        {/* 标题 */}
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

        {/* 登录表单 */}
        <LoginForm redirectPath={redirectPath} />

        {/* 底部提示 */}
        <div className="mt-6 text-center">
          <p 
            className="text-[11px]"
            style={{ color: 'var(--text-muted)' }}
          >
            默认账号: admin / admin
          </p>
        </div>
      </div>
    </div>
  );
}