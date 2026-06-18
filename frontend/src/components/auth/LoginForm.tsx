"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { login } from '@/lib/auth';

interface LoginFormProps {
  redirectPath?: string;
}

export default function LoginForm({ redirectPath = '/dashboard' }: LoginFormProps) {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const result = await login(username, password);
      
      if (result.success) {
        // 保存认证信息到 cookie（用于 middleware）
        document.cookie = `auth_token=${result.token}; path=/; max-age=86400`;
        
        // 跳转到目标页面
        router.push(redirectPath);
      } else {
        setError(result.error || '登录失败');
      }
    } catch {
      setError('登录请求失败，请检查网络连接');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-[320px]">
      {/* 用户名输入 */}
      <div className="mb-4">
        <label 
          className="block text-[13px] font-semibold tracking-[1px] mb-2"
          style={{ color: 'var(--text-secondary)' }}
        >
          用户名
        </label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="请输入用户名"
          disabled={isLoading}
          className="w-full px-3 py-2.5 rounded-md text-[13px] outline-none transition-all duration-200"
          style={{
            background: 'var(--bg-input)',
            border: '1px solid var(--border-card)',
            color: 'var(--text-primary)',
          }}
          onFocus={(e) => {
            e.target.style.borderColor = 'var(--accent-cyan)';
          }}
          onBlur={(e) => {
            e.target.style.borderColor = 'var(--border-card)';
          }}
        />
      </div>

      {/* 密码输入 */}
      <div className="mb-6">
        <label 
          className="block text-[13px] font-semibold tracking-[1px] mb-2"
          style={{ color: 'var(--text-secondary)' }}
        >
          密码
        </label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="请输入密码"
          disabled={isLoading}
          className="w-full px-3 py-2.5 rounded-md text-[13px] outline-none transition-all duration-200"
          style={{
            background: 'var(--bg-input)',
            border: '1px solid var(--border-card)',
            color: 'var(--text-primary)',
          }}
          onFocus={(e) => {
            e.target.style.borderColor = 'var(--accent-cyan)';
          }}
          onBlur={(e) => {
            e.target.style.borderColor = 'var(--border-card)';
          }}
        />
      </div>

      {/* 错误提示 */}
      {error && (
        <div 
          className="mb-4 px-3 py-2 rounded-md text-[12px]"
          style={{
            background: 'rgba(255, 71, 87, 0.12)',
            border: '1px solid rgba(255, 71, 87, 0.3)',
            color: 'var(--accent-red)',
          }}
        >
          {error}
        </div>
      )}

      {/* 登录按钮 */}
      <button
        type="submit"
        disabled={isLoading || !username || !password}
        className="w-full py-3 rounded-md text-[14px] font-semibold tracking-[1px] transition-all duration-200"
        style={{
          background: isLoading || !username || !password 
            ? 'rgba(32, 80, 160, 0.35)' 
            : 'var(--gradient-cyan)',
          color: '#fff',
          cursor: isLoading || !username || !password ? 'not-allowed' : 'pointer',
          opacity: isLoading || !username || !password ? 0.7 : 1,
        }}
      >
        {isLoading ? '登录中...' : '登 录'}
      </button>
    </form>
  );
}