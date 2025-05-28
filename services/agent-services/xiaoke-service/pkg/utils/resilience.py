#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
弹性工具
提供断路器、限流器、重试策略等弹性机制
"""

import time
import logging
import functools
import asyncio
from typing import Callable, Any, Dict, List, Optional
import threading

from .config_loader import get_config

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """断路器，防止系统级联失败"""

    # 断路器状态
    CLOSED = "closed"  # 正常关闭状态
    OPEN = "open"  # 开路状态，快速失败
    HALF_OPEN = "half_open"  # 半开状态，尝试恢复

    def __init__(self, name: str, failure_threshold: int = 5, recovery_time: int = 30):
        """
        初始化断路器

        Args:
            name: 断路器名称
            failure_threshold: 触发断路的失败阈值
            recovery_time: 恢复尝试时间（秒）
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time

        # 状态
        self.state = self.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.lock = threading.RLock()

    def _record_failure(self):
        """记录失败"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            # 检查是否达到开路阈值
            if (
                self.state == self.CLOSED
                and self.failure_count >= self.failure_threshold
            ):
                logger.warning(
                    f"断路器 {self.name} 开路: 失败次数达到阈值 {self.failure_threshold}"
                )
                self.state = self.OPEN

    def _record_success(self):
        """记录成功"""
        with self.lock:
            # 如果是半开状态，成功则恢复到关闭状态
            if self.state == self.HALF_OPEN:
                logger.info(f"断路器 {self.name} 关闭: 恢复正常")
                self.state = self.CLOSED
                self.failure_count = 0

    def _check_state(self):
        """检查并更新断路器状态"""
        with self.lock:
            # 如果是开路状态且已超过恢复时间，尝试半开
            if self.state == self.OPEN:
                elapsed = time.time() - self.last_failure_time
                if elapsed >= self.recovery_time:
                    logger.info(f"断路器 {self.name} 半开: 尝试恢复")
                    self.state = self.HALF_OPEN

    def allow_request(self) -> bool:
        """
        检查是否允许请求通过

        Returns:
            bool: 是否允许请求
        """
        self._check_state()

        with self.lock:
            # 开路状态直接拒绝请求
            if self.state == self.OPEN:
                return False

            # 半开状态只允许一个请求通过
            if self.state == self.HALF_OPEN:
                # 允许通过后立即切换回开路状态，防止并发请求都通过
                self.state = self.OPEN
                return True

            # 关闭状态允许请求
            return True

    def on_success(self):
        """调用成功时的回调"""
        self._record_success()

    def on_failure(self):
        """调用失败时的回调"""
        self._record_failure()

    def reset(self):
        """重置断路器状态"""
        with self.lock:
            self.state = self.CLOSED
            self.failure_count = 0
            logger.info(f"断路器 {self.name} 已重置")


# 断路器注册表 name -> CircuitBreaker
_circuit_breakers = {}
_circuit_breakers_lock = threading.RLock()


def get_circuit_breaker(
    name: str, failure_threshold: int = 5, recovery_time: int = 30
) -> CircuitBreaker:
    """
    获取或创建断路器

    Args:
        name: 断路器名称
        failure_threshold: 触发断路的失败阈值
        recovery_time: 恢复尝试时间（秒）

    Returns:
        CircuitBreaker: 断路器实例
    """
    with _circuit_breakers_lock:
        if name not in _circuit_breakers:
            _circuit_breakers[name] = CircuitBreaker(
                name, failure_threshold, recovery_time
            )
        return _circuit_breakers[name]


def circuit_breaker(failure_threshold: int = 5, recovery_time: int = 30):
    """
    断路器装饰器

    Args:
        failure_threshold: 触发断路的失败阈值
        recovery_time: 恢复尝试时间（秒）
    """

    def decorator(func):
        # 使用函数名作为断路器名称
        breaker_name = f"cb_{func.__name__}"

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            breaker = get_circuit_breaker(
                breaker_name, failure_threshold, recovery_time
            )

            # 检查是否允许请求
            if not breaker.allow_request():
                logger.warning(f"断路器 {breaker_name} 拒绝请求")
                raise RuntimeError(f"Circuit breaker is open: {breaker_name}")

            try:
                # 调用原始函数
                result = await func(*args, **kwargs)

                # 记录成功
                breaker.on_success()
                return result

            except Exception as e:
                # 记录失败
                breaker.on_failure()
                raise

        return wrapper

    return decorator


class RateLimiter:
    """速率限制器，限制请求频率"""

    def __init__(self, name: str, max_calls: int, time_period: int):
        """
        初始化速率限制器

        Args:
            name: 限制器名称
            max_calls: 时间周期内允许的最大调用次数
            time_period: 时间周期（秒）
        """
        self.name = name
        self.max_calls = max_calls
        self.time_period = time_period

        # 调用记录 (时间戳, 计数)
        self.calls = []
        self.lock = threading.RLock()

    def _cleanup_old_calls(self):
        """清理过期的调用记录"""
        now = time.time()
        with self.lock:
            self.calls = [
                call for call in self.calls if now - call[0] < self.time_period
            ]

    def allow_call(self) -> bool:
        """
        检查是否允许当前调用

        Returns:
            bool: 是否允许调用
        """
        self._cleanup_old_calls()

        with self.lock:
            # 计算当前窗口内的调用次数
            current_calls = sum(call[1] for call in self.calls)

            # 检查是否达到限制
            if current_calls >= self.max_calls:
                logger.warning(
                    f"速率限制器 {self.name} 限制请求: {current_calls}/{self.max_calls} in {self.time_period}s"
                )
                return False

            # 记录调用
            now = time.time()
            self.calls.append((now, 1))
            return True

    def reset(self):
        """重置限制器"""
        with self.lock:
            self.calls = []
            logger.info(f"速率限制器 {self.name} 已重置")


# 速率限制器注册表 name -> RateLimiter
_rate_limiters = {}
_rate_limiters_lock = threading.RLock()


def get_rate_limiter(
    name: str, max_calls: int = 100, time_period: int = 60
) -> RateLimiter:
    """
    获取或创建速率限制器

    Args:
        name: 限制器名称
        max_calls: 时间周期内允许的最大调用次数
        time_period: 时间周期（秒）

    Returns:
        RateLimiter: 速率限制器实例
    """
    with _rate_limiters_lock:
        if name not in _rate_limiters:
            _rate_limiters[name] = RateLimiter(name, max_calls, time_period)
        return _rate_limiters[name]


def rate_limiter(max_calls: int = 100, time_period: int = 60):
    """
    速率限制器装饰器

    Args:
        max_calls: 时间周期内允许的最大调用次数
        time_period: 时间周期（秒）
    """

    def decorator(func):
        # 使用函数名作为限制器名称
        limiter_name = f"rl_{func.__name__}"

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            limiter = get_rate_limiter(limiter_name, max_calls, time_period)

            # 检查是否允许调用
            if not limiter.allow_call():
                logger.warning(f"速率限制器 {limiter_name} 拒绝请求")

                # 在拒绝请求时等待一小段时间再次尝试
                retry_wait = 1.0  # 1秒
                logger.info(f"等待 {retry_wait}s 后重试")
                await asyncio.sleep(retry_wait)

                # 再次检查
                if not limiter.allow_call():
                    raise RuntimeError(f"Rate limit exceeded: {limiter_name}")

            # 调用原始函数
            return await func(*args, **kwargs)

        return wrapper

    return decorator
