"""
索克生活项目 - 统一异常处理框架
定义项目级别的异常类和处理机制
"""

import logging
import sys
import traceback
from enum import Enum
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """错误严重性级别"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SuokeBaseException(Exception):
    """索克生活项目基础异常类"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.context = context or {}

        # 自动记录异常
        self._log_exception()

    def _log_exception(self):
        """记录异常信息"""
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL,
        }.get(self.severity, logging.ERROR)

        logger.log(
            log_level,
            f"[{self.error_code or 'UNKNOWN'}] {self.message}",
            extra={
                "error_code": self.error_code,
                "severity": self.severity.value,
                "context": self.context,
            },
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "severity": self.severity.value,
            "context": self.context,
            "type": self.__class__.__name__,
        }


# 业务异常类
class AgentException(SuokeBaseException):
    """智能体相关异常"""

    pass


class ServiceException(SuokeBaseException):
    """服务相关异常"""

    pass


class DataException(SuokeBaseException):
    """数据相关异常"""

    pass


class AuthenticationException(SuokeBaseException):
    """认证相关异常"""

    pass


class AuthorizationException(SuokeBaseException):
    """授权相关异常"""

    pass


class ValidationException(SuokeBaseException):
    """验证相关异常"""

    pass


class ConfigurationException(SuokeBaseException):
    """配置相关异常"""

    pass


class NetworkException(SuokeBaseException):
    """网络相关异常"""

    pass


class DatabaseException(SuokeBaseException):
    """数据库相关异常"""

    pass


class AIModelException(SuokeBaseException):
    """AI模型相关异常"""

    pass


# 异常处理装饰器
def handle_exceptions(
    default_return=None,
    log_errors=True,
    reraise=False,
    exception_mapping: Optional[Dict[type, type]] = None,
):
    """
    统一异常处理装饰器

    Args:
        default_return: 异常时的默认返回值
        log_errors: 是否记录错误日志
        reraise: 是否重新抛出异常
        exception_mapping: 异常类型映射
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(
                        f"Exception in {func.__name__}: {str(e)}", exc_info=True
                    )

                # 异常类型转换
                if exception_mapping and type(e) in exception_mapping:
                    mapped_exception = exception_mapping[type(e)]
                    raise mapped_exception(
                        f"Error in {func.__name__}: {str(e)}",
                        error_code=f"{func.__module__}.{func.__name__}",
                        context={"original_exception": str(e)},
                    )

                if reraise:
                    raise

                return default_return

        return wrapper

    return decorator


# 异常处理上下文管理器
class ExceptionContext:
    """异常处理上下文管理器"""

    def __init__(
        self,
        operation_name: str,
        suppress_exceptions: bool = False,
        default_return=None,
    ):
        self.operation_name = operation_name
        self.suppress_exceptions = suppress_exceptions
        self.default_return = default_return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error(
                f"Exception in {self.operation_name}: {exc_val}", exc_info=True
            )

            if self.suppress_exceptions:
                return True  # 抑制异常

        return False


# 全局异常处理器
class GlobalExceptionHandler:
    """全局异常处理器"""

    @staticmethod
    def setup_global_handler():
        """设置全局异常处理器"""

        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            logger.critical(
                "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
            )

        sys.excepthook = handle_exception

    @staticmethod
    def handle_async_exception(loop, context):
        """处理异步异常"""
        exception = context.get("exception")
        if exception:
            logger.error(f"Async exception: {exception}", exc_info=exception)
        else:
            logger.error(f"Async error: {context['message']}")


# 异常恢复策略
class RecoveryStrategy:
    """异常恢复策略"""

    @staticmethod
    def retry_with_backoff(
        func,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        exceptions: Tuple[type, ...] = (Exception,),
    ):
        """带退避的重试策略"""
        import time

        for attempt in range(max_retries + 1):
            try:
                return func()
            except exceptions as e:
                if attempt == max_retries:
                    raise

                wait_time = backoff_factor * (2**attempt)
                logger.warning(
                    f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}"
                )
                time.sleep(wait_time)

    @staticmethod
    def circuit_breaker(failure_threshold: int = 5, recovery_timeout: int = 60):
        """断路器模式"""

        def decorator(func):
            func._failures = 0
            func._last_failure_time = 0
            func._state = "closed"  # closed, open, half-open

            def wrapper(*args, **kwargs):
                import time

                current_time = time.time()

                # 检查是否可以从开路状态恢复
                if (
                    func._state == "open"
                    and current_time - func._last_failure_time > recovery_timeout
                ):
                    func._state = "half-open"

                # 开路状态直接抛出异常
                if func._state == "open":
                    raise ServiceException(
                        "Circuit breaker is open", error_code="CIRCUIT_BREAKER_OPEN"
                    )

                try:
                    result = func(*args, **kwargs)
                    # 成功时重置计数器
                    if func._state == "half-open":
                        func._state = "closed"
                        func._failures = 0
                    return result
                except Exception as e:
                    func._failures += 1
                    func._last_failure_time = current_time

                    if func._failures >= failure_threshold:
                        func._state = "open"

                    raise

            return wrapper

        return decorator
