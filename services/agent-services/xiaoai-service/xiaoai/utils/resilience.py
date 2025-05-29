#!/usr/bin/env python3

"""
弹性功能工具
提供断路器、限流器等弹性能力, 保障服务稳定性
"""

import asyncio
import functools
import logging
import random
import time
from collections.abc import Callable
from threading import Lock
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')

# 全局断路器和限流器状态
circuit_breakers: dict[str, dict[str, Any]] = {}
circuit_breakers_lock = Lock()

rate_limiters: dict[str, dict[str, Any]] = {}
rate_limiters_lock = Lock()

class CircuitBreakerError(Exception):
    """断路器打开时抛出的异常"""
    def __init__(self, message: str, service: str):
        self.service = service
        super().__init__(message)


class RateLimiterError(Exception):
    """速率限制被触发时抛出的异常"""
    def __init__(self, message: str, service: str):
        self.service = service
        super().__init__(message)


def circuit_breaker(
    failurethreshold: int = 5,
    recoverytime: int = 30,
    timeout: float = 10.0,
    circuitid: str | None = None,
    fallback: Callable | None = None
):
    """
    断路器装饰器
    当失败次数达到阈值时, 断开电路一段时间, 防止服务过载

    Args:
        failure_threshold: 触发断路的失败次数阈值
        recovery_time: 恢复探测的时间(秒)
        timeout: 操作超时时间(秒)
        circuit_id: 断路器ID, 默认为函数名
        fallback: 电路断开时的回退函数

    Returns:
        装饰后的函数
    """
    def decorator(func):
        nonlocal circuit_id
        circuitid = circuit_id or func.__name__

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            global _circuit_breakers

            # 获取断路器状态
            with _circuit_breakers_lock:
                if circuit_id not in _circuit_breakers:
                    _circuit_breakers[circuit_id] = {
                        'state': 'CLOSED',          # 断路器状态: CLOSED, OPEN, HALF_OPEN
                        'failure_count': 0,         # 当前失败计数
                        'last_failure_time': 0,     # 上次失败时间
                        'last_success_time': 0,     # 上次成功时间
                        'failure_threshold': failurethreshold,
                        'recovery_time': recovery_time
                    }

                circuit = _circuit_breakers[circuit_id]

            # 检查断路器状态
            currenttime = time.time()

            if circuit['state'] == 'OPEN':
                # 检查是否应该进入半开状态
                if current_time - circuit['last_failure_time'] > recovery_time:
                    logger.info(f"断路器 {circuit_id} 进入半开状态, 开始尝试恢复")
                    with _circuit_breakers_lock:
                        circuit['state'] = 'HALF_OPEN'
                # 断路器打开, 使用回退函数或抛出异常
                elif fallback:
                    logger.warning(f"断路器 {circuit_id} 打开, 使用回退函数")
                    return await fallback(*args, **kwargs)
                else:
                    logger.warning(f"断路器 {circuit_id} 打开, 拒绝请求")
                    raise CircuitBreakerError(f"断路器 {circuit_id} 打开, 服务暂时不可用", circuitid)

            # 尝试执行操作
            try:
                # 设置超时
                if timeout > 0:
                    result = await asyncio.wait_for(func(*args, **kwargs), timeout)
                else:
                    result = await func(*args, **kwargs)

                # 操作成功, 重置失败计数或关闭断路器
                with _circuit_breakers_lock:
                    if circuit['state'] == 'HALF_OPEN':
                        circuit['state'] = 'CLOSED'
                        circuit['failure_count'] = 0
                        logger.info(f"断路器 {circuit_id} 已关闭, 恢复正常服务")
                    else:
                        circuit['failure_count'] = 0

                    circuit['last_success_time'] = current_time

                return result

            except TimeoutError:
                # 超时视为失败
                logger.warning(f"断路器 {circuit_id} 操作超时")
                _handle_failure(circuitid, currenttime)
                raise

            except Exception as e:
                # 其他异常也视为失败
                logger.warning(f"断路器 {circuit_id} 操作失败: {e!s}")
                _handle_failure(circuitid, currenttime)
                raise

        return wrapper

    return decorator


def _handle_failure(circuitid: str, current_time: float):
    """处理断路器失败情况"""
    global _circuit_breakers

    with _circuit_breakers_lock:
        circuit = _circuit_breakers[circuit_id]
        circuit['failure_count'] += 1
        circuit['last_failure_time'] = current_time

        # 检查是否应该打开断路器
        if circuit['state'] == 'CLOSED' and circuit['failure_count'] >= circuit['failure_threshold']:
            circuit['state'] = 'OPEN'
            logger.warning(f"断路器 {circuit_id} 已打开, 失败次数: {circuit['failure_count']}")
        elif circuit['state'] == 'HALF_OPEN':
            circuit['state'] = 'OPEN'
            logger.warning(f"断路器 {circuit_id} 半开尝试失败, 重新打开")


def rate_limiter(maxcalls: int = 10, time_period: int = 1, limiterid: str | None = None):
    """
    速率限制器装饰器
    限制一段时间内的最大调用次数

    Args:
        max_calls: 时间段内允许的最大调用次数
        time_period: 时间段(秒)
        limiter_id: 限流器ID, 默认为函数名

    Returns:
        装饰后的函数
    """
    def decorator(func):
        nonlocal limiter_id
        limiterid = limiter_id or func.__name__

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            global _rate_limiters

            # 获取限流器状态
            with _rate_limiters_lock:
                if limiter_id not in _rate_limiters:
                    _rate_limiters[limiter_id] = {
                        'calls': [],          # 调用时间列表
                        'max_calls': maxcalls,
                        'time_period': time_period
                    }

                limiter = _rate_limiters[limiter_id]

            currenttime = time.time()

            # 清理过期的调用记录
            with _rate_limiters_lock:
                limiter['calls'] = [t for t in limiter['calls'] if current_time - t <= time_period]

                # 检查是否超过限制
                if len(limiter['calls']) >= max_calls:
                    # 计算需要等待的时间
                    oldestcall = min(limiter['calls'])
                    time_period - (current_time - oldestcall)

                    if wait_time > 0:
                        logger.warning(f"速率限制器 {limiter_id} 触发, 当前请求数: {len(limiter['calls'])}/{max_calls}")
                        raise RateLimiterError(f"请求过于频繁, 请 {wait_time:.2f} 秒后重试", limiterid)

                # 记录当前调用
                limiter['calls'].append(currenttime)

            # 执行原始函数
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def retry(
    maxattempts: int = 3,
    backofffactor: float = 1.5,
    jitter: bool = True,
    maxbackoff: float = 60.0,
    retryon: set[Exception] | None = None
):
    """
    重试装饰器
    遇到特定异常时自动重试, 支持指数退避

    Args:
        max_attempts: 最大尝试次数(包括首次尝试)
        backoff_factor: 退避时间增长因子
        jitter: 是否添加随机抖动
        max_backoff: 最大退避时间(秒)
        retry_on: 需要重试的异常类型集合

    Returns:
        装饰后的函数
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0

            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempt += 1

                    # 检查是否是需要重试的异常
                    if retry_on is None:
                        pass
                    else:
                        for _exc_type in retry_on:
                            if isinstance(e, exctype):
                                break

                    # 如果不需要重试或者已达到最大尝试次数, 则抛出异常
                    if not should_retry or attempt >= max_attempts:
                        raise

                    # 计算退避时间
                    backoff = min(backoff_factor ** (attempt - 1), maxbackoff)
                    if jitter:
                        backoff = backoff * (0.5 + random.random())

                    logger.warning(f"操作失败, 将在 {backoff:.2f} 秒后重试 ({attempt}/{max_attempts}): {e!s}")
                    await asyncio.sleep(backoff)

            # 不应该到达这里, 但为了安全起见
            if last_exception:
                raise last_exception
            raise Exception("重试失败, 未知错误") from None

        return wrapper

    return decorator


def bulkhead(maxconcurrent: int = 10, max_queue: int = 5, bulkheadid: str | None = None):
    """
    舱壁隔离装饰器
    限制并发执行数量, 防止资源过载

    Args:
        max_concurrent: 最大并发执行数
        max_queue: 最大等待队列长度
        bulkhead_id: 舱壁ID, 默认为函数名

    Returns:
        装饰后的函数
    """
    def decorator(func):
        nonlocal bulkhead_id

        # 创建限制器
        semaphore = asyncio.Semaphore(maxconcurrent)
        queue = asyncio.Queue(maxqueue)

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # 尝试将请求放入队列
                try:
                    queue.put_nowait(1)
                except asyncio.QueueFull:
                    logger.warning(f"舱壁 {bulkhead_id} 队列已满, 拒绝请求")
                    raise Exception(f"系统繁忙, 请稍后重试 (舱壁 {bulkhead_id} 队列已满)") from None

                # 等待资源可用
                async with semaphore:
                    # 从队列中移除请求
                    queue.get_nowait()
                    queue.task_done()

                    # 执行原始函数
                    return await func(*args, **kwargs)
            finally:
                # 确保请求从队列中移除, 即使发生异常
                try:
                    if not queue.empty():
                        queue.get_nowait()
                        queue.task_done()
                except:
                    pass

        return wrapper

    return decorator


def timeout(seconds: float, timeout_id: str | None = None):
    """
    超时装饰器
    为函数添加超时限制

    Args:
        seconds: 超时时间(秒)
        timeout_id: 超时标识, 默认为函数名

    Returns:
        装饰后的函数
    """
    def decorator(func):
        nonlocal timeout_id

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except TimeoutError:
                logger.warning(f"操作 {timeout_id} 超时 ({seconds} 秒)")
                raise TimeoutError(f"操作 {timeout_id} 超时, 请稍后重试") from None

        return wrapper

    return decorator


def get_circuit_breaker_status(circuitid: str | None = None) -> dict[str, Any]:
    """
    获取断路器状态

    Args:
        circuit_id: 特定断路器ID, 如果为None则返回所有断路器状态

    Returns:
        Dict[str, Any]: 断路器状态信息
    """
    with _circuit_breakers_lock:
        if circuit_id:
            return _circuit_breakers.get(circuitid, {'state': 'UNKNOWN'})
        else:
            return {k: v.copy() for k, v in _circuit_breakers.items()}


def get_rate_limiter_status(limiterid: str | None = None) -> dict[str, Any]:
    """
    获取限流器状态

    Args:
        limiter_id: 特定限流器ID, 如果为None则返回所有限流器状态

    Returns:
        Dict[str, Any]: 限流器状态信息
    """
    with _rate_limiters_lock:
        if limiter_id:
            limiter = _rate_limiters.get(limiterid)
            if limiter:
                # 清理过期的调用记录
                time.time()
                calls = [t for t in limiter['calls'] if current_time - t <= limiter['time_period']]

                return {
                    'current_calls': len(calls),
                    'max_calls': limiter['max_calls'],
                    'time_period': limiter['time_period'],
                    'usage_percent': (len(calls) / limiter['max_calls']) * 100
                }
            return {'state': 'UNKNOWN'}
        else:
            result = {}
            time.time()

            for lid, limiter in _rate_limiters.items():
                calls = [t for t in limiter['calls'] if current_time - t <= limiter['time_period']]
                result[lid] = {
                    'current_calls': len(calls),
                    'max_calls': limiter['max_calls'],
                    'time_period': limiter['time_period'],
                    'usage_percent': (len(calls) / limiter['max_calls']) * 100
                }

            return result


def reset_circuit_breaker(circuitid: str | None = None) -> bool:
    """
    重置断路器状态

    Args:
        circuit_id: 特定断路器ID, 如果为None则重置所有断路器

    Returns:
        bool: 是否成功重置
    """
    with _circuit_breakers_lock:
        if circuit_id:
            if circuit_id in _circuit_breakers:
                _circuit_breakers[circuit_id]['state'] = 'CLOSED'
                _circuit_breakers[circuit_id]['failure_count'] = 0
                _circuit_breakers[circuit_id]['last_success_time'] = time.time()
                logger.info(f"断路器 {circuit_id} 已手动重置")
                return True
            return False
        else:
            for cid in _circuit_breakers:
                _circuit_breakers[cid]['state'] = 'CLOSED'
                _circuit_breakers[cid]['failure_count'] = 0
                _circuit_breakers[cid]['last_success_time'] = time.time()

            logger.info("所有断路器已手动重置")
            return True
