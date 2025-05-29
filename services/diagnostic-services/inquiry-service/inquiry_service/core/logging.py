"""
日志配置模块

使用 Loguru 和 Structlog 提供结构化日志记录功能。
"""

from pathlib import Path
import sys
from typing import Any

from loguru import logger
import structlog

from inquiry_service.core.config import LoggingSettings


def setup_logging(
    settings: LoggingSettings | None = None,
    log_dir: Path | None = None,
) -> None:
    """
    设置日志配置

    Args:
        settings: 日志配置
        log_dir: 日志目录
    """
    if settings is None:
        from inquiry_service.core.config import get_settings

        settings = get_settings().logging

    if log_dir is None:
        log_dir = Path("logs")

    # 确保日志目录存在
    log_dir.mkdir(exist_ok=True)

    # 移除默认的 loguru 处理器
    logger.remove()

    # 添加控制台处理器
    logger.add(
        sys.stderr,
        format=settings.format,
        level=settings.level,
        colorize=True,
        serialize=settings.serialize,
    )

    # 添加文件处理器
    logger.add(
        log_dir / "inquiry_service.log",
        format=settings.format,
        level=settings.level,
        rotation=settings.rotation,
        retention=settings.retention,
        compression=settings.compression,
        serialize=settings.serialize,
        encoding="utf-8",
    )

    # 添加错误日志文件处理器
    logger.add(
        log_dir / "error.log",
        format=settings.format,
        level="ERROR",
        rotation=settings.rotation,
        retention=settings.retention,
        compression=settings.compression,
        serialize=settings.serialize,
        encoding="utf-8",
    )

    # 配置 structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
            if settings.serialize
            else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """
    获取结构化日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        结构化日志记录器
    """
    return structlog.get_logger(name)


def log_function_call(func_name: str, **kwargs: Any) -> None:
    """
    记录函数调用日志

    Args:
        func_name: 函数名称
        **kwargs: 函数参数
    """
    logger.debug(f"Calling function: {func_name}", **kwargs)


def log_performance(operation: str, duration: float, **context: Any) -> None:
    """
    记录性能日志

    Args:
        operation: 操作名称
        duration: 执行时间（秒）
        **context: 上下文信息
    """
    logger.info(f"Performance: {operation}", duration=duration, **context)


def log_error(error: Exception, operation: str, **context: Any) -> None:
    """
    记录错误日志

    Args:
        error: 异常对象
        operation: 操作名称
        **context: 上下文信息
    """
    logger.error(
        f"Error in {operation}: {error!s}",
        error_type=type(error).__name__,
        error_message=str(error),
        **context,
        exc_info=True,
    )


def log_api_request(
    method: str, path: str, status_code: int, duration: float, **context: Any
) -> None:
    """
    记录API请求日志

    Args:
        method: HTTP方法
        path: 请求路径
        status_code: 状态码
        duration: 请求时间（秒）
        **context: 上下文信息
    """
    logger.info(
        f"API Request: {method} {path}",
        method=method,
        path=path,
        status_code=status_code,
        duration=duration,
        **context,
    )


def log_grpc_request(
    service: str, method: str, status: str, duration: float, **context: Any
) -> None:
    """
    记录gRPC请求日志

    Args:
        service: 服务名称
        method: 方法名称
        status: 状态
        duration: 请求时间（秒）
        **context: 上下文信息
    """
    logger.info(
        f"gRPC Request: {service}.{method}",
        service=service,
        method=method,
        status=status,
        duration=duration,
        **context,
    )


def log_database_operation(
    operation: str, table: str, duration: float, **context: Any
) -> None:
    """
    记录数据库操作日志

    Args:
        operation: 操作类型
        table: 表名
        duration: 执行时间（秒）
        **context: 上下文信息
    """
    logger.debug(
        f"Database {operation}: {table}",
        operation=operation,
        table=table,
        duration=duration,
        **context,
    )


def log_cache_operation(
    operation: str, key: str, hit: bool | None = None, **context: Any
) -> None:
    """
    记录缓存操作日志

    Args:
        operation: 操作类型
        key: 缓存键
        hit: 是否命中（仅对读操作有效）
        **context: 上下文信息
    """
    logger.debug(
        f"Cache {operation}: {key}", operation=operation, key=key, hit=hit, **context
    )


def log_ai_request(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    duration: float,
    **context: Any,
) -> None:
    """
    记录AI请求日志

    Args:
        model: 模型名称
        prompt_tokens: 提示词token数
        completion_tokens: 完成token数
        duration: 请求时间（秒）
        **context: 上下文信息
    """
    logger.info(
        f"AI Request: {model}",
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        duration=duration,
        **context,
    )


class LoggerMixin:
    """日志记录器混入类"""

    @property
    def logger(self) -> Any:
        """获取类专用的日志记录器"""
        return get_logger(self.__class__.__name__)

    def log_info(self, message: str, **kwargs: Any) -> None:
        """记录信息日志"""
        self.logger.info(message, **kwargs)

    def log_debug(self, message: str, **kwargs: Any) -> None:
        """记录调试日志"""
        self.logger.debug(message, **kwargs)

    def log_warning(self, message: str, **kwargs: Any) -> None:
        """记录警告日志"""
        self.logger.warning(message, **kwargs)

    def log_error(
        self, message: str, error: Exception | None = None, **kwargs: Any
    ) -> None:
        """记录错误日志"""
        if error:
            self.logger.error(
                message, error=str(error), error_type=type(error).__name__, **kwargs
            )
        else:
            self.logger.error(message, **kwargs)
