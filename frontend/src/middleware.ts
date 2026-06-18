import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Next.js 路由守卫中间件
 * 未登录访问 /dashboard 或 /import 时重定向到 /login
 */

// 需要认证保护的路由
const protectedRoutes = ['/', '/dashboard', '/import', '/quality', '/trend'];

// 公开路由（不需要认证）
const publicRoutes = ['/login', '/api'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // 检查是否是公开路由
  const isPublicRoute = publicRoutes.some(route => 
    pathname === route || pathname.startsWith(route + '/')
  );
  
  // 如果是公开路由，直接放行
  if (isPublicRoute) {
    return NextResponse.next();
  }
  
  // 检查是否是受保护路由
  const isProtectedRoute = protectedRoutes.some(route => 
    pathname === route || pathname.startsWith(route + '/')
  );
  
  // 如果不是受保护路由，直接放行
  if (!isProtectedRoute) {
    return NextResponse.next();
  }
  
  // 检查认证 token
  const token = request.cookies.get('auth_token')?.value;
  
  // 如果没有 token，重定向到登录页
  if (!token) {
    const loginUrl = new URL('/login', request.url);
    // 保存原始请求路径，登录后可以跳转回去
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }
  
  // 有 token，放行
  return NextResponse.next();
}

// 配置匹配的路径
export const config = {
  matcher: [
    /*
     * 匹配所有路径，除了：
     * - _next/static (静态文件)
     * - _next/image (图片优化文件)
     * - favicon.ico (网站图标)
     * - public folder 中的文件
     */
    '/((?!_next/static|_next/image|favicon.ico|public/).*)',
  ],
};