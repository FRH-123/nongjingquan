"use client";

import { useState, useCallback } from 'react';

interface DropZoneProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
}

export default function DropZone({ onFileSelect, disabled = false }: DropZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setIsDragging(true);
  }, [disabled]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (disabled) return;

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.name.toLowerCase().endsWith('.zip')) {
        setSelectedFile(file);
        onFileSelect(file);
      } else {
        alert('请上传 ZIP 格式的文件');
      }
    }
  }, [disabled, onFileSelect]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.name.toLowerCase().endsWith('.zip')) {
        setSelectedFile(file);
        onFileSelect(file);
      } else {
        alert('请上传 ZIP 格式的文件');
      }
    }
  }, [onFileSelect]);

  const clearFile = useCallback(() => {
    setSelectedFile(null);
  }, []);

  return (
    <div className="w-full">
      {/* 拖拽区域 */}
      <div
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        className="relative w-full h-[160px] rounded-lg flex flex-col items-center justify-center transition-all duration-200 cursor-pointer"
        style={{
          background: isDragging 
            ? 'rgba(0, 212, 255, 0.08)' 
            : 'var(--bg-input)',
          border: isDragging 
            ? '2px dashed var(--accent-cyan)' 
            : '1px dashed var(--border-card)',
          opacity: disabled ? 0.6 : 1,
        }}
      >
        {/* 上传图标 */}
        <div 
          className="mb-3"
          style={{
            color: isDragging ? 'var(--accent-cyan)' : 'var(--text-secondary)',
          }}
        >
          <svg 
            width="48" 
            height="48" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="1.5"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
        </div>

        {/* 提示文字 */}
        <p 
          className="text-[13px] mb-1"
          style={{ color: 'var(--text-secondary)' }}
        >
          {isDragging ? '释放文件开始上传' : '拖拽 ZIP 文件到此处'}
        </p>
        <p 
          className="text-[11px]"
          style={{ color: 'var(--text-muted)' }}
        >
          或点击下方按钮选择文件
        </p>

        {/* 文件选择按钮 */}
        <label 
          className="mt-3 px-4 py-2 rounded-md text-[12px] cursor-pointer transition-all duration-200"
          style={{
            background: 'var(--gradient-cyan)',
            color: '#fff',
            opacity: disabled ? 0.5 : 1,
          }}
        >
          选择文件
          <input
            type="file"
            accept=".zip"
            onChange={handleFileInput}
            disabled={disabled}
            className="hidden"
          />
        </label>
      </div>

      {/* 已选择的文件 */}
      {selectedFile && (
        <div 
          className="mt-3 px-3 py-2 rounded-md flex items-center justify-between"
          style={{
            background: 'rgba(0, 212, 255, 0.08)',
            border: '1px solid rgba(0, 212, 255, 0.2)',
          }}
        >
          <div className="flex items-center gap-2">
            <svg 
              width="16" 
              height="16" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2"
              style={{ color: 'var(--accent-cyan)' }}
            >
              <path d="M21 8v13H3V8" />
              <path d="M3 8l9-6 9 6" />
            </svg>
            <span 
              className="text-[12px]"
              style={{ color: 'var(--text-primary)' }}
            >
              {selectedFile.name}
            </span>
            <span 
              className="text-[11px]"
              style={{ color: 'var(--text-muted)' }}
            >
              ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
            </span>
          </div>
          {!disabled && (
            <button
              onClick={clearFile}
              className="text-[11px] px-2 py-1 rounded transition-colors"
              style={{
                color: 'var(--accent-red)',
                background: 'rgba(255, 71, 87, 0.1)',
              }}
            >
              移除
            </button>
          )}
        </div>
      )}
    </div>
  );
}