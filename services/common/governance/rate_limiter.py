#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
限流器实现
提供令牌桶、滑动窗口等限流算法
"""

import asyncio
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from collections import deque

logger = logging.getLogger(__name__)

class RateLimitExceededError(Exception):
    """限流异常"""
    pass

@dataclass
class RateLimitConfig:
    """限流配置"""
    rate: float = 100.0        # 每秒允许的请求数
    burst: int = 10            # 突发请求数
    window_size: int = 60      # 时间窗口大小（秒）

class RateLimiter(ABC):
    """限流器抽象基类"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.stats = {
            'total_requests': 0,
            'allowed_requests': 0,
            'rejected_requests': 0,
            'last_reset_time': time.time()
        }
    
    @abstractmethod
    async def acquire(self, tokens: int = 1) -> bool:
        """
        获取令牌
        
        Args:
            tokens: 需要的令牌数
            
        Returns:
            bool: 是否成功获取令牌
        """
        pass
    
    @abstractmethod
    async def try_acquire(self, tokens: int = 1) -> bool:
        """
        尝试获取令牌（非阻塞）
        
        Args:
            tokens: 需要的令牌数
            
        Returns:
            bool: 是否成功获取令牌
        """
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            'rejection_rate': (
                self.stats['rejected_requests'] / self.stats['total_requests']
                if self.stats['total_requests'] > 0 else 0
            ),
            'config': {
                'rate': self.config.rate,
                'burst': self.config.burst,
                'window_size': self.config.window_size
            }
        }
    
    async def reset(self):
        """重置限流器"""
        self.stats = {
            'total_requests': 0,
            'allowed_requests': 0,
            'rejected_requests': 0,
            'last_reset_time': time.time()
        }

class TokenBucketRateLimiter(RateLimiter):
    """令牌桶限流器"""
    
    def __init__(self, config: RateLimitConfig):
        super().__init__(config)
        self.tokens = float(config.burst)  # 当前令牌数
        self.last_refill_time = time.time()
        self._lock = asyncio.Lock()
        
        logger.info(f"令牌桶限流器初始化，速率: {config.rate}/s, 桶容量: {config.burst}")
    
    async def _refill_tokens(self):
        """补充令牌"""
        current_time = time.time()
        time_passed = current_time - self.last_refill_time
        
        # 计算应该添加的令牌数
        tokens_to_add = time_passed * self.config.rate
        self.tokens = min(self.config.burst, self.tokens + tokens_to_add)
        self.last_refill_time = current_time
    
    async def acquire(self, tokens: int = 1) -> bool:
        """获取令牌（阻塞直到获取成功）"""
        while True:
            if await self.try_acquire(tokens):
                return True
            
            # 计算需要等待的时间
            async with self._lock:
                await self._refill_tokens()
                if self.tokens >= tokens:
                    continue
                
                # 计算等待时间
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.config.rate
                
            await asyncio.sleep(min(wait_time, 1.0))  # 最多等待1秒
    
    async def try_acquire(self, tokens: int = 1) -> bool:
        """尝试获取令牌（非阻塞）"""
        async with self._lock:
            self.stats['total_requests'] += 1
            await self._refill_tokens()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                self.stats['allowed_requests'] += 1
                return True
            else:
                self.stats['rejected_requests'] += 1
                return False

class SlidingWindowRateLimiter(RateLimiter):
    """滑动窗口限流器"""
    
    def __init__(self, config: RateLimitConfig):
        super().__init__(config)
        self.requests = deque()  # 存储请求时间戳
        self._lock = asyncio.Lock()
        
        logger.info(f"滑动窗口限流器初始化，窗口: {config.window_size}s, 限制: {config.rate * config.window_size}")
    
    async def _clean_old_requests(self):
        """清理过期的请求记录"""
        current_time = time.time()
        cutoff_time = current_time - self.config.window_size
        
        while self.requests and self.requests[0] < cutoff_time:
            self.requests.popleft()
    
    async def acquire(self, tokens: int = 1) -> bool:
        """获取令牌（阻塞直到获取成功）"""
        while True:
            if await self.try_acquire(tokens):
                return True
            
            # 等待一段时间后重试
            await asyncio.sleep(0.1)
    
    async def try_acquire(self, tokens: int = 1) -> bool:
        """尝试获取令牌（非阻塞）"""
        async with self._lock:
            self.stats['total_requests'] += 1
            await self._clean_old_requests()
            
            # 检查当前窗口内的请求数
            max_requests = int(self.config.rate * self.config.window_size)
            current_requests = len(self.requests)
            
            if current_requests + tokens <= max_requests:
                # 记录请求时间
                current_time = time.time()
                for _ in range(tokens):
                    self.requests.append(current_time)
                
                self.stats['allowed_requests'] += 1
                return True
            else:
                self.stats['rejected_requests'] += 1
                return False

class FixedWindowRateLimiter(RateLimiter):
    """固定窗口限流器"""
    
    def __init__(self, config: RateLimitConfig):
        super().__init__(config)
        self.current_window_start = int(time.time() // config.window_size) * config.window_size
        self.current_window_count = 0
        self._lock = asyncio.Lock()
        
        logger.info(f"固定窗口限流器初始化，窗口: {config.window_size}s")
    
    async def _check_window(self):
        """检查并重置窗口"""
        current_time = time.time()
        window_start = int(current_time // self.config.window_size) * self.config.window_size
        
        if window_start > self.current_window_start:
            self.current_window_start = window_start
            self.current_window_count = 0
    
    async def acquire(self, tokens: int = 1) -> bool:
        """获取令牌（阻塞直到获取成功）"""
        while True:
            if await self.try_acquire(tokens):
                return True
            
            # 等待到下一个窗口
            current_time = time.time()
            next_window = (int(current_time // self.config.window_size) + 1) * self.config.window_size
            wait_time = next_window - current_time
            
            await asyncio.sleep(min(wait_time, 1.0))
    
    async def try_acquire(self, tokens: int = 1) -> bool:
        """尝试获取令牌（非阻塞）"""
        async with self._lock:
            self.stats['total_requests'] += 1
            await self._check_window()
            
            max_requests = int(self.config.rate * self.config.window_size)
            
            if self.current_window_count + tokens <= max_requests:
                self.current_window_count += tokens
                self.stats['allowed_requests'] += 1
                return True
            else:
                self.stats['rejected_requests'] += 1
                return False

class AdaptiveRateLimiter(RateLimiter):
    """自适应限流器"""
    
    def __init__(self, config: RateLimitConfig):
        super().__init__(config)
        self.base_limiter = TokenBucketRateLimiter(config)
        self.success_rate_window = deque(maxlen=100)  # 最近100个请求的成功率
        self.adjustment_factor = 1.0  # 调整因子
        self._lock = asyncio.Lock()
        
        logger.info("自适应限流器初始化")
    
    async def _adjust_rate(self, success: bool):
        """根据成功率调整限流速率"""
        self.success_rate_window.append(success)
        
        if len(self.success_rate_window) >= 10:  # 至少有10个样本
            success_rate = sum(self.success_rate_window) / len(self.success_rate_window)
            
            if success_rate > 0.95:  # 成功率高，可以放宽限制
                self.adjustment_factor = min(2.0, self.adjustment_factor * 1.1)
            elif success_rate < 0.8:  # 成功率低，收紧限制
                self.adjustment_factor = max(0.5, self.adjustment_factor * 0.9)
            
            # 更新基础限流器的配置
            adjusted_config = RateLimitConfig(
                rate=self.config.rate * self.adjustment_factor,
                burst=self.config.burst,
                window_size=self.config.window_size
            )
            self.base_limiter.config = adjusted_config
    
    async def acquire(self, tokens: int = 1) -> bool:
        """获取令牌"""
        result = await self.base_limiter.acquire(tokens)
        await self._adjust_rate(result)
        return result
    
    async def try_acquire(self, tokens: int = 1) -> bool:
        """尝试获取令牌"""
        result = await self.base_limiter.try_acquire(tokens)
        await self._adjust_rate(result)
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        base_stats = self.base_limiter.get_stats()
        base_stats['adjustment_factor'] = self.adjustment_factor
        base_stats['current_success_rate'] = (
            sum(self.success_rate_window) / len(self.success_rate_window)
            if self.success_rate_window else 0
        )
        return base_stats

class RateLimiterRegistry:
    """限流器注册表"""
    
    def __init__(self):
        self._limiters: Dict[str, RateLimiter] = {}
        self._lock = asyncio.Lock()
    
    async def get_limiter(
        self, 
        name: str, 
        limiter_type: str = "token_bucket",
        config: Optional[RateLimitConfig] = None
    ) -> RateLimiter:
        """
        获取或创建限流器
        
        Args:
            name: 限流器名称
            limiter_type: 限流器类型 (token_bucket, sliding_window, fixed_window, adaptive)
            config: 限流器配置
            
        Returns:
            RateLimiter: 限流器实例
        """
        async with self._lock:
            if name not in self._limiters:
                if config is None:
                    config = RateLimitConfig()
                
                if limiter_type == "token_bucket":
                    self._limiters[name] = TokenBucketRateLimiter(config)
                elif limiter_type == "sliding_window":
                    self._limiters[name] = SlidingWindowRateLimiter(config)
                elif limiter_type == "fixed_window":
                    self._limiters[name] = FixedWindowRateLimiter(config)
                elif limiter_type == "adaptive":
                    self._limiters[name] = AdaptiveRateLimiter(config)
                else:
                    raise ValueError(f"不支持的限流器类型: {limiter_type}")
                
                logger.info(f"创建新的限流器: {name} ({limiter_type})")
            
            return self._limiters[name]
    
    async def remove_limiter(self, name: str):
        """移除限流器"""
        async with self._lock:
            if name in self._limiters:
                del self._limiters[name]
                logger.info(f"移除限流器: {name}")
    
    def list_limiters(self) -> Dict[str, Dict[str, Any]]:
        """列出所有限流器及其状态"""
        return {
            name: limiter.get_stats()
            for name, limiter in self._limiters.items()
        }
    
    async def reset_all(self):
        """重置所有限流器"""
        async with self._lock:
            for limiter in self._limiters.values():
                await limiter.reset()
            logger.info("所有限流器已重置")

# 全局限流器注册表
_global_limiter_registry = RateLimiterRegistry()

async def get_rate_limiter(
    name: str,
    limiter_type: str = "token_bucket", 
    config: Optional[RateLimitConfig] = None
) -> RateLimiter:
    """获取全局限流器实例"""
    return await _global_limiter_registry.get_limiter(name, limiter_type, config)

# 装饰器支持
def rate_limit(
    name: str,
    limiter_type: str = "token_bucket",
    config: Optional[RateLimitConfig] = None,
    tokens: int = 1
):
    """
    限流装饰器
    
    Args:
        name: 限流器名称
        limiter_type: 限流器类型
        config: 限流器配置
        tokens: 需要的令牌数
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            limiter = await get_rate_limiter(name, limiter_type, config)
            
            if not await limiter.try_acquire(tokens):
                raise RateLimitExceededError(f"限流器 {name} 拒绝请求")
            
            return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
        
        return wrapper
    return decorator 