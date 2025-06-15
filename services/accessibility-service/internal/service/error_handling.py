#!/usr/bin/env python3
"""
统一错误处理模块
提供标准化的错误处理、日志记录和恢复机制
"""

import logging
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """错误严重程度"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """错误类别"""

    CONFIGURATION = "configuration"
    NETWORK = "network"
    MODEL_LOADING = "model_loading"
    DATA_PROCESSING = "data_processing"
    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    RESOURCE = "resource"
    VALIDATION = "validation"
    EXTERNAL_SERVICE = "external_service"
    UNKNOWN = "unknown"


@dataclass
class ErrorInfo:
    """错误信息"""

    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: str | None = None
    timestamp: float = None
    context: dict[str, Any] | None = None
    traceback_info: str | None = None
    recovery_suggestion: str | None = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = time.time()


class AccessibilityServiceError(Exception):
    """无障碍服务基础异常"""

    def __init__(self, error_info: ErrorInfo):
        self.error_info = error_info
        super().__init__(error_info.message)


class ConfigurationError(AccessibilityServiceError):
    """配置错误"""

    pass


class ModelLoadingError(AccessibilityServiceError):
    """模型加载错误"""

    pass


class DataProcessingError(AccessibilityServiceError):
    """数据处理错误"""

    pass


class NetworkError(AccessibilityServiceError):
    """网络错误"""

    pass


class ResourceError(AccessibilityServiceError):
    """资源错误"""

    pass


class ErrorHandler:
    """统一错误处理器"""

    def __init__(self) -> None:
        self.error_count = {}
        self.error_history = []
        self.max_history = 1000

    def handle_error(
        self,
        error: Exception,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: dict[str, Any] | None = None,
        recovery_suggestion: str | None = None,
    ) -> ErrorInfo:
        """
        处理错误

        Args:
            error: 异常对象
            category: 错误类别
            severity: 错误严重程度
            context: 错误上下文
            recovery_suggestion: 恢复建议

        Returns:
            ErrorInfo: 错误信息对象
        """
        error_id = f"{category.value}_{int(time.time())}_{id(error)}"

        error_info = ErrorInfo(
            error_id=error_id,
            category=category,
            severity=severity,
            message=str(error),
            details=getattr(error, "details", None),
            context=context or {},
            traceback_info=traceback.format_exc(),
            recovery_suggestion=recovery_suggestion,
        )

        # 记录错误
        self._log_error(error_info)

        # 更新错误统计
        self._update_error_stats(category, severity)

        # 添加到历史记录
        self._add_to_history(error_info)

        # 根据严重程度采取行动
        self._handle_by_severity(error_info)

        return error_info

    def _log_error(self, error_info: ErrorInfo):
        """记录错误日志"""
        log_message = (
            f"[{error_info.error_id}] {error_info.category.value.upper()}: "
            f"{error_info.message}"
        )

        if error_info.context:
            log_message += f" | Context: {error_info.context}"

        if error_info.recovery_suggestion:
            log_message += f" | Recovery: {error_info.recovery_suggestion}"

        if error_info.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
            if error_info.traceback_info:
                logger.critical(f"Traceback: {error_info.traceback_info}")
        elif error_info.severity == ErrorSeverity.HIGH:
            logger.error(log_message)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)

    def _update_error_stats(self, category: ErrorCategory, severity: ErrorSeverity):
        """更新错误统计"""
        key = f"{category.value}_{severity.value}"
        self.error_count[key] = self.error_count.get(key, 0) + 1

    def _add_to_history(self, error_info: ErrorInfo):
        """添加到错误历史"""
        self.error_history.append(error_info)

        # 保持历史记录大小
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history :]

    def _handle_by_severity(self, error_info: ErrorInfo):
        """根据严重程度处理错误"""
        if error_info.severity == ErrorSeverity.CRITICAL:
            # 关键错误：记录详细信息，可能需要服务重启
            logger.critical(f"CRITICAL ERROR: {error_info.error_id}")
            # 这里可以添加告警机制

        elif error_info.severity == ErrorSeverity.HIGH:
            # 高级错误：需要立即关注
            logger.error(f"HIGH SEVERITY ERROR: {error_info.error_id}")

        # 中低级错误已在日志中记录

    def get_error_stats(self) -> dict[str, Any]:
        """获取错误统计"""
        return {
            "total_errors": sum(self.error_count.values()),
            "error_by_category": self.error_count.copy(),
            "recent_errors": len(
                [
                    e
                    for e in self.error_history
                    if time.time() - e.timestamp < 3600  # 最近1小时
                ]
            ),
        }

    def get_recent_errors(self, limit: int = 10) -> list[ErrorInfo]:
        """获取最近的错误"""
        return sorted(self.error_history, key=lambda x: x.timestamp, reverse=True)[
            :limit
        ]


# 全局错误处理器实例
global_error_handler = ErrorHandler()


def error_handler(
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    recovery_suggestion: str | None = None,
    reraise: bool = False,
):
    """
    错误处理装饰器

    Args:
        category: 错误类别
        severity: 错误严重程度
        recovery_suggestion: 恢复建议
        reraise: 是否重新抛出异常
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    "function": func.__name__,
                    "args": str(args)[:200],  # 限制长度
                    "kwargs": str(kwargs)[:200],
                }

                error_info = global_error_handler.handle_error(
                    error=e,
                    category=category,
                    severity=severity,
                    context=context,
                    recovery_suggestion=recovery_suggestion,
                )

                if reraise:
                    raise AccessibilityServiceError(error_info) from e

                # 返回默认值或None
                return None

        return wrapper

    return decorator


def async_error_handler(
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    recovery_suggestion: str | None = None,
    reraise: bool = False,
):
    """
    异步错误处理装饰器
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = {
                    "function": func.__name__,
                    "args": str(args)[:200],
                    "kwargs": str(kwargs)[:200],
                }

                error_info = global_error_handler.handle_error(
                    error=e,
                    category=category,
                    severity=severity,
                    context=context,
                    recovery_suggestion=recovery_suggestion,
                )

                if reraise:
                    raise AccessibilityServiceError(error_info) from e

                return None

        return wrapper

    return decorator


def create_error_info(
    category: ErrorCategory,
    severity: ErrorSeverity,
    message: str,
    details: str | None = None,
    context: dict[str, Any] | None = None,
    recovery_suggestion: str | None = None,
) -> ErrorInfo:
    """
    创建错误信息对象

    Args:
        category: 错误类别
        severity: 错误严重程度
        message: 错误消息
        details: 错误详情
        context: 错误上下文
        recovery_suggestion: 恢复建议

    Returns:
        ErrorInfo: 错误信息对象
    """
    error_id = f"{category.value}_{int(time.time())}"

    return ErrorInfo(
        error_id=error_id,
        category=category,
        severity=severity,
        message=message,
        details=details,
        context=context or {},
        recovery_suggestion=recovery_suggestion,
    )


def log_error_info(error_info: ErrorInfo):
    """记录错误信息"""
    global_error_handler._log_error(error_info)
    global_error_handler._add_to_history(error_info)


# 常用的错误处理函数
def handle_configuration_error(error: Exception, config_key: str = None):
    """处理配置错误"""
    context = {"config_key": config_key} if config_key else {}
    return global_error_handler.handle_error(
        error=error,
        category=ErrorCategory.CONFIGURATION,
        severity=ErrorSeverity.HIGH,
        context=context,
        recovery_suggestion="检查配置文件格式和必需的配置项",
    )


def handle_model_loading_error(error: Exception, model_name: str = None):
    """处理模型加载错误"""
    context = {"model_name": model_name} if model_name else {}
    return global_error_handler.handle_error(
        error=error,
        category=ErrorCategory.MODEL_LOADING,
        severity=ErrorSeverity.HIGH,
        context=context,
        recovery_suggestion="检查模型文件路径和依赖库是否正确安装",
    )


def handle_network_error(error: Exception, endpoint: str = None):
    """处理网络错误"""
    context = {"endpoint": endpoint} if endpoint else {}
    return global_error_handler.handle_error(
        error=error,
        category=ErrorCategory.NETWORK,
        severity=ErrorSeverity.MEDIUM,
        context=context,
        recovery_suggestion="检查网络连接和服务端点可用性",
    )


def handle_data_processing_error(error: Exception, data_type: str = None):
    """处理数据处理错误"""
    context = {"data_type": data_type} if data_type else {}
    return global_error_handler.handle_error(
        error=error,
        category=ErrorCategory.DATA_PROCESSING,
        severity=ErrorSeverity.MEDIUM,
        context=context,
        recovery_suggestion="检查输入数据格式和处理逻辑",
    )
