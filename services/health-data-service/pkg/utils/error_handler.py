#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
错误处理和重试机制模块
"""

import asyncio
import time
import random
from typing import Any, Callable, Dict, List, Optional, Type, Union
from functools import wraps
from enum import Enum

from tenacity import (
    retry, stop_after_attempt, wait_exponential, 
    retry_if_exception_type, before_sleep_log
)
from loguru import logger


class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class HealthDataError(Exception):
    """健康数据服务基础异常"""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "UNKNOWN_ERROR",
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.details = details or {}
        self.timestamp = time.time()


class DatabaseError(HealthDataError):
    """数据库相关错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message, 
            error_code="DATABASE_ERROR",
            severity=ErrorSeverity.HIGH,
            details=details
        )


class CacheError(HealthDataError):
    """缓存相关错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message, 
            error_code="CACHE_ERROR",
            severity=ErrorSeverity.LOW,
            details=details
        )


class ValidationError(HealthDataError):
    """数据验证错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message, 
            error_code="VALIDATION_ERROR",
            severity=ErrorSeverity.MEDIUM,
            details=details
        )


class ExternalServiceError(HealthDataError):
    """外部服务错误"""
    
    def __init__(self, message: str, service_name: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["service_name"] = service_name
        super().__init__(
            message, 
            error_code="EXTERNAL_SERVICE_ERROR",
            severity=ErrorSeverity.MEDIUM,
            details=details
        )


class RateLimitError(HealthDataError):
    """限流错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message, 
            error_code="RATE_LIMIT_ERROR",
            severity=ErrorSeverity.LOW,
            details=details
        )


class CircuitBreakerError(HealthDataError):
    """熔断器错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message, 
            error_code="CIRCUIT_BREAKER_ERROR",
            severity=ErrorSeverity.HIGH,
            details=details
        )


class CircuitBreaker:
    """熔断器实现"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                else:
                    raise CircuitBreakerError(
                        f"熔断器开启，服务不可用",
                        details={
                            "failure_count": self.failure_count,
                            "last_failure_time": self.last_failure_time
                        }
                    )
            
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置熔断器"""
        return (
            self.last_failure_time and 
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def _on_success(self):
        """成功时的处理"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """失败时的处理"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.error_stats = {
            "total_errors": 0,
            "errors_by_type": {},
            "errors_by_severity": {}
        }
    
    def handle_error(
        self, 
        error: Exception, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        处理错误
        
        Args:
            error: 异常对象
            context: 错误上下文
            
        Returns:
            错误处理结果
        """
        context = context or {}
        
        # 更新统计信息
        self._update_stats(error)
        
        # 记录错误日志
        self._log_error(error, context)
        
        # 生成错误响应
        error_response = self._generate_error_response(error, context)
        
        # 发送告警（如果需要）
        if isinstance(error, HealthDataError) and error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self._send_alert(error, context)
        
        return error_response
    
    def _update_stats(self, error: Exception):
        """更新错误统计"""
        self.error_stats["total_errors"] += 1
        
        error_type = type(error).__name__
        self.error_stats["errors_by_type"][error_type] = (
            self.error_stats["errors_by_type"].get(error_type, 0) + 1
        )
        
        if isinstance(error, HealthDataError):
            severity = error.severity.value
            self.error_stats["errors_by_severity"][severity] = (
                self.error_stats["errors_by_severity"].get(severity, 0) + 1
            )
    
    def _log_error(self, error: Exception, context: Dict[str, Any]):
        """记录错误日志"""
        if isinstance(error, HealthDataError):
            logger.error(
                f"健康数据服务错误: {error.message}",
                extra={
                    "error_code": error.error_code,
                    "severity": error.severity.value,
                    "details": error.details,
                    "context": context,
                    "timestamp": error.timestamp
                }
            )
        else:
            logger.error(
                f"未处理的错误: {str(error)}",
                extra={
                    "error_type": type(error).__name__,
                    "context": context
                }
            )
    
    def _generate_error_response(
        self, 
        error: Exception, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成错误响应"""
        if isinstance(error, HealthDataError):
            return {
                "error": True,
                "error_code": error.error_code,
                "message": error.message,
                "severity": error.severity.value,
                "timestamp": error.timestamp,
                "details": error.details
            }
        else:
            return {
                "error": True,
                "error_code": "INTERNAL_ERROR",
                "message": "内部服务错误",
                "severity": ErrorSeverity.HIGH.value,
                "timestamp": time.time()
            }
    
    def _send_alert(self, error: HealthDataError, context: Dict[str, Any]):
        """发送告警"""
        # 这里可以集成告警系统，如邮件、短信、钉钉等
        logger.warning(
            f"发送告警: {error.error_code} - {error.message}",
            extra={
                "severity": error.severity.value,
                "context": context
            }
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """获取错误统计信息"""
        return self.error_stats.copy()


def with_retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    retry_exceptions: tuple = (Exception,),
    stop_exceptions: tuple = (ValidationError,)
):
    """
    重试装饰器
    
    Args:
        max_attempts: 最大重试次数
        backoff_factor: 退避因子
        max_delay: 最大延迟时间
        retry_exceptions: 需要重试的异常类型
        stop_exceptions: 不重试的异常类型
    """
    def decorator(func):
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=1, max=max_delay),
            retry=retry_if_exception_type(retry_exceptions),
            before_sleep=before_sleep_log(logger, "WARNING")
        )
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except stop_exceptions:
                # 不重试的异常直接抛出
                raise
            except retry_exceptions as e:
                logger.warning(f"函数 {func.__name__} 执行失败，准备重试: {str(e)}")
                raise
        
        return wrapper
    return decorator


def with_timeout(timeout_seconds: float = 30.0):
    """
    超时装饰器
    
    Args:
        timeout_seconds: 超时时间（秒）
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs), 
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                raise HealthDataError(
                    f"函数 {func.__name__} 执行超时",
                    error_code="TIMEOUT_ERROR",
                    severity=ErrorSeverity.MEDIUM,
                    details={"timeout_seconds": timeout_seconds}
                )
        
        return wrapper
    return decorator


def safe_execute(
    default_return: Any = None,
    log_errors: bool = True,
    raise_on_error: bool = False
):
    """
    安全执行装饰器
    
    Args:
        default_return: 出错时的默认返回值
        log_errors: 是否记录错误日志
        raise_on_error: 是否在出错时抛出异常
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(f"函数 {func.__name__} 执行出错: {str(e)}")
                
                if raise_on_error:
                    raise
                
                return default_return
        
        return wrapper
    return decorator


# 全局错误处理器实例
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> Optional[ErrorHandler]:
    """获取全局错误处理器"""
    return _error_handler


def init_error_handler(config: Dict[str, Any]) -> ErrorHandler:
    """初始化全局错误处理器"""
    global _error_handler
    _error_handler = ErrorHandler(config)
    return _error_handler


def handle_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """处理错误的便捷函数"""
    if _error_handler:
        return _error_handler.handle_error(error, context)
    else:
        # 如果没有初始化错误处理器，使用简单的错误处理
        logger.error(f"未初始化错误处理器，直接记录错误: {str(error)}")
        return {
            "error": True,
            "message": str(error),
            "timestamp": time.time()
        } 