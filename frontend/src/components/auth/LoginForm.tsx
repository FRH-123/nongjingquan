"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface LoginFormProps {
  redirectPath?: string;
}

export default function LoginForm({ redirectPath = '/dashboard' }: LoginFormProps) {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const canSubmit = !isLoading && username.length > 0 && password.length > 0;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        document.cookie = `auth_token=${data.token}; path=/; max-age=86400`;
        router.push(redirectPath);
      } else {
        setError(data.message || '登录失败');
      }
    } catch (err) {
      setError('网络错误，请检查连接');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-[320px]">
      <div className="mb-4">
        <label className="block text-[13px] font-semibold tracking-[1px] mb-2" style={{ color: 'var(--text-secondary)' }}>
          用户名
        </label>
        <input
          type="text"
          value={username}
          onChange={(e) => {
            console.log('username:', e.target.value);
            setUsername(e.target.value);
          }}
          placeholder="请输入用户名"
          disabled={isLoading}
          className="w-full px-3 py-2.5 rounded-md text-[13px] outline-none transition-all duration-200"
          style={{
            background: 'var(--bg-input)',
            border: '1px solid var(--border-card)',
            color: 'var(--text-primary)',
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
          onChange={(e) => {
            console.log('password:', e.target.value);
            setPassword(e.target.value);
          }}
          placeholder="请输入密码"
          disabled={isLoading}
          className="w-full px-3 py-2.5 rounded-md text-[13px] outline-none transition-all duration-200"
          style={{
            background: 'var(--bg-input)',
            border: '1px solid var(--border-card)',
            color: 'var(--text-primary)',
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

      <div className="mb-4 text-xs text-gray-500">
        Debug: canSubmit={canSubmit}, username={username}, password={password}
      </div>

      <button
        type="submit"
        disabled={!canSubmit}
        className="w-full py-3 rounded-md text-[14px] font-semibold tracking-[1px] transition-all duration-200"
        style={{
          background: canSubmit ? 'var(--gradient-cyan)' : 'rgba(32, 80, 160, 0.35)',
          color: '#fff',
          cursor: canSubmit ? 'pointer' : 'not-allowed',
          opacity: canSubmit ? 1 : 0.7,
        }}
      >
        {isLoading ? '登录中...' : '登 录'}
      </button>
    </form>
  );
}