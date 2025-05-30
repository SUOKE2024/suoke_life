"""
缓存管理工具

提供算诊结果的缓存功能
"""

import json
import hashlib
import time
from typing import Any, Dict, Optional
from functools import wraps


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, ttl: int = 3600):
        """
        初始化缓存管理器
        
        Args:
            ttl: 缓存生存时间（秒）
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl
    
    def _generate_key(self, data: Dict[str, Any]) -> str:
        """
        生成缓存键
        
        Args:
            data: 数据字典
            
        Returns:
            缓存键
        """
        # 将数据转换为JSON字符串并计算MD5哈希
        json_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(json_str.encode('utf-8')).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存数据
        
        Args:
            key: 缓存键
            
        Returns:
            缓存的数据，如果不存在或过期则返回None
        """
        if key not in self.cache:
            return None
        
        cache_item = self.cache[key]
        current_time = time.time()
        
        # 检查是否过期
        if current_time - cache_item["timestamp"] > self.ttl:
            del self.cache[key]
            return None
        
        return cache_item["data"]
    
    def set(self, key: str, data: Any) -> None:
        """
        设置缓存数据
        
        Args:
            key: 缓存键
            data: 要缓存的数据
        """
        self.cache[key] = {
            "data": data,
            "timestamp": time.time()
        }
    
    def delete(self, key: str) -> bool:
        """
        删除缓存数据
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """清空所有缓存"""
        self.cache.clear()
    
    def cleanup_expired(self) -> int:
        """
        清理过期缓存
        
        Returns:
            清理的缓存项数量
        """
        current_time = time.time()
        expired_keys = []
        
        for key, cache_item in self.cache.items():
            if current_time - cache_item["timestamp"] > self.ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计信息
        """
        current_time = time.time()
        total_items = len(self.cache)
        expired_items = 0
        
        for cache_item in self.cache.values():
            if current_time - cache_item["timestamp"] > self.ttl:
                expired_items += 1
        
        return {
            "total_items": total_items,
            "active_items": total_items - expired_items,
            "expired_items": expired_items,
            "ttl": self.ttl
        }


# 全局缓存实例
cache_manager = CacheManager()


def cached_calculation(cache_key_func=None):
    """
    算诊计算缓存装饰器
    
    Args:
        cache_key_func: 自定义缓存键生成函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                # 默认使用函数名和参数生成键
                key_data = {
                    "function": func.__name__,
                    "args": args,
                    "kwargs": kwargs
                }
                cache_key = cache_manager._generate_key(key_data)
            
            # 尝试从缓存获取结果
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行计算
            result = func(*args, **kwargs)
            
            # 缓存结果
            cache_manager.set(cache_key, result)
            
            return result
        
        return wrapper
    return decorator


def generate_birth_info_cache_key(birth_info: Dict[str, Any], analysis_date: str = None) -> str:
    """
    生成出生信息缓存键
    
    Args:
        birth_info: 出生信息
        analysis_date: 分析日期
        
    Returns:
        缓存键
    """
    key_data = {
        "birth_info": birth_info,
        "analysis_date": analysis_date
    }
    return cache_manager._generate_key(key_data)


def generate_time_analysis_cache_key(analysis_time: str) -> str:
    """
    生成时间分析缓存键
    
    Args:
        analysis_time: 分析时间
        
    Returns:
        缓存键
    """
    # 只缓存到小时级别，避免缓存过于细粒度
    time_parts = analysis_time.split(":")
    if len(time_parts) >= 2:
        hour_time = f"{time_parts[0]}:{time_parts[1]}"
    else:
        hour_time = analysis_time
    
    key_data = {"analysis_time": hour_time}
    return cache_manager._generate_key(key_data) 