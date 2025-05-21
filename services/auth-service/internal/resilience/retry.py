#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重试策略模块

提供可配置的重试机制，支持指数回退和抖动，减轻服务压力
"""
import asyncio
import functools
import random
import time
from typing import Any, Callable, List, Optional, Type, TypeVar, Union, cast

from internal.observability.telemetry import get_logger

# 创建日志记录器
logger = get_logger(__name__)

# 函数结果类型
T = TypeVar("T")


class RetryError(Exception):
    """重试失败异常"""
    def __init__(self, message: str, last_exception: Optional[Exception] = None):
        self.last_exception = last_exception
        super().__init__(message)


class Retrier:
    """重试策略实现"""
    
    def __init__(
        self,
        name: str,
        max_attempts: int = 3,
        initial_backoff: float = 1.0,
        max_backoff: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        retry_exceptions: List[Type[Exception]] = None,
        ignore_exceptions: List[Type[Exception]] = None
    ):
        """
        初始化重试器
        
        Args:
            name: 重试器名称，用于日志
            max_attempts: 最大尝试次数
            initial_backoff: 初始等待时间（秒）
            max_backoff: 最大等待时间（秒）
            backoff_factor: 回退因子（指数增长）
            jitter: 是否添加随机抖动
            retry_exceptions: 触发重试的异常类型列表
            ignore_exceptions: 不触发重试的异常类型列表
        """
        self.name = name
        self.max_attempts = max_attempts
        self.initial_backoff = initial_backoff
        self.max_backoff = max_backoff
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retry_exceptions = retry_exceptions or [Exception]
        self.ignore_exceptions = ignore_exceptions or []
        
        # 统计数据
        self._total_attempts = 0
        self._total_success = 0
        self._total_failures = 0
        self._total_retries = 0
    
    def _is_exception_retryable(self, exception: Exception) -> bool:
        """
        检查异常是否应该触发重试
        
        Args:
            exception: 要检查的异常
            
        Returns:
            是否应该重试
        """
        # 如果异常在忽略列表中，则不重试
        for ignored in self.ignore_exceptions:
            if isinstance(exception, ignored):
                return False
        
        # 如果异常在重试列表中，则重试
        for retryable in self.retry_exceptions:
            if isinstance(exception, retryable):
                return True
        
        # 默认不重试
        return False
    
    def _calculate_backoff_time(self, attempt: int) -> float:
        """
        计算重试等待时间
        
        Args:
            attempt: 当前尝试次数
            
        Returns:
            等待时间（秒）
        """
        # 计算指数回退等待时间
        backoff = min(
            self.max_backoff,
            self.initial_backoff * (self.backoff_factor ** (attempt - 1))
        )
        
        # 如果启用抖动，则添加随机波动
        if self.jitter:
            backoff = backoff * (0.5 + random.random())
        
        return backoff
    
    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        装饰器方法，用于包装需要重试的函数
        
        Args:
            func: 要重试的函数
            
        Returns:
            包装后的函数
        """
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                return await self.call_async(func, *args, **kwargs)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                return asyncio.run(self.call_async(func, *args, **kwargs))
            return sync_wrapper
    
    async def call_async(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """
        异步调用函数并处理重试
        
        Args:
            func: 要调用的函数
            args: 位置参数
            kwargs: 关键字参数
            
        Returns:
            函数返回值
            
        Raises:
            RetryError: 重试次数用尽仍然失败
            Exception: 不可重试的异常
        """
        attempt = 0
        last_exception = None
        
        while attempt < self.max_attempts:
            attempt += 1
            self._total_attempts += 1
            
            try:
                # 根据函数类型选择同步或异步调用
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # 调用成功
                self._total_success += 1
                if attempt > 1:
                    logger.info(f"重试器 {self.name} 在第 {attempt} 次尝试成功")
                    
                return result
                
            except Exception as e:
                last_exception = e
                
                # 判断是否可以重试
                if attempt < self.max_attempts and self._is_exception_retryable(e):
                    self._total_retries += 1
                    backoff_time = self._calculate_backoff_time(attempt)
                    
                    logger.warning(
                        f"重试器 {self.name} 第 {attempt} 次调用失败: {str(e)}, "
                        f"将在 {backoff_time:.2f} 秒后重试"
                    )
                    
                    # 等待后重试
                    await asyncio.sleep(backoff_time)
                else:
                    # 不可重试或次数用尽
                    if not self._is_exception_retryable(e):
                        logger.warning(f"重试器 {self.name} 遇到不可重试异常: {str(e)}")
                        raise  # 直接抛出不可重试的异常
                    else:
                        self._total_failures += 1
                        logger.error(
                            f"重试器 {self.name} 重试 {attempt} 次后仍然失败: {str(e)}"
                        )
                        break  # 重试次数用尽，跳出循环
        
        # 所有重试都失败
        self._total_failures += 1
        raise RetryError(
            f"重试器 {self.name} 在 {self.max_attempts} 次尝试后失败",
            last_exception
        )


# 便捷函数，用于创建和应用重试策略
def with_retry(
    name: str = "default",
    max_attempts: int = 3,
    initial_backoff: float = 1.0,
    max_backoff: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retry_exceptions: List[Type[Exception]] = None,
    ignore_exceptions: List[Type[Exception]] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    创建重试装饰器
    
    Args:
        name: 重试器名称
        max_attempts: 最大尝试次数
        initial_backoff: 初始等待时间（秒）
        max_backoff: 最大等待时间（秒）
        backoff_factor: 回退因子
        jitter: 是否添加随机抖动
        retry_exceptions: 触发重试的异常类型列表
        ignore_exceptions: 不触发重试的异常类型列表
        
    Returns:
        重试装饰器
    """
    retrier = Retrier(
        name=name,
        max_attempts=max_attempts,
        initial_backoff=initial_backoff,
        max_backoff=max_backoff,
        backoff_factor=backoff_factor,
        jitter=jitter,
        retry_exceptions=retry_exceptions,
        ignore_exceptions=ignore_exceptions
    )
    
    return retrier 