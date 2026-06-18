"""
缓存服务 (CacheService)
支持 Redis 缓存，如果 Redis 不可用则使用内存缓存替代
"""
import json
import time
from typing import Optional, Any, Dict
from datetime import datetime, timedelta

from app.config import settings


class CacheService:
    """
    缓存服务类
    支持 Redis 和内存缓存两种模式
    """
    
    # 默认缓存 TTL（秒）
    DEFAULT_TTL = 300  # 5 分钟
    
    # 内存缓存存储
    _memory_cache: Dict[str, Dict[str, Any]] = {}
    
    # Redis 客户端（可选）
    _redis_client: Optional[Any] = None
    
    def __init__(self):
        """初始化缓存服务"""
        self._init_redis()
    
    def _init_redis(self):
        """尝试初始化 Redis 连接"""
        if settings.REDIS_URL:
            try:
                import redis
                self._redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True
                )
                # 测试连接
                self._redis_client.ping()
                print("Redis 缓存已连接")
            except Exception as e:
                print(f"Redis 连接失败，使用内存缓存: {e}")
                self._redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或已过期则返回 None
        """
        if self._redis_client:
            try:
                value = self._redis_client.get(key)
                if value:
                    return json.loads(value)
                return None
            except Exception as e:
                print(f"Redis get 错误: {e}")
                return self._memory_get(key)
        else:
            return self._memory_get(key)
    
    def _memory_get(self, key: str) -> Optional[Any]:
        """从内存缓存获取值"""
        if key not in self._memory_cache:
            return None
        
        cache_item = self._memory_cache[key]
        if cache_item["expires_at"] < time.time():
            # 已过期，删除缓存
            del self._memory_cache[key]
            return None
        
        return cache_item["value"]
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），默认 5 分钟
            
        Returns:
            是否成功
        """
        ttl = ttl or self.DEFAULT_TTL
        
        if self._redis_client:
            try:
                self._redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value, ensure_ascii=False, default=str)
                )
                return True
            except Exception as e:
                print(f"Redis set 错误: {e}")
                return self._memory_set(key, value, ttl)
        else:
            return self._memory_set(key, value, ttl)
    
    def _memory_set(self, key: str, value: Any, ttl: int) -> bool:
        """设置内存缓存"""
        self._memory_cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl
        }
        return True
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功
        """
        if self._redis_client:
            try:
                self._redis_client.delete(key)
                return True
            except Exception as e:
                print(f"Redis delete 错误: {e}")
        
        if key in self._memory_cache:
            del self._memory_cache[key]
        return True
    
    def delete_pattern(self, pattern: str) -> int:
        """
        删除匹配模式的缓存
        
        Args:
            pattern: 缓存键模式（如 "indicator:*"）
            
        Returns:
            删除的缓存数量
        """
        count = 0
        
        if self._redis_client:
            try:
                keys = self._redis_client.keys(pattern)
                if keys:
                    count = self._redis_client.delete(*keys)
            except Exception as e:
                print(f"Redis delete_pattern 错误: {e}")
        
        # 同时清理内存缓存
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            keys_to_delete = [k for k in self._memory_cache.keys() if k.startswith(prefix)]
            for k in keys_to_delete:
                del self._memory_cache[k]
                count += 1
        
        return count
    
    def clear_all_indicators(self) -> int:
        """
        清除所有指标缓存
        
        Returns:
            删除的缓存数量
        """
        return self.delete_pattern("indicator:*")
    
    def refresh_cache(self) -> bool:
        """
        刷新所有指标缓存（导入新数据后调用）
        
        Returns:
            是否成功
        """
        self.clear_all_indicators()
        return True
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计信息
        """
        stats = {
            "type": "redis" if self._redis_client else "memory",
            "indicator_keys": 0,
        }
        
        if self._redis_client:
            try:
                keys = self._redis_client.keys("indicator:*")
                stats["indicator_keys"] = len(keys)
                stats["redis_connected"] = True
            except Exception:
                stats["redis_connected"] = False
        else:
            keys = [k for k in self._memory_cache.keys() if k.startswith("indicator:")]
            stats["indicator_keys"] = len(keys)
            stats["memory_cache_size"] = len(self._memory_cache)
        
        return stats


# 全局缓存服务实例
cache_service = CacheService()