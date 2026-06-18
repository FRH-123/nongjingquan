"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginForm() {
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
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
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

  const isButtonDisabled = isLoading || !username || !password;

  return (
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
          onFocus={(e) => {
            e.target.style.borderColor = 'var(--accent-cyan)';
          }}
          onBlur={(e) => {
            e.target.style.borderColor = 'var(--border-card)';
          }}
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
          onFocus={(e) => {
            e.target.style.borderColor = 'var(--accent-cyan)';
          }}
          onBlur={(e) => {
            e.target.style.borderColor = 'var(--border-card)';
          }}
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
  );
}