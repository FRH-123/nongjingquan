"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const isButtonDisabled = isLoading || !username || !password;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        document.cookie = `auth_token=${data.token}; path=/; max-age=86400`;
        router.push('/dashboard');
      } else {
        setError(data.message || '登录失败');
      }
    } catch {
      setError('网络错误，请检查连接');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      {/* 背景 */}
      <div className="absolute inset-0 pointer-events-none" style={{ background: 'var(--bg-primary)' }} />
      {/* 氛围光效 */}
      <div className="absolute inset-0 pointer-events-none" style={{
        background: `
          radial-gradient(ellipse 80% 50% at 50% 0%, rgba(0,80,180,0.15), transparent 60%),
          radial-gradient(ellipse 60% 40% at 80% 100%, rgba(0,160,255,0.08), transparent 50%),
          radial-gradient(ellipse 50% 30% at 10% 80%, rgba(100,0,200,0.06), transparent 50%)
        `,
      }} />

      {/* 登录卡片 */}
      <div className="relative w-[400px] rounded-lg p-8" style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-card)',
        boxShadow: 'var(--shadow-card)',
      }}>
        <div className="text-center mb-8">
          <h1 className="text-[20px] font-bold tracking-[4px] mb-2" style={{ color: 'var(--text-primary)' }}>
            农经权二轮延包可视化平台
          </h1>
          <div className="w-[60%] h-[1px] mx-auto" style={{ background: 'var(--gradient-header-line)' }} />
        </div>

        <form onSubmit={handleSubmit} className="w-full max-w-[320px]">
          <div className="mb-4">
            <label className="block text-[13px] font-semibold tracking-[1px] mb-2" style={{ color: 'var(--text-secondary)' }}>
              用户名
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="admin"
              disabled={isLoading}
              className="w-full px-3 py-2.5 rounded-md text-[13px] outline-none transition-all duration-200"
              style={{
                background: 'var(--bg-input)',
                border: '1px solid var(--border-card)',
                color: 'var(--text-primary)',
              }}
              onFocus={(e) => { e.target.style.borderColor = 'var(--accent-cyan)'; }}
              onBlur={(e) => { e.target.style.borderColor = 'var(--border-card)'; }}
            />
          </div>

          <div className="mb-6">
            <label className="block text-[13px] font-semibold tracking-[1px] mb-2" style={{ color: 'var(--text-secondary)' }}>
              密码
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="admin"
              disabled={isLoading}
              className="w-full px-3 py-2.5 rounded-md text-[13px] outline-none transition-all duration-200"
              style={{
                background: 'var(--bg-input)',
                border: '1px solid var(--border-card)',
                color: 'var(--text-primary)',
              }}
              onFocus={(e) => { e.target.style.borderColor = 'var(--accent-cyan)'; }}
              onBlur={(e) => { e.target.style.borderColor = 'var(--border-card)'; }}
            />
          </div>

          {error && (
            <div className="mb-4 px-3 py-2 rounded-md text-[12px]" style={{
              background: 'rgba(255, 71, 87, 0.12)',
              border: '1px solid rgba(255, 71, 87, 0.3)',
              color: 'var(--accent-red)',
            }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isButtonDisabled}
            className="w-full py-3 rounded-md text-[14px] font-semibold tracking-[1px] transition-all duration-200"
            style={{
              background: isButtonDisabled ? 'rgba(32, 80, 160, 0.35)' : 'linear-gradient(90deg, #0066cc, #00d4ff)',
              color: '#fff',
              cursor: isButtonDisabled ? 'not-allowed' : 'pointer',
              opacity: isButtonDisabled ? 0.7 : 1,
            }}
          >
            {isLoading ? '登录中...' : '登 录'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-[11px]" style={{ color: 'var(--text-muted)' }}>
            默认账号: admin / admin
          </p>
        </div>
      </div>
    </div>
  );
}