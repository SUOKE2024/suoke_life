#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
断路器模式实现
用于服务间通信中的错误处理和恢复机制
"""

import time
import logging
import asyncio
import functools
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Dict, Any, Optional, Awaitable, TypeVar, Generic, Union, List

# 设置日志
logger = logging.getLogger(__name__)

# 定义返回类型泛型
T = TypeVar('T')


class CircuitState(Enum):
    """断路器状态枚举"""
    CLOSED = 'CLOSED'          # 正常状态，请求可以通过
    OPEN = 'OPEN'              # 断开状态，请求被阻止
    HALF_OPEN = 'HALF_OPEN'    # 半开状态，允许部分请求通过进行测试


@dataclass
class CircuitBreakerConfig:
    """断路器配置"""
    failure_threshold: int = 5         # 触发断路器的失败次数阈值
    success_threshold: int = 2         # 恢复正常所需的成功次数
    timeout_seconds: int = 30          # 断路器打开后的超时时间（秒）
    exclude_exceptions: List[type] = None  # 不计入失败次数的异常类型列表


class CircuitBreaker(Generic[T]):
    """断路器实现类"""
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        """
        初始化断路器
        
        Args:
            name: 断路器名称（通常是被保护的服务名）
            config: 断路器配置，如果为None则使用默认配置
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.exclude_exceptions = self.config.exclude_exceptions or []
        
        # 状态追踪
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.last_success_time = 0
        
        logger.info(f"创建断路器: {self.name}，初始状态: {self.state.value}")
    
    async def execute(self, func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        """
        执行受断路器保护的异步函数
        
        Args:
            func: 要执行的异步函数
            *args: 传递给函数的位置参数
            **kwargs: 传递给函数的关键字参数
            
        Returns:
            函数执行结果
            
        Raises:
            CircuitBreakerOpenError: 当断路器处于打开状态时抛出
            Exception: 函数执行过程中的任何异常
        """
        # 检查断路器状态
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.config.timeout_seconds:
                # 超时后转到半开状态
                logger.info(f"断路器 {self.name} 从OPEN状态转为HALF_OPEN状态")
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                # 断路器仍处于打开状态，快速失败
                logger.warning(f"断路器 {self.name} 处于OPEN状态，拒绝请求")
                raise CircuitBreakerOpenError(f"断路器 {self.name} 已打开")
        
        try:
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 处理成功情况
            self._handle_success()
            
            return result
            
        except Exception as e:
            # 处理异常情况
            self._handle_failure(e)
            
            # 重新抛出异常
            raise
    
    def _handle_success(self):
        """处理成功调用"""
        self.last_success_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            # 在半开状态下累计成功次数
            self.success_count += 1
            logger.debug(f"断路器 {self.name} 在HALF_OPEN状态下成功执行，成功计数: {self.success_count}/{self.config.success_threshold}")
            
            if self.success_count >= self.config.success_threshold:
                # 达到成功阈值，恢复到关闭状态
                logger.info(f"断路器 {self.name} 从HALF_OPEN状态转为CLOSED状态")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
        
        elif self.state == CircuitState.CLOSED:
            # 在关闭状态下重置失败计数
            self.failure_count = 0
    
    def _handle_failure(self, exception: Exception):
        """
        处理失败调用
        
        Args:
            exception: 捕获到的异常
        """
        # 检查是否为排除的异常类型
        if any(isinstance(exception, exc_type) for exc_type in self.exclude_exceptions):
            logger.debug(f"断路器 {self.name} 忽略排除异常: {type(exception).__name__}")
            return
        
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.CLOSED:
            # 在关闭状态下累计失败次数
            self.failure_count += 1
            logger.debug(f"断路器 {self.name} 失败执行，失败计数: {self.failure_count}/{self.config.failure_threshold}")
            
            if self.failure_count >= self.config.failure_threshold:
                # 达到失败阈值，转到打开状态
                logger.warning(f"断路器 {self.name} 从CLOSED状态转为OPEN状态")
                self.state = CircuitState.OPEN
        
        elif self.state == CircuitState.HALF_OPEN:
            # 在半开状态下，任何失败都会重新打开断路器
            logger.warning(f"断路器 {self.name} 在HALF_OPEN状态下失败，重新回到OPEN状态")
            self.state = CircuitState.OPEN
            self.success_count = 0
    
    def reset(self):
        """重置断路器到初始状态"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        logger.info(f"断路器 {self.name} 已重置到CLOSED状态")


class CircuitBreakerOpenError(Exception):
    """断路器打开时的异常"""
    pass


# 全局断路器实例字典
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
    """
    获取或创建命名断路器实例
    
    Args:
        name: 断路器名称
        config: 断路器配置（仅在首次创建时使用）
        
    Returns:
        CircuitBreaker实例
    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(name, config)
    
    return _circuit_breakers[name]


def with_circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None):
    """
    断路器装饰器
    
    Args:
        name: 断路器名称
        config: 断路器配置（仅在首次创建时使用）
        
    Returns:
        装饰器函数
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取断路器实例
            circuit_breaker = get_circuit_breaker(name, config)
            
            # 使用断路器执行函数
            return await circuit_breaker.execute(func, *args, **kwargs)
        
        return wrapper
    
    return decorator


async def with_retry(
    func: Callable[..., Awaitable[T]], 
    max_retries: int = 3, 
    retry_delay: float = 0.5, 
    backoff_factor: float = 2.0,
    retry_exceptions: List[type] = None
) -> T:
    """
    重试机制包装器
    
    Args:
        func: 要执行的异步函数
        max_retries: 最大重试次数
        retry_delay: 初始重试延迟(秒)
        backoff_factor: 退避因子(每次重试增加的倍数)
        retry_exceptions: 可重试的异常类型列表，如果为None则重试所有异常
        
    Returns:
        函数执行结果
        
    Raises:
        Exception: 超过重试次数后仍然失败的异常
    """
    retry_exceptions = retry_exceptions or [Exception]
    retries = 0
    delay = retry_delay
    
    while True:
        try:
            return await func()
        except Exception as e:
            # 判断是否是可重试的异常
            if not any(isinstance(e, exc_type) for exc_type in retry_exceptions):
                raise
            
            retries += 1
            if retries > max_retries:
                logger.error(f"达到最大重试次数 {max_retries}，放弃重试")
                raise
            
            logger.warning(f"操作失败 (重试 {retries}/{max_retries})，等待 {delay:.2f} 秒后重试. 异常: {str(e)}")
            
            # 等待后重试
            await asyncio.sleep(delay)
            
            # 增加退避延迟
            delay *= backoff_factor 