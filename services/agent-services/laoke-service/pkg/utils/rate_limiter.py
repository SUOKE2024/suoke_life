#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
速率限制器
提供灵活的速率限制功能，支持多种算法
"""

import time
import asyncio
import logging
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum
import hashlib
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class RateLimitAlgorithm(Enum):
    """速率限制算法"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"

@dataclass
class RateLimitRule:
    """速率限制规则"""
    requests: int  # 允许的请求数
    window: int    # 时间窗口（秒）
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.SLIDING_WINDOW
    burst: Optional[int] = None  # 突发请求数（仅用于令牌桶）

@dataclass
class RateLimitResult:
    """速率限制结果"""
    allowed: bool
    remaining: int
    reset_time: float
    retry_after: Optional[int] = None

class TokenBucket:
    """令牌桶算法实现"""
    
    def __init__(self, capacity: int, refill_rate: float, burst: Optional[int] = None):
        self.capacity = capacity
        self.refill_rate = refill_rate  # 每秒添加的令牌数
        self.burst = burst or capacity
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """消费令牌"""
        async with self._lock:
            now = time.time()
            
            # 添加令牌
            time_passed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + time_passed * self.refill_rate)
            self.last_refill = now
            
            # 检查是否有足够的令牌
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def get_remaining(self) -> int:
        """获取剩余令牌数"""
        now = time.time()
        time_passed = now - self.last_refill
        current_tokens = min(self.capacity, self.tokens + time_passed * self.refill_rate)
        return int(current_tokens)

class SlidingWindow:
    """滑动窗口算法实现"""
    
    def __init__(self, limit: int, window: int):
        self.limit = limit
        self.window = window
        self.requests: deque = deque()
        self._lock = asyncio.Lock()
    
    async def is_allowed(self) -> bool:
        """检查是否允许请求"""
        async with self._lock:
            now = time.time()
            
            # 移除过期的请求
            while self.requests and self.requests[0] <= now - self.window:
                self.requests.popleft()
            
            # 检查是否超过限制
            if len(self.requests) < self.limit:
                self.requests.append(now)
                return True
            
            return False
    
    def get_remaining(self) -> int:
        """获取剩余请求数"""
        now = time.time()
        # 计算当前窗口内的请求数
        valid_requests = sum(1 for req_time in self.requests if req_time > now - self.window)
        return max(0, self.limit - valid_requests)
    
    def get_reset_time(self) -> float:
        """获取重置时间"""
        if not self.requests:
            return time.time()
        return self.requests[0] + self.window

class FixedWindow:
    """固定窗口算法实现"""
    
    def __init__(self, limit: int, window: int):
        self.limit = limit
        self.window = window
        self.count = 0
        self.window_start = time.time()
        self._lock = asyncio.Lock()
    
    async def is_allowed(self) -> bool:
        """检查是否允许请求"""
        async with self._lock:
            now = time.time()
            
            # 检查是否需要重置窗口
            if now - self.window_start >= self.window:
                self.count = 0
                self.window_start = now
            
            # 检查是否超过限制
            if self.count < self.limit:
                self.count += 1
                return True
            
            return False
    
    def get_remaining(self) -> int:
        """获取剩余请求数"""
        now = time.time()
        if now - self.window_start >= self.window:
            return self.limit
        return max(0, self.limit - self.count)
    
    def get_reset_time(self) -> float:
        """获取重置时间"""
        return self.window_start + self.window

class RateLimiter:
    """速率限制器"""
    
    def __init__(self, config=None):
        self.config = config
        self._limiters: Dict[str, Any] = {}
        self._rules: Dict[str, RateLimitRule] = {}
        self._global_rules: List[RateLimitRule] = []
        
        # 加载配置
        self._load_config()
        
        # 清理任务
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_cleanup_task()
    
    def _load_config(self) -> None:
        """加载配置"""
        if not self.config:
            # 默认配置
            self._global_rules = [
                RateLimitRule(requests=100, window=60),  # 每分钟100请求
                RateLimitRule(requests=1000, window=3600),  # 每小时1000请求
            ]
            return
        
        # 从配置加载规则
        rate_limit_config = self.config.get_section('rate_limit')
        
        # 全局规则
        global_rules = rate_limit_config.get('global_rules', [])
        for rule_config in global_rules:
            rule = RateLimitRule(
                requests=rule_config['requests'],
                window=rule_config['window'],
                algorithm=RateLimitAlgorithm(rule_config.get('algorithm', 'sliding_window')),
                burst=rule_config.get('burst')
            )
            self._global_rules.append(rule)
        
        # 用户特定规则
        user_rules = rate_limit_config.get('user_rules', {})
        for user_pattern, rule_config in user_rules.items():
            rule = RateLimitRule(
                requests=rule_config['requests'],
                window=rule_config['window'],
                algorithm=RateLimitAlgorithm(rule_config.get('algorithm', 'sliding_window')),
                burst=rule_config.get('burst')
            )
            self._rules[user_pattern] = rule
    
    def _start_cleanup_task(self) -> None:
        """启动清理任务"""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self) -> None:
        """清理过期的限制器"""
        while True:
            try:
                await asyncio.sleep(300)  # 每5分钟清理一次
                await self._cleanup_expired_limiters()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"清理任务异常: {str(e)}")
    
    async def _cleanup_expired_limiters(self) -> None:
        """清理过期的限制器"""
        now = time.time()
        expired_keys = []
        
        for key, limiter in self._limiters.items():
            # 检查限制器是否长时间未使用
            if hasattr(limiter, 'last_access') and now - limiter.last_access > 3600:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._limiters[key]
        
        if expired_keys:
            logger.debug(f"清理了 {len(expired_keys)} 个过期的速率限制器")
    
    def _get_limiter_key(self, identifier: str, rule: RateLimitRule) -> str:
        """生成限制器键"""
        rule_hash = hashlib.md5(f"{rule.requests}:{rule.window}:{rule.algorithm.value}".encode()).hexdigest()[:8]
        return f"{identifier}:{rule_hash}"
    
    def _create_limiter(self, rule: RateLimitRule) -> Any:
        """创建限制器实例"""
        if rule.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            refill_rate = rule.requests / rule.window
            return TokenBucket(rule.requests, refill_rate, rule.burst)
        elif rule.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            return SlidingWindow(rule.requests, rule.window)
        elif rule.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
            return FixedWindow(rule.requests, rule.window)
        else:
            raise ValueError(f"不支持的算法: {rule.algorithm}")
    
    def _get_rules_for_identifier(self, identifier: str) -> List[RateLimitRule]:
        """获取标识符对应的规则"""
        rules = []
        
        # 添加全局规则
        rules.extend(self._global_rules)
        
        # 添加匹配的用户规则
        for pattern, rule in self._rules.items():
            if pattern in identifier or identifier.startswith(pattern):
                rules.append(rule)
        
        return rules
    
    async def check_rate_limit(self, identifier: str) -> bool:
        """检查速率限制"""
        rules = self._get_rules_for_identifier(identifier)
        
        for rule in rules:
            limiter_key = self._get_limiter_key(identifier, rule)
            
            # 获取或创建限制器
            if limiter_key not in self._limiters:
                self._limiters[limiter_key] = self._create_limiter(rule)
            
            limiter = self._limiters[limiter_key]
            
            # 更新最后访问时间
            limiter.last_access = time.time()
            
            # 检查限制
            if rule.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
                if not await limiter.consume():
                    logger.debug(f"速率限制触发: {identifier}, 规则: {rule}")
                    return False
            else:
                if not await limiter.is_allowed():
                    logger.debug(f"速率限制触发: {identifier}, 规则: {rule}")
                    return False
        
        return True
    
    async def get_rate_limit_status(self, identifier: str) -> Dict[str, RateLimitResult]:
        """获取速率限制状态"""
        rules = self._get_rules_for_identifier(identifier)
        results = {}
        
        for i, rule in enumerate(rules):
            limiter_key = self._get_limiter_key(identifier, rule)
            
            if limiter_key not in self._limiters:
                # 如果限制器不存在，说明还没有请求
                results[f"rule_{i}"] = RateLimitResult(
                    allowed=True,
                    remaining=rule.requests,
                    reset_time=time.time() + rule.window
                )
                continue
            
            limiter = self._limiters[limiter_key]
            
            # 获取状态
            remaining = limiter.get_remaining()
            reset_time = getattr(limiter, 'get_reset_time', lambda: time.time() + rule.window)()
            
            # 模拟检查是否允许（不实际消费）
            if rule.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
                allowed = remaining >= 1
            else:
                # 对于窗口算法，需要实际检查
                test_limiter = self._create_limiter(rule)
                allowed = await test_limiter.is_allowed()
            
            retry_after = None
            if not allowed:
                retry_after = int(reset_time - time.time())
            
            results[f"rule_{i}"] = RateLimitResult(
                allowed=allowed,
                remaining=remaining,
                reset_time=reset_time,
                retry_after=retry_after
            )
        
        return results
    
    async def reset_rate_limit(self, identifier: str) -> bool:
        """重置速率限制"""
        rules = self._get_rules_for_identifier(identifier)
        reset_count = 0
        
        for rule in rules:
            limiter_key = self._get_limiter_key(identifier, rule)
            if limiter_key in self._limiters:
                del self._limiters[limiter_key]
                reset_count += 1
        
        logger.info(f"重置了 {reset_count} 个速率限制器: {identifier}")
        return reset_count > 0
    
    def add_rule(self, pattern: str, rule: RateLimitRule) -> None:
        """添加规则"""
        self._rules[pattern] = rule
        logger.info(f"添加速率限制规则: {pattern} -> {rule}")
    
    def remove_rule(self, pattern: str) -> bool:
        """移除规则"""
        if pattern in self._rules:
            del self._rules[pattern]
            logger.info(f"移除速率限制规则: {pattern}")
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'active_limiters': len(self._limiters),
            'global_rules': len(self._global_rules),
            'user_rules': len(self._rules),
            'total_rules': len(self._global_rules) + len(self._rules)
        }
    
    async def close(self) -> None:
        """关闭速率限制器"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        self._limiters.clear()
        logger.info("速率限制器已关闭")

# 全局速率限制器实例
_rate_limiter: Optional[RateLimiter] = None

def get_rate_limiter(config=None) -> RateLimiter:
    """获取全局速率限制器实例"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(config)
    return _rate_limiter

def rate_limit(identifier_func=None, requests: int = 100, window: int = 60):
    """速率限制装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成标识符
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            else:
                # 默认使用函数名作为标识符
                identifier = func.__name__
            
            # 检查速率限制
            rate_limiter = get_rate_limiter()
            if not await rate_limiter.check_rate_limit(identifier):
                raise Exception(f"速率限制: {identifier}")
            
            # 执行函数
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        
        return wrapper
    return decorator 