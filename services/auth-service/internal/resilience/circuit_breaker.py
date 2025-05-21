#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
断路器实现模块

为外部服务调用提供断路器模式，防止级联故障
支持自定义失败阈值、重试策略和降级行为
"""
import asyncio
import functools
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, cast

from internal.observability.telemetry import get_logger

# 创建日志记录器
logger = get_logger(__name__)

# 断路器状态枚举
class CircuitState(Enum):
    """断路器状态"""
    CLOSED = "closed"  # 正常状态，允许请求通过
    OPEN = "open"      # 断开状态，拒绝所有请求
    HALF_OPEN = "half_open"  # 半开状态，允许有限请求通过测试


# 函数结果类型
T = TypeVar("T")


class CircuitBreakerError(Exception):
    """断路器异常基类"""
    pass


class CircuitOpenError(CircuitBreakerError):
    """断路器开路异常"""
    def __init__(self, service_name: str, open_until: float):
        self.service_name = service_name
        self.open_until = open_until
        time_remaining = max(0, open_until - time.time())
        super().__init__(
            f"服务 {service_name} 的断路器处于开路状态，将在 {time_remaining:.2f} 秒后尝试半开状态"
        )


class CircuitBreaker:
    """断路器实现"""
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_threshold: int = 3,
        recovery_timeout: float = 30.0,
        expected_exceptions: List[Type[Exception]] = None,
        exclude_exceptions: List[Type[Exception]] = None,
        fallback_function: Optional[Callable] = None
    ):
        """
        初始化断路器
        
        Args:
            name: 断路器名称，通常是被保护的服务名
            failure_threshold: 触发断路器开路的连续失败次数
            recovery_threshold: 半开状态下恢复所需的成功次数
            recovery_timeout: 断路器从开路到半开状态的超时时间（秒）
            expected_exceptions: 计入失败次数的异常类型列表
            exclude_exceptions: 不计入失败次数的异常类型列表
            fallback_function: 断路器开路时的降级函数
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_threshold = recovery_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions or [Exception]
        self.exclude_exceptions = exclude_exceptions or []
        self.fallback_function = fallback_function
        
        # 状态信息
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0
        self._open_until = 0
        
        # 统计数据
        self._total_requests = 0
        self._total_failures = 0
        self._total_successes = 0
        self._total_short_circuited = 0
        self._total_fallback_successes = 0
        self._total_fallback_failures = 0
        
        # 线程安全的锁
        self._lock = asyncio.Lock()
    
    @property
    def state(self) -> CircuitState:
        """获取当前断路器状态"""
        # 如果状态是开路，但已经超过恢复超时时间，则转为半开状态
        if self._state == CircuitState.OPEN and time.time() >= self._open_until:
            self._state = CircuitState.HALF_OPEN
            self._success_count = 0
            logger.info(f"断路器 {self.name} 从开路状态转为半开状态")
        
        return self._state
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """获取断路器指标"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "total_requests": self._total_requests,
            "total_failures": self._total_failures,
            "total_successes": self._total_successes,
            "total_short_circuited": self._total_short_circuited,
            "total_fallback_successes": self._total_fallback_successes,
            "total_fallback_failures": self._total_fallback_failures,
            "failure_threshold": self.failure_threshold,
            "recovery_threshold": self.recovery_threshold,
            "recovery_timeout": self.recovery_timeout
        }
    
    def _is_exception_expected(self, exception: Exception) -> bool:
        """
        检查异常是否是预期中应该触发断路器的类型
        
        Args:
            exception: 要检查的异常
            
        Returns:
            是否应该触发断路器
        """
        # 如果异常在排除列表中，则不计入失败
        for excluded in self.exclude_exceptions:
            if isinstance(exception, excluded):
                return False
        
        # 如果异常在预期列表中，则计入失败
        for expected in self.expected_exceptions:
            if isinstance(exception, expected):
                return True
        
        # 默认不计入
        return False
    
    async def _on_success(self) -> None:
        """处理成功调用"""
        async with self._lock:
            self._total_successes += 1
            
            if self._state == CircuitState.CLOSED:
                # 闭合状态下，重置失败计数
                self._failure_count = 0
            
            elif self._state == CircuitState.HALF_OPEN:
                # 半开状态下，增加成功计数
                self._success_count += 1
                
                # 如果成功次数达到恢复阈值，则关闭断路器
                if self._success_count >= self.recovery_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._success_count = 0
                    logger.info(f"断路器 {self.name} 从半开状态转为闭合状态")
    
    async def _on_failure(self, exception: Exception) -> None:
        """
        处理失败调用
        
        Args:
            exception: 失败异常
        """
        async with self._lock:
            self._total_failures += 1
            self._last_failure_time = time.time()
            
            # 如果不是预期异常，则不影响断路器状态
            if not self._is_exception_expected(exception):
                return
            
            if self._state == CircuitState.CLOSED:
                # 闭合状态下，增加失败计数
                self._failure_count += 1
                
                # 如果失败次数达到阈值，则打开断路器
                if self._failure_count >= self.failure_threshold:
                    self._state = CircuitState.OPEN
                    self._open_until = time.time() + self.recovery_timeout
                    logger.warning(
                        f"断路器 {self.name} 从闭合状态转为开路状态，"
                        f"将在 {self.recovery_timeout} 秒后尝试半开状态"
                    )
            
            elif self._state == CircuitState.HALF_OPEN:
                # 半开状态下，任何失败都会重新打开断路器
                self._state = CircuitState.OPEN
                self._open_until = time.time() + self.recovery_timeout
                self._success_count = 0
                logger.warning(
                    f"断路器 {self.name} 从半开状态转为开路状态，"
                    f"将在 {self.recovery_timeout} 秒后再次尝试半开状态"
                )
    
    async def _handle_short_circuit(self, *args: Any, **kwargs: Any) -> Any:
        """
        处理断路器开路时的请求
        
        Returns:
            降级函数的返回值
            
        Raises:
            CircuitOpenError: 如果没有提供降级函数
        """
        self._total_short_circuited += 1
        
        # 如果有降级函数，则调用
        if self.fallback_function:
            try:
                if asyncio.iscoroutinefunction(self.fallback_function):
                    result = await self.fallback_function(*args, **kwargs)
                else:
                    result = self.fallback_function(*args, **kwargs)
                
                self._total_fallback_successes += 1
                return result
            except Exception as e:
                self._total_fallback_failures += 1
                logger.exception(f"断路器 {self.name} 降级函数失败: {str(e)}")
                raise
        
        # 没有降级函数，则抛出断路器开路异常
        raise CircuitOpenError(self.name, self._open_until)
    
    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        装饰器方法，用于包装需要断路器保护的函数
        
        Args:
            func: 要保护的函数
            
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
        异步调用受保护的函数
        
        Args:
            func: 要调用的函数
            args: 位置参数
            kwargs: 关键字参数
            
        Returns:
            函数返回值
            
        Raises:
            Exception: 函数抛出的异常（如果断路器允许通过）
        """
        self._total_requests += 1
        
        # 检查断路器状态
        current_state = self.state
        
        # 如果断路器开路，则短路请求
        if current_state == CircuitState.OPEN:
            return await self._handle_short_circuit(*args, **kwargs)
        
        # 尝试执行函数
        try:
            # 根据函数类型选择同步或异步调用
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # 处理成功情况
            await self._on_success()
            return result
        
        except Exception as e:
            # 处理失败情况
            await self._on_failure(e)
            raise
    
    def reset(self) -> None:
        """重置断路器状态为闭合"""
        async def _reset():
            async with self._lock:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                self._success_count = 0
                self._last_failure_time = 0
                self._open_until = 0
                logger.info(f"断路器 {self.name} 已重置为闭合状态")
        
        asyncio.create_task(_reset())


# 全局断路器注册表
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str) -> Optional[CircuitBreaker]:
    """
    获取指定名称的断路器
    
    Args:
        name: 断路器名称
        
    Returns:
        断路器实例，如果不存在则返回None
    """
    return _circuit_breakers.get(name)


def register_circuit_breaker(circuit_breaker: CircuitBreaker) -> None:
    """
    注册断路器到全局注册表
    
    Args:
        circuit_breaker: 断路器实例
    """
    _circuit_breakers[circuit_breaker.name] = circuit_breaker
    logger.info(f"断路器 {circuit_breaker.name} 已注册")


def create_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_threshold: int = 3,
    recovery_timeout: float = 30.0,
    expected_exceptions: List[Type[Exception]] = None,
    exclude_exceptions: List[Type[Exception]] = None,
    fallback_function: Optional[Callable] = None
) -> CircuitBreaker:
    """
    创建并注册新的断路器
    
    Args:
        name: 断路器名称
        failure_threshold: 失败阈值
        recovery_threshold: 恢复阈值
        recovery_timeout: 恢复超时时间（秒）
        expected_exceptions: 预期异常类型列表
        exclude_exceptions: 排除异常类型列表
        fallback_function: 降级函数
        
    Returns:
        创建的断路器实例
    """
    circuit_breaker = CircuitBreaker(
        name=name,
        failure_threshold=failure_threshold,
        recovery_threshold=recovery_threshold,
        recovery_timeout=recovery_timeout,
        expected_exceptions=expected_exceptions,
        exclude_exceptions=exclude_exceptions,
        fallback_function=fallback_function
    )
    
    register_circuit_breaker(circuit_breaker)
    return circuit_breaker


def get_all_circuit_breakers() -> Dict[str, CircuitBreaker]:
    """
    获取所有已注册的断路器
    
    Returns:
        断路器名称到实例的映射
    """
    return _circuit_breakers.copy()


def reset_all_circuit_breakers() -> None:
    """重置所有断路器状态"""
    for cb in _circuit_breakers.values():
        cb.reset()
    logger.info("所有断路器已重置") 