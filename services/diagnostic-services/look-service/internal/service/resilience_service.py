#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
弹性和重试服务

提供错误处理、重试机制、断路器、超时控制等功能。
"""

import asyncio
import time
import random
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List, Union, Type
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager
from functools import wraps

from structlog import get_logger

logger = get_logger()


class RetryStrategy(Enum):
    """重试策略"""
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    RANDOM = "random"


class CircuitBreakerState(Enum):
    """断路器状态"""
    CLOSED = "closed"      # 正常状态
    OPEN = "open"          # 断开状态
    HALF_OPEN = "half_open"  # 半开状态


@dataclass
class RetryConfig:
    """重试配置"""
    max_attempts: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_multiplier: float = 2.0
    jitter: bool = True
    exceptions: List[Type[Exception]] = field(default_factory=lambda: [Exception])
    stop_on_exceptions: List[Type[Exception]] = field(default_factory=list)


@dataclass
class CircuitBreakerConfig:
    """断路器配置"""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    expected_exception: Type[Exception] = Exception
    success_threshold: int = 3  # 半开状态下需要的成功次数


@dataclass
class TimeoutConfig:
    """超时配置"""
    timeout: float = 30.0
    raise_on_timeout: bool = True


class RetryableError(Exception):
    """可重试错误"""
    pass


class NonRetryableError(Exception):
    """不可重试错误"""
    pass


class CircuitBreakerOpenError(Exception):
    """断路器开启错误"""
    pass


class TimeoutError(Exception):
    """超时错误"""
    pass


class RetryService:
    """重试服务"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
        
    def calculate_delay(self, attempt: int) -> float:
        """计算延迟时间"""
        if self.config.strategy == RetryStrategy.FIXED:
            delay = self.config.base_delay
        elif self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.config.base_delay * (self.config.backoff_multiplier ** (attempt - 1))
        elif self.config.strategy == RetryStrategy.LINEAR:
            delay = self.config.base_delay * attempt
        elif self.config.strategy == RetryStrategy.RANDOM:
            delay = random.uniform(self.config.base_delay, self.config.max_delay)
        else:
            delay = self.config.base_delay
        
        # 限制最大延迟
        delay = min(delay, self.config.max_delay)
        
        # 添加抖动
        if self.config.jitter:
            jitter_range = delay * 0.1
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)
    
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """判断是否应该重试"""
        # 检查是否超过最大重试次数
        if attempt >= self.config.max_attempts:
            return False
        
        # 检查是否是停止重试的异常
        for stop_exception in self.config.stop_on_exceptions:
            if isinstance(exception, stop_exception):
                return False
        
        # 检查是否是可重试的异常
        for retry_exception in self.config.exceptions:
            if isinstance(exception, retry_exception):
                return True
        
        return False
    
    async def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """执行带重试的函数"""
        last_exception = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                logger.debug(
                    "执行重试函数",
                    function=func.__name__,
                    attempt=attempt,
                    max_attempts=self.config.max_attempts
                )
                
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                if attempt > 1:
                    logger.info(
                        "重试成功",
                        function=func.__name__,
                        attempt=attempt,
                        total_attempts=attempt
                    )
                
                return result
                
            except Exception as e:
                last_exception = e
                
                if not self.should_retry(e, attempt):
                    logger.error(
                        "重试失败，不再重试",
                        function=func.__name__,
                        attempt=attempt,
                        error=str(e),
                        error_type=type(e).__name__
                    )
                    raise e
                
                if attempt < self.config.max_attempts:
                    delay = self.calculate_delay(attempt)
                    logger.warning(
                        "重试失败，等待后重试",
                        function=func.__name__,
                        attempt=attempt,
                        error=str(e),
                        delay_seconds=delay
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        "重试次数已用完",
                        function=func.__name__,
                        total_attempts=attempt,
                        error=str(e)
                    )
        
        # 如果所有重试都失败了，抛出最后一个异常
        raise last_exception


class CircuitBreaker:
    """断路器"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.next_attempt_time = None
        
    def _should_attempt_reset(self) -> bool:
        """判断是否应该尝试重置"""
        return (self.state == CircuitBreakerState.OPEN and
                self.next_attempt_time and
                time.time() >= self.next_attempt_time)
    
    def _on_success(self):
        """成功回调"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._reset()
        elif self.state == CircuitBreakerState.CLOSED:
            self.failure_count = 0
    
    def _on_failure(self, exception: Exception):
        """失败回调"""
        if isinstance(exception, self.config.expected_exception):
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                self._open()
            elif (self.state == CircuitBreakerState.CLOSED and
                  self.failure_count >= self.config.failure_threshold):
                self._open()
    
    def _open(self):
        """打开断路器"""
        self.state = CircuitBreakerState.OPEN
        self.next_attempt_time = time.time() + self.config.recovery_timeout
        logger.warning(
            "断路器已打开",
            failure_count=self.failure_count,
            recovery_timeout=self.config.recovery_timeout
        )
    
    def _half_open(self):
        """半开断路器"""
        self.state = CircuitBreakerState.HALF_OPEN
        self.success_count = 0
        logger.info("断路器已半开")
    
    def _reset(self):
        """重置断路器"""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.next_attempt_time = None
        logger.info("断路器已重置")
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """执行带断路器保护的函数"""
        # 检查是否应该尝试重置
        if self._should_attempt_reset():
            self._half_open()
        
        # 如果断路器是开启状态，直接抛出异常
        if self.state == CircuitBreakerState.OPEN:
            raise CircuitBreakerOpenError("断路器已开启，拒绝执行")
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure(e)
            raise
    
    def get_state(self) -> Dict[str, Any]:
        """获取断路器状态"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "next_attempt_time": self.next_attempt_time
        }


class TimeoutService:
    """超时服务"""
    
    def __init__(self, config: TimeoutConfig):
        self.config = config
    
    async def execute_with_timeout(self, func: Callable, *args, **kwargs) -> Any:
        """执行带超时的函数"""
        try:
            if asyncio.iscoroutinefunction(func):
                coro = func(*args, **kwargs)
            else:
                loop = asyncio.get_event_loop()
                coro = loop.run_in_executor(None, func, *args, **kwargs)
            
            result = await asyncio.wait_for(coro, timeout=self.config.timeout)
            return result
            
        except asyncio.TimeoutError:
            error_msg = f"函数执行超时 ({self.config.timeout}s): {func.__name__}"
            logger.warning(error_msg)
            
            if self.config.raise_on_timeout:
                raise TimeoutError(error_msg)
            else:
                return None


class ResilienceService:
    """弹性服务 - 组合重试、断路器和超时功能"""
    
    def __init__(self, 
                 retry_config: Optional[RetryConfig] = None,
                 circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
                 timeout_config: Optional[TimeoutConfig] = None):
        
        self.retry_service = RetryService(retry_config) if retry_config else None
        self.circuit_breaker = CircuitBreaker(circuit_breaker_config) if circuit_breaker_config else None
        self.timeout_service = TimeoutService(timeout_config) if timeout_config else None
        
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """执行带弹性保护的函数"""
        
        async def protected_func(*args, **kwargs):
            # 应用超时保护
            if self.timeout_service:
                return await self.timeout_service.execute_with_timeout(func, *args, **kwargs)
            else:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
        
        # 应用断路器保护
        if self.circuit_breaker:
            protected_func = lambda *a, **kw: self.circuit_breaker.execute(protected_func, *a, **kw)
        
        # 应用重试保护
        if self.retry_service:
            return await self.retry_service.execute_with_retry(protected_func, *args, **kwargs)
        else:
            return await protected_func(*args, **kwargs)
    
    def get_status(self) -> Dict[str, Any]:
        """获取弹性服务状态"""
        status = {}
        
        if self.circuit_breaker:
            status["circuit_breaker"] = self.circuit_breaker.get_state()
        
        if self.retry_service:
            status["retry"] = {
                "max_attempts": self.retry_service.config.max_attempts,
                "strategy": self.retry_service.config.strategy.value
            }
        
        if self.timeout_service:
            status["timeout"] = {
                "timeout": self.timeout_service.config.timeout,
                "raise_on_timeout": self.timeout_service.config.raise_on_timeout
            }
        
        return status


# 装饰器
def retry(config: RetryConfig = None):
    """重试装饰器"""
    if config is None:
        config = RetryConfig()
    
    retry_service = RetryService(config)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_service.execute_with_retry(func, *args, **kwargs)
        return wrapper
    return decorator


def circuit_breaker(config: CircuitBreakerConfig = None):
    """断路器装饰器"""
    if config is None:
        config = CircuitBreakerConfig()
    
    cb = CircuitBreaker(config)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await cb.execute(func, *args, **kwargs)
        return wrapper
    return decorator


def timeout(timeout_seconds: float = 30.0, raise_on_timeout: bool = True):
    """超时装饰器"""
    config = TimeoutConfig(timeout=timeout_seconds, raise_on_timeout=raise_on_timeout)
    timeout_service = TimeoutService(config)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await timeout_service.execute_with_timeout(func, *args, **kwargs)
        return wrapper
    return decorator


def resilient(retry_config: RetryConfig = None,
              circuit_breaker_config: CircuitBreakerConfig = None,
              timeout_config: TimeoutConfig = None):
    """弹性装饰器 - 组合所有保护机制"""
    resilience_service = ResilienceService(retry_config, circuit_breaker_config, timeout_config)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await resilience_service.execute(func, *args, **kwargs)
        return wrapper
    return decorator


# 上下文管理器
@asynccontextmanager
async def resilience_context(retry_config: RetryConfig = None,
                           circuit_breaker_config: CircuitBreakerConfig = None,
                           timeout_config: TimeoutConfig = None):
    """弹性上下文管理器"""
    service = ResilienceService(retry_config, circuit_breaker_config, timeout_config)
    try:
        yield service
    finally:
        # 清理资源（如果需要）
        pass


# 预定义配置
class PresetConfigs:
    """预设配置"""
    
    @staticmethod
    def default_retry() -> RetryConfig:
        """默认重试配置"""
        return RetryConfig(
            max_attempts=3,
            strategy=RetryStrategy.EXPONENTIAL,
            base_delay=1.0,
            max_delay=30.0,
            backoff_multiplier=2.0,
            jitter=True
        )
    
    @staticmethod
    def aggressive_retry() -> RetryConfig:
        """激进重试配置"""
        return RetryConfig(
            max_attempts=5,
            strategy=RetryStrategy.EXPONENTIAL,
            base_delay=0.5,
            max_delay=60.0,
            backoff_multiplier=1.5,
            jitter=True
        )
    
    @staticmethod
    def conservative_retry() -> RetryConfig:
        """保守重试配置"""
        return RetryConfig(
            max_attempts=2,
            strategy=RetryStrategy.FIXED,
            base_delay=2.0,
            max_delay=10.0,
            jitter=False
        )
    
    @staticmethod
    def default_circuit_breaker() -> CircuitBreakerConfig:
        """默认断路器配置"""
        return CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=60.0,
            success_threshold=3
        )
    
    @staticmethod
    def sensitive_circuit_breaker() -> CircuitBreakerConfig:
        """敏感断路器配置"""
        return CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30.0,
            success_threshold=2
        )
    
    @staticmethod
    def default_timeout() -> TimeoutConfig:
        """默认超时配置"""
        return TimeoutConfig(
            timeout=30.0,
            raise_on_timeout=True
        )
    
    @staticmethod
    def long_timeout() -> TimeoutConfig:
        """长超时配置"""
        return TimeoutConfig(
            timeout=120.0,
            raise_on_timeout=True
        )
    
    @staticmethod
    def analysis_resilience() -> ResilienceService:
        """分析任务弹性配置"""
        return ResilienceService(
            retry_config=RetryConfig(
                max_attempts=3,
                strategy=RetryStrategy.EXPONENTIAL,
                base_delay=2.0,
                max_delay=30.0,
                exceptions=[ConnectionError, TimeoutError, RetryableError]
            ),
            circuit_breaker_config=CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60.0,
                success_threshold=3
            ),
            timeout_config=TimeoutConfig(
                timeout=60.0,
                raise_on_timeout=True
            )
        )
    
    @staticmethod
    def external_service_resilience() -> ResilienceService:
        """外部服务弹性配置"""
        return ResilienceService(
            retry_config=RetryConfig(
                max_attempts=5,
                strategy=RetryStrategy.EXPONENTIAL,
                base_delay=1.0,
                max_delay=60.0,
                exceptions=[ConnectionError, TimeoutError]
            ),
            circuit_breaker_config=CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30.0,
                success_threshold=2
            ),
            timeout_config=TimeoutConfig(
                timeout=30.0,
                raise_on_timeout=True
            )
        ) 