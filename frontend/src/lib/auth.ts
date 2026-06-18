/**
 * 前端认证工具
 * 处理 token 存取、登录状态检查、登出等操作
 */

const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

export interface AuthUser {
  username: string;
  role: string;
}

/**
 * 保存认证 token
 */
export function setToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, token);
  }
}

/**
 * 获取认证 token
 */
export function getToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(TOKEN_KEY);
  }
  return null;
}

/**
 * 移除认证 token
 */
export function removeToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
}

/**
 * 保存用户信息
 */
export function setUser(user: AuthUser): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }
}

/**
 * 获取用户信息
 */
export function getUser(): AuthUser | null {
  if (typeof window !== 'undefined') {
    const userStr = localStorage.getItem(USER_KEY);
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch {
        return null;
      }
    }
  }
  return null;
}

/**
 * 检查是否已登录
 */
export function isAuthenticated(): boolean {
  return !!getToken();
}

/**
 * 登出 - 清除所有认证信息
 */
export function logout(): void {
  removeToken();
}

/**
 * 登录 API 调用
 */
export async function login(username: string, password: string): Promise<{ success: boolean; token?: string; user?: AuthUser; error?: string }> {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (response.ok && data.success) {
      setToken(data.token);
      setUser(data.user);
      return { success: true, token: data.token, user: data.user };
    } else {
      return { success: false, error: data.message || '登录失败' };
    }
  } catch {
    return { success: false, error: '网络错误，请检查连接' };
  }
}