"""
circuit_breaker - 索克生活项目模块
"""

from enum import Enum
from functools import wraps
from loguru import logger
from typing import Callable, Any, Dict, Optional, TypeVar, Awaitable, Union, List
import asyncio
import random
import time

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
断路器模块，用于提高服务的容错能力
"""



T = TypeVar('T')


class CircuitState(Enum):
    """断路器状态"""
    CLOSED = "closed"  # 关闭状态，允许请求通过
    OPEN = "open"      # 开启状态，阻止请求通过
    HALF_OPEN = "half_open"  # 半开状态，允许部分请求通过以测试服务是否恢复


class CircuitBreakerError(Exception):
    """断路器错误基类"""
    pass


class CircuitOpenError(CircuitBreakerError):
    """断路器开启错误，表示当前断路器处于开启状态，不允许请求通过"""
    
    def __init__(self, service_name: str, reset_timeout: float):
        self.service_name = service_name
        self.reset_timeout = reset_timeout
        super().__init__(f"Circuit for {service_name} is OPEN. Retry after {reset_timeout:.2f}s")


class CircuitBreaker:
    """
    断路器实现，用于增强服务的弹性能力
    
    基于错误率和超时控制服务调用，防止连锁故障
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_threshold: int = 3,
        reset_timeout: float = 30.0,
        timeout: float = 10.0,
        exclude_exceptions: List[type] = None,
        fallback_function: Optional[Callable] = None,
    ):
        """
        初始化断路器
        
        Args:
            name: 断路器名称，通常为被保护的服务名
            failure_threshold: 触发断路器的连续失败次数
            recovery_threshold: 半开状态时恢复所需的连续成功次数
            reset_timeout: 断路器从开启到半开的超时时间（秒）
            timeout: 操作超时时间（秒）
            exclude_exceptions: 不计入失败的异常类型列表
            fallback_function: 服务不可用时的回退函数
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_threshold = recovery_threshold
        self.reset_timeout = reset_timeout
        self.timeout = timeout
        self.exclude_exceptions = exclude_exceptions or []
        self.fallback_function = fallback_function
        
        # 内部状态
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0
        self._last_success_time = 0
        self._lock = asyncio.Lock()
    
    @property
    def state(self) -> CircuitState:
        """获取当前断路器状态"""
        # 如果是开启状态，检查是否应该转为半开
        if self._state == CircuitState.OPEN:
            elapsed = time.time() - self._last_failure_time
            if elapsed >= self.reset_timeout:
                self._state = CircuitState.HALF_OPEN
                logger.info(f"Circuit {self.name} state changed: OPEN -> HALF_OPEN")
        
        return self._state
    
    def _check_exclude_exception(self, exception: Exception) -> bool:
        """检查异常是否应该被排除在失败计数之外"""
        for excluded_type in self.exclude_exceptions:
            if isinstance(exception, excluded_type):
                return True
        return False
    
    async def _handle_success(self) -> None:
        """处理成功情况"""
        async with self._lock:
            self._last_success_time = time.time()
            
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.recovery_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._success_count = 0
                    logger.info(f"Circuit {self.name} state changed: HALF_OPEN -> CLOSED")
            elif self._state == CircuitState.CLOSED:
                self._failure_count = 0
    
    async def _handle_failure(self, exception: Exception) -> None:
        """处理失败情况"""
        # 排除不计入失败的异常
        if self._check_exclude_exception(exception):
            return
        
        async with self._lock:
            self._last_failure_time = time.time()
            
            if self._state == CircuitState.CLOSED:
                self._failure_count += 1
                if self._failure_count >= self.failure_threshold:
                    self._state = CircuitState.OPEN
                    logger.warning(f"Circuit {self.name} state changed: CLOSED -> OPEN. Reason: {str(exception)}")
            
            elif self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                self._success_count = 0
                logger.warning(f"Circuit {self.name} state changed: HALF_OPEN -> OPEN. Reason: {str(exception)}")
    
    async def execute(
        self, 
        function: Callable[..., Awaitable[T]], 
        *args, 
        **kwargs
    ) -> T:
        """
        执行受断路器保护的异步函数
        
        Args:
            function: 要执行的异步函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            函数的返回值
            
        Raises:
            CircuitOpenError: 断路器开启时抛出
            TimeoutError: 操作超时时抛出
            Exception: 其他执行异常
        """
        current_state = self.state
        
        # 检查断路器状态
        if current_state == CircuitState.OPEN:
            logger.warning(f"Circuit {self.name} is OPEN, fast failing request")
            if self.fallback_function:
                return await self.fallback_function(*args, **kwargs)
            else:
                raise CircuitOpenError(self.name, self.reset_timeout)
        
        # 在半开状态下，随机拒绝一部分请求
        if current_state == CircuitState.HALF_OPEN:
            # 只接受约1/3的请求
            if random.random() > 0.3:
                logger.info(f"Circuit {self.name} is HALF_OPEN, randomly rejecting request")
                if self.fallback_function:
                    return await self.fallback_function(*args, **kwargs)
                else:
                    raise CircuitOpenError(self.name, 0)
        
        # 执行函数，带超时控制
        try:
            result = await asyncio.wait_for(function(*args, **kwargs), timeout=self.timeout)
            await self._handle_success()
            return result
        except asyncio.TimeoutError:
            logger.warning(f"Circuit {self.name} timeout after {self.timeout}s")
            await self._handle_failure(asyncio.TimeoutError(f"Operation timeout after {self.timeout}s"))
            if self.fallback_function:
                return await self.fallback_function(*args, **kwargs)
            raise
        except Exception as e:
            logger.warning(f"Circuit {self.name} caught exception: {str(e)}")
            await self._handle_failure(e)
            if self.fallback_function:
                return await self.fallback_function(*args, **kwargs)
            raise


def circuit_breaker(
    name: Optional[str] = None,
    failure_threshold: int = 5,
    recovery_threshold: int = 3,
    reset_timeout: float = 30.0,
    timeout: float = 10.0,
    exclude_exceptions: List[type] = None,
    fallback_function: Optional[Callable] = None,
):
    """
    断路器装饰器，用于保护异步函数
    
    Args:
        name: 断路器名称，默认使用被装饰函数名
        failure_threshold: 触发断路器的连续失败次数
        recovery_threshold: 半开状态时恢复所需的连续成功次数
        reset_timeout: 断路器从开启到半开的超时时间（秒）
        timeout: 操作超时时间（秒）
        exclude_exceptions: 不计入失败的异常类型列表
        fallback_function: 服务不可用时的回退函数
        
    Returns:
        装饰器函数
    """
    breakers = {}
    
    def get_or_create_breaker(breaker_name: str) -> CircuitBreaker:
        """获取或创建断路器实例"""
        if breaker_name not in breakers:
            breakers[breaker_name] = CircuitBreaker(
                name=breaker_name,
                failure_threshold=failure_threshold,
                recovery_threshold=recovery_threshold,
                reset_timeout=reset_timeout,
                timeout=timeout,
                exclude_exceptions=exclude_exceptions,
                fallback_function=fallback_function,
            )
        return breakers[breaker_name]
    
    def decorator(func):
        breaker_name = name or func.__name__
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            breaker = get_or_create_breaker(breaker_name)
            return await breaker.execute(func, *args, **kwargs)
        
        return wrapper
    
    return decorator


class CircuitBreakerRegistry:
    """断路器注册表，管理多个断路器实例"""
    
    _instance = None
    _breakers: Dict[str, CircuitBreaker] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CircuitBreakerRegistry, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def get(cls, name: str) -> Optional[CircuitBreaker]:
        """获取指定名称的断路器"""
        return cls._breakers.get(name)
    
    @classmethod
    def register(cls, breaker: CircuitBreaker) -> None:
        """注册断路器"""
        cls._breakers[breaker.name] = breaker
    
    @classmethod
    def create_and_register(
        cls,
        name: str,
        failure_threshold: int = 5,
        recovery_threshold: int = 3,
        reset_timeout: float = 30.0,
        timeout: float = 10.0,
        exclude_exceptions: List[type] = None,
        fallback_function: Optional[Callable] = None,
    ) -> CircuitBreaker:
        """创建并注册断路器"""
        breaker = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            recovery_threshold=recovery_threshold,
            reset_timeout=reset_timeout,
            timeout=timeout,
            exclude_exceptions=exclude_exceptions,
            fallback_function=fallback_function,
        )
        cls.register(breaker)
        return breaker
    
    @classmethod
    def list_all(cls) -> Dict[str, Dict[str, Any]]:
        """列出所有断路器及其状态"""
        result = {}
        for name, breaker in cls._breakers.items():
            result[name] = {
                "state": breaker.state.value,
                "failure_count": breaker._failure_count,
                "success_count": breaker._success_count,
                "failure_threshold": breaker.failure_threshold,
                "recovery_threshold": breaker.recovery_threshold,
                "last_failure_time": breaker._last_failure_time,
                "last_success_time": breaker._last_success_time,
            }
        return result 