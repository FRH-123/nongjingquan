import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "农经权二轮延包可视化平台",
  description: "农经权二轮延包数据监控可视化大屏平台",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" className="h-full antialiased">
      <body className="min-h-full flex flex-col">
        {children}
      </body>
    </html>
  );
}