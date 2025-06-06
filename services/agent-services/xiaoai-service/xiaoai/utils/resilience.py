"""
resilience - 索克生活项目模块
"""

from collections.abc import Callable
import asyncio
import functools
import random
import threading
import time

"""
弹性工具模块 - 提供断路器、限流器、重试等弹性模式
"""


# 全局状态存储
_circuit_breakers = {}
_circuit_breakers_lock = threading.Lock()
_rate_limiters = {}
_rate_limiters_lock = threading.Lock()


class CircuitBreakerError(Exception):
    """断路器错误"""
    def __init__(self, message: str, circuit_id: str):
        super().__init__(message)
        self.circuit_id = circuit_id


class RateLimiterError(Exception):
    """限流器错误"""
    def __init__(self, message: str, limiter_id: str):
        super().__init__(message)
        self.limiter_id = limiter_id


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_time: float = 60.0,
    timeout: float = 30.0,
    circuit_id: str | None = None,
    fallback: Callable | None = None
):
    """
    断路器装饰器
    
    Args:
        failure_threshold: 失败阈值
        recovery_time: 恢复时间（秒）
        timeout: 超时时间（秒）
        circuit_id: 断路器ID
        fallback: 降级函数
    """
    def decorator(func):
        nonlocal circuit_id
        circuit_id = circuit_id or func.__name__

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            global _circuit_breakers
            current_time = time.time()

            # 初始化断路器
            with _circuit_breakers_lock:
                if circuit_id not in _circuit_breakers:
                    _circuit_breakers[circuit_id] = {
                        "state": "CLOSED",
                        "failure_count": 0,
                        "last_failure_time": 0,
                        "last_success_time": 0,
                        "failure_threshold": failure_threshold,
                        "recovery_time": recovery_time
                    }

                circuit = _circuit_breakers[circuit_id]

            # 检查断路器状态
            if circuit["state"] == "OPEN":
                if current_time - circuit["last_failure_time"] > recovery_time:
                    with _circuit_breakers_lock:
                        circuit["state"] = "HALF_OPEN"
                else:
                    if fallback:
                        return await fallback(*args, **kwargs)
                    raise CircuitBreakerError(f"断路器 {circuit_id} 打开", circuit_id)

            try:
                # 执行函数
                result = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)

                # 成功时重置计数
                with _circuit_breakers_lock:
                    if circuit["state"] == "HALF_OPEN":
                        circuit["state"] = "CLOSED"
                    circuit["failure_count"] = 0
                    circuit["last_success_time"] = current_time

                return result

            except Exception:
                _handle_failure(circuit_id, current_time)
                raise

        return wrapper

    return decorator


def _handle_failure(circuit_id: str, current_time: float):
    """处理断路器失败"""
    with _circuit_breakers_lock:
        circuit = _circuit_breakers[circuit_id]
        circuit["failure_count"] += 1
        circuit["last_failure_time"] = current_time

        if circuit["failure_count"] >= circuit["failure_threshold"]:
            circuit["state"] = "OPEN"


def rate_limiter(
    max_calls: int = 10,
    time_period: int = 1,
    limiter_id: str | None = None
):
    """限流器装饰器"""

    def decorator(func):
        nonlocal limiter_id
        limiter_id = limiter_id or func.__name__

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_time = time.time()

            with _rate_limiters_lock:
                if limiter_id not in _rate_limiters:
                    _rate_limiters[limiter_id] = {
                        "calls": [],
                        "max_calls": max_calls,
                        "time_period": time_period
                    }

                limiter = _rate_limiters[limiter_id]

                # 清理过期调用
                limiter["calls"] = [
                    t for t in limiter["calls"] if current_time - t <= time_period
                ]

                # 检查限制
                if len(limiter["calls"]) >= max_calls:
                    raise RateLimiterError("请求过于频繁", limiter_id)

                # 记录调用
                limiter["calls"].append(current_time)

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def retry(
    max_attempts: int = 3,
    backoff_factor: float = 1.5,
    jitter: bool = True,
    max_backoff: float = 60.0,
    retry_on: set[type[Exception]] | None = None
):
    """重试装饰器"""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # 检查是否需要重试
                    should_retry = True
                    if retry_on is not None:
                        should_retry = any(
                            isinstance(e, exc_type) for exc_type in retry_on
                        )

                    if not should_retry or attempt >= max_attempts - 1:
                        raise

                    # 计算退避时间
                    backoff = min(backoff_factor**attempt, max_backoff)
                    if jitter:
                        backoff *= 0.5 + random.random()

                    await asyncio.sleep(backoff)

            if last_exception:
                raise last_exception
            raise Exception("重试失败")

        return wrapper

    return decorator


def bulkhead(max_concurrent: int = 10, bulkhead_id: str | None = None):
    """舱壁装饰器"""

    def decorator(func):
        nonlocal bulkhead_id
        bulkhead_id = bulkhead_id or func.__name__
        semaphore = asyncio.Semaphore(max_concurrent)

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            async with semaphore:
                return await func(*args, **kwargs)

        return wrapper

    return decorator
