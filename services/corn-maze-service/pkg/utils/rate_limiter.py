#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API限流器 - 防止恶意请求和系统过载
"""

import time
import logging
import asyncio
from typing import Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
from functools import wraps

from pkg.utils.cache import CacheManager
from pkg.utils.metrics import record_cache_operation, errors_total

logger = logging.getLogger(__name__)

class TokenBucket:
    """令牌桶算法实现"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        初始化令牌桶
        
        Args:
            capacity: 桶容量（最大令牌数）
            refill_rate: 令牌补充速率（每秒补充的令牌数）
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """
        消费令牌
        
        Args:
            tokens: 需要消费的令牌数
            
        Returns:
            bool: 是否成功消费令牌
        """
        now = time.time()
        
        # 补充令牌
        time_passed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + time_passed * self.refill_rate
        )
        self.last_refill = now
        
        # 检查是否有足够的令牌
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        
        return False
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """
        获取需要等待的时间
        
        Args:
            tokens: 需要的令牌数
            
        Returns:
            float: 等待时间（秒）
        """
        if self.tokens >= tokens:
            return 0.0
        
        needed_tokens = tokens - self.tokens
        return needed_tokens / self.refill_rate

class SlidingWindowCounter:
    """滑动窗口计数器"""
    
    def __init__(self, window_size: int, max_requests: int):
        """
        初始化滑动窗口计数器
        
        Args:
            window_size: 窗口大小（秒）
            max_requests: 窗口内最大请求数
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests = deque()
    
    def is_allowed(self) -> bool:
        """
        检查是否允许请求
        
        Returns:
            bool: 是否允许
        """
        now = time.time()
        
        # 清理过期的请求记录
        while self.requests and self.requests[0] <= now - self.window_size:
            self.requests.popleft()
        
        # 检查是否超过限制
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        
        return False
    
    def get_reset_time(self) -> float:
        """
        获取重置时间
        
        Returns:
            float: 重置时间戳
        """
        if not self.requests:
            return time.time()
        
        return self.requests[0] + self.window_size

class RateLimiter:
    """综合限流器"""
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """
        初始化限流器
        
        Args:
            cache_manager: 缓存管理器
        """
        self.cache_manager = cache_manager or CacheManager()
        
        # 限流规则配置
        self.rules = {
            # 全局限流
            "global": {
                "requests_per_minute": 1000,
                "requests_per_hour": 10000,
                "burst_capacity": 100
            },
            # 用户限流
            "user": {
                "requests_per_minute": 60,
                "requests_per_hour": 1000,
                "burst_capacity": 10
            },
            # IP限流
            "ip": {
                "requests_per_minute": 100,
                "requests_per_hour": 2000,
                "burst_capacity": 20
            },
            # API端点限流
            "endpoint": {
                "create_maze": {
                    "requests_per_minute": 10,
                    "requests_per_hour": 100
                },
                "search_maze": {
                    "requests_per_minute": 30,
                    "requests_per_hour": 500
                },
                "get_maze": {
                    "requests_per_minute": 100,
                    "requests_per_hour": 2000
                }
            }
        }
        
        # 内存中的限流器实例
        self.token_buckets: Dict[str, TokenBucket] = {}
        self.sliding_windows: Dict[str, SlidingWindowCounter] = {}
        
        # 黑名单和白名单
        self.blacklist = set()
        self.whitelist = set()
        
        logger.info("限流器初始化完成")
    
    async def is_allowed(
        self,
        identifier: str,
        limit_type: str = "user",
        endpoint: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        检查请求是否被允许
        
        Args:
            identifier: 标识符（用户ID、IP等）
            limit_type: 限流类型
            endpoint: API端点
            ip_address: IP地址
            
        Returns:
            Tuple[bool, Dict]: (是否允许, 限流信息)
        """
        try:
            # 检查黑名单
            if identifier in self.blacklist or (ip_address and ip_address in self.blacklist):
                return False, {
                    "reason": "blacklisted",
                    "retry_after": None
                }
            
            # 检查白名单
            if identifier in self.whitelist or (ip_address and ip_address in self.whitelist):
                return True, {"reason": "whitelisted"}
            
            # 获取限流规则
            rules = self.rules.get(limit_type, self.rules["user"])
            
            # 检查端点特定限流
            if endpoint and endpoint in self.rules.get("endpoint", {}):
                endpoint_rules = self.rules["endpoint"][endpoint]
                endpoint_allowed, endpoint_info = await self._check_endpoint_limit(
                    identifier, endpoint, endpoint_rules
                )
                if not endpoint_allowed:
                    return False, endpoint_info
            
            # 检查通用限流
            general_allowed, general_info = await self._check_general_limit(
                identifier, limit_type, rules
            )
            
            if not general_allowed:
                return False, general_info
            
            # 记录成功的请求
            await self._record_request(identifier, limit_type, endpoint)
            
            return True, {"reason": "allowed"}
            
        except Exception as e:
            logger.error(f"限流检查失败: {str(e)}")
            # 出错时允许请求，但记录错误
            errors_total.labels(
                component="rate_limiter",
                error_type="check_failed",
                severity="warning"
            ).inc()
            return True, {"reason": "error_fallback"}
    
    async def _check_endpoint_limit(
        self,
        identifier: str,
        endpoint: str,
        rules: Dict[str, int]
    ) -> Tuple[bool, Dict[str, Any]]:
        """检查端点特定限流"""
        cache_key = f"rate_limit:endpoint:{endpoint}:{identifier}"
        
        # 检查每分钟限制
        if "requests_per_minute" in rules:
            minute_key = f"{cache_key}:minute"
            minute_allowed = await self._check_sliding_window(
                minute_key, 60, rules["requests_per_minute"]
            )
            if not minute_allowed:
                return False, {
                    "reason": "endpoint_minute_limit_exceeded",
                    "endpoint": endpoint,
                    "retry_after": 60
                }
        
        # 检查每小时限制
        if "requests_per_hour" in rules:
            hour_key = f"{cache_key}:hour"
            hour_allowed = await self._check_sliding_window(
                hour_key, 3600, rules["requests_per_hour"]
            )
            if not hour_allowed:
                return False, {
                    "reason": "endpoint_hour_limit_exceeded",
                    "endpoint": endpoint,
                    "retry_after": 3600
                }
        
        return True, {}
    
    async def _check_general_limit(
        self,
        identifier: str,
        limit_type: str,
        rules: Dict[str, int]
    ) -> Tuple[bool, Dict[str, Any]]:
        """检查通用限流"""
        cache_key = f"rate_limit:{limit_type}:{identifier}"
        
        # 检查突发容量（令牌桶）
        if "burst_capacity" in rules:
            bucket_key = f"{cache_key}:burst"
            burst_allowed = await self._check_token_bucket(
                bucket_key,
                rules["burst_capacity"],
                rules.get("requests_per_minute", 60) / 60.0  # 每秒补充速率
            )
            if not burst_allowed:
                return False, {
                    "reason": "burst_limit_exceeded",
                    "retry_after": 1
                }
        
        # 检查每分钟限制
        if "requests_per_minute" in rules:
            minute_key = f"{cache_key}:minute"
            minute_allowed = await self._check_sliding_window(
                minute_key, 60, rules["requests_per_minute"]
            )
            if not minute_allowed:
                return False, {
                    "reason": "minute_limit_exceeded",
                    "retry_after": 60
                }
        
        # 检查每小时限制
        if "requests_per_hour" in rules:
            hour_key = f"{cache_key}:hour"
            hour_allowed = await self._check_sliding_window(
                hour_key, 3600, rules["requests_per_hour"]
            )
            if not hour_allowed:
                return False, {
                    "reason": "hour_limit_exceeded",
                    "retry_after": 3600
                }
        
        return True, {}
    
    async def _check_token_bucket(
        self,
        key: str,
        capacity: int,
        refill_rate: float
    ) -> bool:
        """检查令牌桶限流"""
        # 尝试从缓存获取
        bucket_data = await self.cache_manager.get(key)
        
        if bucket_data:
            bucket = TokenBucket(capacity, refill_rate)
            bucket.tokens = bucket_data.get("tokens", capacity)
            bucket.last_refill = bucket_data.get("last_refill", time.time())
        else:
            bucket = TokenBucket(capacity, refill_rate)
        
        # 检查是否可以消费令牌
        allowed = bucket.consume(1)
        
        # 更新缓存
        await self.cache_manager.set(key, {
            "tokens": bucket.tokens,
            "last_refill": bucket.last_refill
        }, ttl=3600)
        
        return allowed
    
    async def _check_sliding_window(
        self,
        key: str,
        window_size: int,
        max_requests: int
    ) -> bool:
        """检查滑动窗口限流"""
        # 尝试从缓存获取
        window_data = await self.cache_manager.get(key)
        
        if window_data:
            window = SlidingWindowCounter(window_size, max_requests)
            window.requests = deque(window_data.get("requests", []))
        else:
            window = SlidingWindowCounter(window_size, max_requests)
        
        # 检查是否允许
        allowed = window.is_allowed()
        
        # 更新缓存
        await self.cache_manager.set(key, {
            "requests": list(window.requests)
        }, ttl=window_size + 60)  # 稍微长一点的TTL
        
        return allowed
    
    async def _record_request(
        self,
        identifier: str,
        limit_type: str,
        endpoint: Optional[str]
    ):
        """记录请求"""
        try:
            # 记录到缓存中用于统计
            stats_key = f"rate_limit_stats:{limit_type}:{identifier}"
            stats = await self.cache_manager.get(stats_key) or {
                "total_requests": 0,
                "last_request": None,
                "endpoints": {}
            }
            
            stats["total_requests"] += 1
            stats["last_request"] = time.time()
            
            if endpoint:
                stats["endpoints"][endpoint] = stats["endpoints"].get(endpoint, 0) + 1
            
            await self.cache_manager.set(stats_key, stats, ttl=86400)  # 24小时
            
        except Exception as e:
            logger.warning(f"记录请求统计失败: {str(e)}")
    
    async def add_to_blacklist(self, identifier: str, duration: Optional[int] = None):
        """添加到黑名单"""
        self.blacklist.add(identifier)
        
        if duration:
            # 设置临时黑名单
            await self.cache_manager.set(
                f"blacklist:{identifier}",
                {"added_at": time.time()},
                ttl=duration
            )
        
        logger.warning(f"已将 {identifier} 添加到黑名单")
    
    async def remove_from_blacklist(self, identifier: str):
        """从黑名单移除"""
        self.blacklist.discard(identifier)
        await self.cache_manager.delete(f"blacklist:{identifier}")
        logger.info(f"已将 {identifier} 从黑名单移除")
    
    async def add_to_whitelist(self, identifier: str):
        """添加到白名单"""
        self.whitelist.add(identifier)
        logger.info(f"已将 {identifier} 添加到白名单")
    
    async def get_rate_limit_stats(self, identifier: str, limit_type: str) -> Dict[str, Any]:
        """获取限流统计信息"""
        try:
            stats_key = f"rate_limit_stats:{limit_type}:{identifier}"
            stats = await self.cache_manager.get(stats_key)
            
            if not stats:
                return {
                    "total_requests": 0,
                    "last_request": None,
                    "endpoints": {}
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取限流统计失败: {str(e)}")
            return {}
    
    async def reset_limits(self, identifier: str, limit_type: str):
        """重置限流计数"""
        try:
            # 清除相关的缓存键
            patterns = [
                f"rate_limit:{limit_type}:{identifier}:*",
                f"rate_limit:endpoint:*:{identifier}:*"
            ]
            
            for pattern in patterns:
                await self.cache_manager.delete_pattern(pattern)
            
            logger.info(f"已重置 {identifier} 的限流计数")
            
        except Exception as e:
            logger.error(f"重置限流计数失败: {str(e)}")

# 装饰器函数
def rate_limit(
    limit_type: str = "user",
    endpoint: Optional[str] = None,
    identifier_func: Optional[callable] = None
):
    """
    限流装饰器
    
    Args:
        limit_type: 限流类型
        endpoint: API端点名称
        identifier_func: 获取标识符的函数
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取限流器实例
            rate_limiter = RateLimiter()
            
            # 获取标识符
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            else:
                # 默认从参数中获取user_id
                identifier = kwargs.get("user_id") or (args[1] if len(args) > 1 else "anonymous")
            
            # 获取IP地址（如果可用）
            ip_address = kwargs.get("ip_address")
            
            # 检查限流
            allowed, info = await rate_limiter.is_allowed(
                identifier=identifier,
                limit_type=limit_type,
                endpoint=endpoint or func.__name__,
                ip_address=ip_address
            )
            
            if not allowed:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=429,
                    detail={
                        "message": "Rate limit exceeded",
                        "info": info
                    }
                )
            
            # 执行原函数
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# 全局限流器实例
_rate_limiter: Optional[RateLimiter] = None

def get_rate_limiter() -> RateLimiter:
    """获取全局限流器实例"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter 