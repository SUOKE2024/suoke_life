#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重试和弹性管理器
提供智能重试、熔断器模式和错误恢复机制
"""

import asyncio
import logging
import time
import random
from typing import Any, Callable, Dict, List, Optional, Type, Union
from dataclasses import dataclass
from enum import Enum
from functools import wraps

logger = logging.getLogger(__name__)

class RetryStrategy(Enum):
    """重试策略枚举"""
    FIXED = "fixed"  # 固定间隔
    EXPONENTIAL = "exponential"  # 指数退避
    LINEAR = "linear"  # 线性增长
    RANDOM = "random"  # 随机间隔

class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"  # 关闭状态，正常工作
    OPEN = "open"  # 开启状态，拒绝请求
    HALF_OPEN = "half_open"  # 半开状态，尝试恢复

@dataclass
class RetryConfig:
    """重试配置"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    backoff_multiplier: float = 2.0
    jitter: bool = True
    retryable_exceptions: List[Type[Exception]] = None

@dataclass
class CircuitBreakerConfig:
    """熔断器配置"""
    failure_threshold: int = 5  # 失败阈值
    recovery_timeout: float = 60.0  # 恢复超时时间
    expected_exception: Type[Exception] = Exception
    success_threshold: int = 3  # 半开状态成功阈值

class CircuitBreaker:
    """熔断器实现"""
    
    def __init__(self, config: CircuitBreakerConfig):
        """
        初始化熔断器
        
        Args:
            config: 熔断器配置
        """
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        
        logger.debug("熔断器初始化完成，失败阈值: %d", config.failure_threshold)
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        通过熔断器调用函数
        
        Args:
            func: 要调用的函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            函数执行结果
            
        Raises:
            CircuitBreakerOpenException: 熔断器开启时
        """
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time < self.config.recovery_timeout:
                raise CircuitBreakerOpenException("熔断器处于开启状态")
            else:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logger.info("熔断器进入半开状态")
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            self._on_success()
            return result
            
        except self.config.expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """处理成功调用"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logger.info("熔断器恢复到关闭状态")
        else:
            self.failure_count = 0
    
    def _on_failure(self):
        """处理失败调用"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning("熔断器从半开状态转为开启状态")
        elif self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning("熔断器开启，失败次数: %d", self.failure_count)

class CircuitBreakerOpenException(Exception):
    """熔断器开启异常"""
    pass

class RetryManager:
    """重试管理器"""
    
    def __init__(self):
        """初始化重试管理器"""
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_stats = {
            'total_attempts': 0,
            'successful_retries': 0,
            'failed_retries': 0,
            'circuit_breaker_opens': 0
        }
        
        logger.info("重试管理器初始化完成")
    
    def get_circuit_breaker(self, name: str, config: CircuitBreakerConfig = None) -> CircuitBreaker:
        """
        获取或创建熔断器
        
        Args:
            name: 熔断器名称
            config: 熔断器配置
            
        Returns:
            熔断器实例
        """
        if name not in self.circuit_breakers:
            config = config or CircuitBreakerConfig()
            self.circuit_breakers[name] = CircuitBreaker(config)
        
        return self.circuit_breakers[name]
    
    async def retry_with_backoff(
        self,
        func: Callable,
        config: RetryConfig = None,
        circuit_breaker_name: str = None,
        *args,
        **kwargs
    ) -> Any:
        """
        使用退避策略重试函数
        
        Args:
            func: 要重试的函数
            config: 重试配置
            circuit_breaker_name: 熔断器名称
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            函数执行结果
        """
        config = config or RetryConfig()
        last_exception = None
        
        # 获取熔断器（如果指定）
        circuit_breaker = None
        if circuit_breaker_name:
            circuit_breaker = self.get_circuit_breaker(circuit_breaker_name)
        
        for attempt in range(config.max_attempts):
            try:
                self.retry_stats['total_attempts'] += 1
                
                # 通过熔断器调用函数
                if circuit_breaker:
                    result = await circuit_breaker.call(func, *args, **kwargs)
                else:
                    if asyncio.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)
                
                if attempt > 0:
                    self.retry_stats['successful_retries'] += 1
                    logger.info("重试成功，尝试次数: %d", attempt + 1)
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # 检查是否为可重试异常
                if config.retryable_exceptions:
                    if not any(isinstance(e, exc_type) for exc_type in config.retryable_exceptions):
                        logger.warning("遇到不可重试异常: %s", str(e))
                        break
                
                # 检查是否为熔断器开启异常
                if isinstance(e, CircuitBreakerOpenException):
                    logger.warning("熔断器开启，停止重试")
                    break
                
                # 如果是最后一次尝试，不再等待
                if attempt == config.max_attempts - 1:
                    break
                
                # 计算延迟时间
                delay = self._calculate_delay(attempt, config)
                
                logger.warning("第 %d 次尝试失败: %s，%s 秒后重试", 
                             attempt + 1, str(e), delay)
                
                await asyncio.sleep(delay)
        
        # 所有重试都失败
        self.retry_stats['failed_retries'] += 1
        logger.error("重试失败，已达到最大尝试次数: %d", config.max_attempts)
        
        if last_exception:
            raise last_exception
        else:
            raise RuntimeError("重试失败，未知错误")
    
    def _calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """
        计算延迟时间
        
        Args:
            attempt: 当前尝试次数（从0开始）
            config: 重试配置
            
        Returns:
            延迟时间（秒）
        """
        if config.strategy == RetryStrategy.FIXED:
            delay = config.base_delay
        elif config.strategy == RetryStrategy.EXPONENTIAL:
            delay = config.base_delay * (config.backoff_multiplier ** attempt)
        elif config.strategy == RetryStrategy.LINEAR:
            delay = config.base_delay * (attempt + 1)
        elif config.strategy == RetryStrategy.RANDOM:
            delay = random.uniform(config.base_delay, config.max_delay)
        else:
            delay = config.base_delay
        
        # 限制最大延迟
        delay = min(delay, config.max_delay)
        
        # 添加抖动
        if config.jitter:
            jitter_range = delay * 0.1  # 10%的抖动
            delay += random.uniform(-jitter_range, jitter_range)
            delay = max(0, delay)  # 确保延迟不为负数
        
        return delay
    
    def get_stats(self) -> Dict[str, Any]:
        """获取重试统计信息"""
        circuit_breaker_stats = {}
        for name, cb in self.circuit_breakers.items():
            circuit_breaker_stats[name] = {
                'state': cb.state.value,
                'failure_count': cb.failure_count,
                'success_count': cb.success_count,
                'last_failure_time': cb.last_failure_time
            }
        
        return {
            'retry_stats': self.retry_stats.copy(),
            'circuit_breakers': circuit_breaker_stats
        }

# 装饰器函数
def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    backoff_multiplier: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: List[Type[Exception]] = None,
    circuit_breaker_name: str = None
):
    """
    重试装饰器
    
    Args:
        max_attempts: 最大尝试次数
        base_delay: 基础延迟时间
        max_delay: 最大延迟时间
        strategy: 重试策略
        backoff_multiplier: 退避倍数
        jitter: 是否添加抖动
        retryable_exceptions: 可重试异常列表
        circuit_breaker_name: 熔断器名称
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            config = RetryConfig(
                max_attempts=max_attempts,
                base_delay=base_delay,
                max_delay=max_delay,
                strategy=strategy,
                backoff_multiplier=backoff_multiplier,
                jitter=jitter,
                retryable_exceptions=retryable_exceptions
            )
            
            retry_manager = get_retry_manager()
            return await retry_manager.retry_with_backoff(
                func, config, circuit_breaker_name, *args, **kwargs
            )
        
        return wrapper
    return decorator

def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    expected_exception: Type[Exception] = Exception,
    success_threshold: int = 3
):
    """
    熔断器装饰器
    
    Args:
        name: 熔断器名称
        failure_threshold: 失败阈值
        recovery_timeout: 恢复超时时间
        expected_exception: 预期异常类型
        success_threshold: 半开状态成功阈值
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            config = CircuitBreakerConfig(
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                expected_exception=expected_exception,
                success_threshold=success_threshold
            )
            
            retry_manager = get_retry_manager()
            circuit_breaker = retry_manager.get_circuit_breaker(name, config)
            
            return await circuit_breaker.call(func, *args, **kwargs)
        
        return wrapper
    return decorator

# 全局重试管理器实例
_retry_manager: Optional[RetryManager] = None

def get_retry_manager() -> RetryManager:
    """获取重试管理器实例"""
    global _retry_manager
    
    if _retry_manager is None:
        _retry_manager = RetryManager()
    
    return _retry_manager 