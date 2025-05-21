#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
异常处理模块

定义服务中使用的所有自定义异常类型，确保异常处理的一致性
"""

import grpc
from typing import Dict, Type, Optional, Tuple

class LookServiceBaseError(Exception):
    """
    望诊服务基础异常类
    
    所有的自定义异常都应该继承自这个类
    """
    def __init__(self, message: str = "望诊服务错误", error_code: str = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        super().__init__(self.message)
        
    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"


class InvalidInputError(LookServiceBaseError):
    """
    输入验证错误
    
    当提供的输入无效或格式错误时抛出
    """
    def __init__(self, message: str = "输入无效", error_code: str = None):
        super().__init__(message, error_code)


class ResourceNotFoundError(LookServiceBaseError):
    """
    资源不存在错误
    
    当请求的资源（如用户ID、分析记录等）不存在时抛出
    """
    def __init__(self, message: str = "资源不存在", error_code: str = None):
        super().__init__(message, error_code)


class ProcessingError(LookServiceBaseError):
    """
    处理错误
    
    当图像处理、分析过程中出现错误时抛出
    """
    def __init__(self, message: str = "处理过程中出现错误", error_code: str = None):
        super().__init__(message, error_code)


class DependencyError(LookServiceBaseError):
    """
    依赖错误
    
    当外部依赖服务或组件不可用时抛出
    """
    def __init__(self, message: str = "外部依赖服务不可用", error_code: str = None):
        super().__init__(message, error_code)


class ConfigurationError(LookServiceBaseError):
    """
    配置错误
    
    当配置无效或缺失时抛出
    """
    def __init__(self, message: str = "配置错误", error_code: str = None):
        super().__init__(message, error_code)


class ModelLoadingError(LookServiceBaseError):
    """
    模型加载错误
    
    当AI模型加载失败时抛出
    """
    def __init__(self, message: str = "模型加载失败", error_code: str = None):
        super().__init__(message, error_code)


class AuthenticationError(LookServiceBaseError):
    """
    认证错误
    
    当用户认证失败时抛出
    """
    def __init__(self, message: str = "认证失败", error_code: str = None):
        super().__init__(message, error_code)


class AuthorizationError(LookServiceBaseError):
    """
    授权错误
    
    当用户没有足够权限时抛出
    """
    def __init__(self, message: str = "权限不足", error_code: str = None):
        super().__init__(message, error_code)


class DatabaseError(LookServiceBaseError):
    """
    数据库错误
    
    当数据库操作失败时抛出
    """
    def __init__(self, message: str = "数据库操作失败", error_code: str = None):
        super().__init__(message, error_code)


class RateLimitError(LookServiceBaseError):
    """
    限流错误
    
    当请求超过限流阈值时抛出
    """
    def __init__(self, message: str = "请求频率超过限制", error_code: str = None):
        super().__init__(message, error_code)


class ThirdPartyServiceError(LookServiceBaseError):
    """
    第三方服务错误
    
    当依赖的第三方服务返回错误时抛出
    """
    def __init__(self, message: str = "第三方服务错误", error_code: str = None):
        super().__init__(message, error_code)


class TimeoutError(LookServiceBaseError):
    """
    超时错误
    
    当操作超时时抛出
    """
    def __init__(self, message: str = "操作超时", error_code: str = None):
        super().__init__(message, error_code)


class ValidationError(LookServiceBaseError):
    """
    验证错误
    
    当数据验证失败时抛出
    """
    def __init__(self, message: str = "数据验证失败", error_code: str = None):
        super().__init__(message, error_code)


class UnexpectedError(LookServiceBaseError):
    """
    未预期错误
    
    当发生未分类的异常情况时抛出
    """
    def __init__(self, message: str = "发生未预期的错误", error_code: str = None):
        super().__init__(message, error_code)


class CircuitBreakerOpenError(LookServiceBaseError):
    """
    断路器开启错误
    
    当断路器处于开启状态时抛出
    """
    def __init__(self, message: str = "断路器处于开启状态", error_code: str = None):
        super().__init__(message, error_code)


class RetryError(LookServiceBaseError):
    """
    重试错误
    
    当重试操作失败时抛出
    """
    def __init__(self, message: str = "重试操作失败", error_code: str = None):
        super().__init__(message, error_code)


# 将错误代码映射到异常类
ERROR_CODE_MAP: Dict[str, Type[LookServiceBaseError]] = {
    "INVALID_INPUT": InvalidInputError,
    "RESOURCE_NOT_FOUND": ResourceNotFoundError,
    "PROCESSING_ERROR": ProcessingError,
    "DEPENDENCY_ERROR": DependencyError,
    "CONFIGURATION_ERROR": ConfigurationError,
    "MODEL_LOADING_ERROR": ModelLoadingError,
    "AUTHENTICATION_ERROR": AuthenticationError,
    "AUTHORIZATION_ERROR": AuthorizationError,
    "DATABASE_ERROR": DatabaseError,
    "RATE_LIMIT_ERROR": RateLimitError,
    "THIRD_PARTY_SERVICE_ERROR": ThirdPartyServiceError,
    "TIMEOUT_ERROR": TimeoutError,
    "VALIDATION_ERROR": ValidationError,
    "UNEXPECTED_ERROR": UnexpectedError,
    "CIRCUIT_BREAKER_OPEN_ERROR": CircuitBreakerOpenError,
    "RETRY_ERROR": RetryError
}

# gRPC状态码映射
GRPC_STATUS_MAP: Dict[Type[LookServiceBaseError], Tuple[grpc.StatusCode, str]] = {
    InvalidInputError: (grpc.StatusCode.INVALID_ARGUMENT, "无效参数"),
    ResourceNotFoundError: (grpc.StatusCode.NOT_FOUND, "资源未找到"),
    ProcessingError: (grpc.StatusCode.INTERNAL, "内部处理错误"),
    DependencyError: (grpc.StatusCode.UNAVAILABLE, "依赖服务不可用"),
    ConfigurationError: (grpc.StatusCode.INTERNAL, "配置错误"),
    ModelLoadingError: (grpc.StatusCode.INTERNAL, "模型加载错误"),
    AuthenticationError: (grpc.StatusCode.UNAUTHENTICATED, "未认证"),
    AuthorizationError: (grpc.StatusCode.PERMISSION_DENIED, "权限不足"),
    DatabaseError: (grpc.StatusCode.INTERNAL, "数据库错误"),
    RateLimitError: (grpc.StatusCode.RESOURCE_EXHAUSTED, "资源耗尽"),
    ThirdPartyServiceError: (grpc.StatusCode.UNAVAILABLE, "第三方服务错误"),
    TimeoutError: (grpc.StatusCode.DEADLINE_EXCEEDED, "超时"),
    ValidationError: (grpc.StatusCode.INVALID_ARGUMENT, "验证失败"),
    UnexpectedError: (grpc.StatusCode.INTERNAL, "未预期的错误"),
    CircuitBreakerOpenError: (grpc.StatusCode.UNAVAILABLE, "断路器打开"),
    RetryError: (grpc.StatusCode.ABORTED, "重试失败")
}


def create_exception_from_code(error_code: str, message: str = None) -> LookServiceBaseError:
    """
    根据错误代码创建异常实例
    
    Args:
        error_code: 错误代码
        message: 可选的错误消息
        
    Returns:
        相应的异常实例
        
    Raises:
        KeyError: 当错误代码不存在于映射中时
    """
    if error_code not in ERROR_CODE_MAP:
        raise KeyError(f"未知错误代码: {error_code}")
    
    exception_class = ERROR_CODE_MAP[error_code]
    if message:
        return exception_class(message, error_code)
    else:
        return exception_class(error_code=error_code)


def get_grpc_status_from_exception(exception: LookServiceBaseError) -> Tuple[grpc.StatusCode, str]:
    """
    从异常获取gRPC状态码和描述
    
    Args:
        exception: 异常实例
        
    Returns:
        (gRPC状态码, 状态描述)
    """
    exception_class = exception.__class__
    if exception_class in GRPC_STATUS_MAP:
        status_code, default_message = GRPC_STATUS_MAP[exception_class]
        return status_code, exception.message
    
    # 默认返回内部错误
    return grpc.StatusCode.INTERNAL, exception.message


def create_grpc_context_error(exception: LookServiceBaseError) -> grpc.RpcError:
    """
    创建gRPC上下文错误
    
    Args:
        exception: 异常实例
        
    Returns:
        gRPC错误对象
    """
    status_code, message = get_grpc_status_from_exception(exception)
    context = grpc.StatusCode.to_string(status_code)
    return grpc.RpcError(f"[{context}] {message}", status_code=status_code, details=message) 