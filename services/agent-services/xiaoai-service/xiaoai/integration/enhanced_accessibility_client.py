#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版无障碍服务客户端
包含连接池管理、缓存机制、错误处理和降级策略
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from functools import wraps
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor
import threading

from .accessibility_client import AccessibilityServiceClient, AccessibilityConfig

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """缓存条目"""
    data: Any
    timestamp: float
    ttl: float
    
    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl

class ConnectionPool:
    """连接池管理器"""
    
    def __init__(self, max_connections: int = 5, timeout: float = 30.0):
        self.max_connections = max_connections
        self.timeout = timeout
        self._connections: List[AccessibilityServiceClient] = []
        self._available_connections: List[AccessibilityServiceClient] = []
        self._lock = threading.Lock()
        self._config: Optional[AccessibilityConfig] = None
        
    def initialize(self, config: AccessibilityConfig):
        """初始化连接池"""
        self._config = config
        with self._lock:
            for _ in range(self.max_connections):
                try:
                    client = AccessibilityServiceClient(config)
                    client.initialize()
                    self._connections.append(client)
                    self._available_connections.append(client)
                except Exception as e:
                    logger.warning(f"创建连接失败: {e}")
                    
    def get_connection(self) -> Optional[AccessibilityServiceClient]:
        """获取可用连接"""
        with self._lock:
            if self._available_connections:
                return self._available_connections.pop()
            elif len(self._connections) < self.max_connections and self._config:
                try:
                    client = AccessibilityServiceClient(self._config)
                    client.initialize()
                    self._connections.append(client)
                    return client
                except Exception as e:
                    logger.error(f"创建新连接失败: {e}")
                    return None
            return None
            
    def return_connection(self, connection: AccessibilityServiceClient):
        """归还连接"""
        with self._lock:
            if connection in self._connections:
                self._available_connections.append(connection)
                
    def close_all(self):
        """关闭所有连接"""
        with self._lock:
            for conn in self._connections:
                try:
                    conn.close()
                except Exception as e:
                    logger.warning(f"关闭连接失败: {e}")
            self._connections.clear()
            self._available_connections.clear()

class EnhancedAccessibilityClient:
    """增强版无障碍服务客户端"""
    
    def __init__(self, config: AccessibilityConfig):
        self.config = config
        self.connection_pool = ConnectionPool(max_connections=5)
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.fallback_enabled = True
        self.performance_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cache_hits': 0,
            'average_response_time': 0.0
        }
        
        # 初始化连接池
        if config.enabled:
            try:
                self.connection_pool.initialize(config)
                logger.info("无障碍服务连接池初始化成功")
            except Exception as e:
                logger.error(f"连接池初始化失败: {e}")
                
    def _cache_key(self, method: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = {
            'method': method,
            'args': str(args),
            'kwargs': str(sorted(kwargs.items()))
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
        
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        with self.cache_lock:
            entry = self.cache.get(key)
            if entry and not entry.is_expired():
                self.performance_metrics['cache_hits'] += 1
                return entry.data
            elif entry:
                # 清理过期缓存
                del self.cache[key]
            return None
            
    def _set_cache(self, key: str, data: Any, ttl: float = 300.0):
        """设置缓存"""
        with self.cache_lock:
            self.cache[key] = CacheEntry(data, time.time(), ttl)
            
    def _cleanup_cache(self):
        """清理过期缓存"""
        with self.cache_lock:
            expired_keys = [k for k, v in self.cache.items() if v.is_expired()]
            for key in expired_keys:
                del self.cache[key]
                
    def _with_performance_tracking(func):
        """性能跟踪装饰器"""
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            start_time = time.time()
            self.performance_metrics['total_requests'] += 1
            
            try:
                result = await func(self, *args, **kwargs)
                self.performance_metrics['successful_requests'] += 1
                return result
            except Exception as e:
                self.performance_metrics['failed_requests'] += 1
                raise e
            finally:
                duration = time.time() - start_time
                # 更新平均响应时间
                total = self.performance_metrics['total_requests']
                current_avg = self.performance_metrics['average_response_time']
                self.performance_metrics['average_response_time'] = (
                    (current_avg * (total - 1) + duration) / total
                )
                
        return wrapper
        
    @_with_performance_tracking
    async def process_voice_input(self, audio_data: bytes, user_id: str = None, 
                                 use_cache: bool = True) -> Dict[str, Any]:
        """处理语音输入（带缓存和错误处理）"""
        try:
            # 生成缓存键（对于语音数据，使用哈希值）
            if use_cache:
                audio_hash = hashlib.md5(audio_data).hexdigest()
                cache_key = self._cache_key('process_voice_input', audio_hash, user_id)
                cached_result = self._get_from_cache(cache_key)
                if cached_result:
                    logger.debug("使用缓存的语音处理结果")
                    return cached_result
                    
            # 获取连接
            connection = self.connection_pool.get_connection()
            if not connection:
                return await self._fallback_voice_processing(audio_data, user_id)
                
            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    connection.process_voice_input,
                    audio_data, user_id
                )
                
                # 缓存结果
                if use_cache and result.get('status') == 'success':
                    self._set_cache(cache_key, result, ttl=600.0)  # 10分钟缓存
                    
                return result
                
            finally:
                self.connection_pool.return_connection(connection)
                
        except Exception as e:
            logger.error(f"语音处理失败: {e}")
            return await self._fallback_voice_processing(audio_data, user_id)
            
    @_with_performance_tracking
    async def process_image_input(self, image_data: bytes, user_id: str = None,
                                 use_cache: bool = True) -> Dict[str, Any]:
        """处理图像输入（带缓存和错误处理）"""
        try:
            # 生成缓存键
            if use_cache:
                image_hash = hashlib.md5(image_data).hexdigest()
                cache_key = self._cache_key('process_image_input', image_hash, user_id)
                cached_result = self._get_from_cache(cache_key)
                if cached_result:
                    logger.debug("使用缓存的图像处理结果")
                    return cached_result
                    
            # 获取连接
            connection = self.connection_pool.get_connection()
            if not connection:
                return await self._fallback_image_processing(image_data, user_id)
                
            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    connection.process_image_input,
                    image_data, user_id
                )
                
                # 缓存结果
                if use_cache and result.get('status') == 'success':
                    self._set_cache(cache_key, result, ttl=1800.0)  # 30分钟缓存
                    
                return result
                
            finally:
                self.connection_pool.return_connection(connection)
                
        except Exception as e:
            logger.error(f"图像处理失败: {e}")
            return await self._fallback_image_processing(image_data, user_id)
            
    @_with_performance_tracking
    async def generate_accessible_content(self, content: str, accessibility_type: str,
                                        user_id: str = None, use_cache: bool = True) -> Dict[str, Any]:
        """生成无障碍内容（带缓存和错误处理）"""
        try:
            # 生成缓存键
            if use_cache:
                cache_key = self._cache_key('generate_accessible_content', 
                                          content, accessibility_type, user_id)
                cached_result = self._get_from_cache(cache_key)
                if cached_result:
                    logger.debug("使用缓存的内容生成结果")
                    return cached_result
                    
            # 获取连接
            connection = self.connection_pool.get_connection()
            if not connection:
                return await self._fallback_content_generation(content, accessibility_type, user_id)
                
            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    connection.generate_accessible_content,
                    content, accessibility_type, user_id
                )
                
                # 缓存结果
                if use_cache and result.get('status') == 'success':
                    self._set_cache(cache_key, result, ttl=3600.0)  # 1小时缓存
                    
                return result
                
            finally:
                self.connection_pool.return_connection(connection)
                
        except Exception as e:
            logger.error(f"内容生成失败: {e}")
            return await self._fallback_content_generation(content, accessibility_type, user_id)
            
    async def _fallback_voice_processing(self, audio_data: bytes, user_id: str = None) -> Dict[str, Any]:
        """语音处理降级方案"""
        if not self.fallback_enabled:
            return {"status": "error", "message": "无障碍服务不可用"}
            
        logger.info("使用语音处理降级方案")
        return {
            "status": "fallback",
            "message": "使用本地语音处理",
            "text": "抱歉，语音识别服务暂时不可用，请尝试文字输入",
            "confidence": 0.5,
            "fallback": True
        }
        
    async def _fallback_image_processing(self, image_data: bytes, user_id: str = None) -> Dict[str, Any]:
        """图像处理降级方案"""
        if not self.fallback_enabled:
            return {"status": "error", "message": "无障碍服务不可用"}
            
        logger.info("使用图像处理降级方案")
        return {
            "status": "fallback",
            "message": "使用本地图像处理",
            "description": "图像识别服务暂时不可用，建议稍后重试",
            "objects": [],
            "text": "",
            "fallback": True
        }
        
    async def _fallback_content_generation(self, content: str, accessibility_type: str, 
                                         user_id: str = None) -> Dict[str, Any]:
        """内容生成降级方案"""
        if not self.fallback_enabled:
            return {"status": "error", "message": "无障碍服务不可用"}
            
        logger.info("使用内容生成降级方案")
        
        # 简单的本地处理
        if accessibility_type == "screen_reader":
            accessible_content = f"屏幕阅读内容：{content}"
        elif accessibility_type == "high_contrast":
            accessible_content = f"高对比度内容：{content}"
        elif accessibility_type == "large_text":
            accessible_content = f"大字体内容：{content}"
        else:
            accessible_content = f"无障碍内容：{content}"
            
        return {
            "status": "fallback",
            "message": "使用本地内容生成",
            "accessible_content": accessible_content,
            "accessibility_type": accessibility_type,
            "fallback": True
        }
        
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            connection = self.connection_pool.get_connection()
            if not connection:
                return {
                    "status": "unhealthy",
                    "message": "无可用连接",
                    "pool_status": {
                        "total_connections": len(self.connection_pool._connections),
                        "available_connections": len(self.connection_pool._available_connections)
                    }
                }
                
            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    connection.health_check
                )
                
                return {
                    "status": "healthy",
                    "service_status": result,
                    "pool_status": {
                        "total_connections": len(self.connection_pool._connections),
                        "available_connections": len(self.connection_pool._available_connections)
                    },
                    "performance_metrics": self.performance_metrics,
                    "cache_size": len(self.cache)
                }
                
            finally:
                self.connection_pool.return_connection(connection)
                
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "performance_metrics": self.performance_metrics
            }
            
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return {
            **self.performance_metrics,
            "cache_size": len(self.cache),
            "pool_status": {
                "total_connections": len(self.connection_pool._connections),
                "available_connections": len(self.connection_pool._available_connections)
            }
        }
        
    def clear_cache(self):
        """清空缓存"""
        with self.cache_lock:
            self.cache.clear()
            logger.info("缓存已清空")
            
    def close(self):
        """关闭客户端"""
        try:
            self.connection_pool.close_all()
            self.executor.shutdown(wait=True)
            self.clear_cache()
            logger.info("增强版无障碍客户端已关闭")
        except Exception as e:
            logger.error(f"关闭客户端失败: {e}") 