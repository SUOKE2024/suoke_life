"""
日志配置模块

提供结构化日志配置和专用日志记录器
"""

import json
import logging
import logging.handlers
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from structlog.typing import FilteringBoundLogger


def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
    log_file: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True,
    enable_colors: bool = True,
    include_caller: bool = True,
    service_name: str = "listen-service",
    service_version: str = "1.0.0",
) -> FilteringBoundLogger:
    """
    设置结构化日志

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: 格式类型 (json, console, plain)
        log_file: 日志文件路径
        max_file_size: 最大文件大小
        backup_count: 备份文件数量
        enable_console: 是否启用控制台输出
        enable_colors: 是否启用彩色输出
        include_caller: 是否包含调用者信息
        service_name: 服务名称
        service_version: 服务版本

    Returns:
        配置好的logger实例
    """

    # 设置日志级别
    log_level = getattr(logging, level.upper(), logging.INFO)

    # 配置structlog处理器
    processors = [
        # 添加时间戳
        structlog.processors.TimeStamper(fmt="iso"),
        # 添加日志级别
        structlog.stdlib.add_log_level,
    ]

    # 添加调用者信息
    if include_caller:
        processors.append(
        structlog.processors.CallsiteParameterAdder(
                parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        )
        )

        # 添加服务元数据
    def add_service_metadata(logger, method_name, event_dict):
        event_dict.update({
            "service": service_name,
            "version": service_version,
        })
        return event_dict

    processors.append(add_service_metadata)

    # 配置输出格式
    if format_type == "json":
        processors.append(structlog.processors.JSONRenderer())
    elif format_type == "console":
        if enable_colors and sys.stderr.isatty():
            processors.append(
                structlog.dev.ConsoleRenderer(
                    colors=True,
                    exception_formatter=structlog.dev.rich_traceback,
                )
            )
        else:
            processors.append(structlog.dev.ConsoleRenderer(colors=False))
    else:  # plain
        processors.append(structlog.processors.KeyValueRenderer())

    # 配置structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # 配置标准库logging
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 添加控制台处理器
    if enable_console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(log_level)

        if format_type == "json":
            console_formatter = JSONFormatter(service_name, service_version)
        else:
            console_formatter = (
                ColoredFormatter() if enable_colors else PlainFormatter()
            )

        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # 添加文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)

        # 文件总是使用JSON格式
        file_formatter = JSONFormatter(service_name, service_version)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # 配置第三方库日志级别
    _configure_third_party_loggers()

    # 获取structlog logger
    logger = structlog.get_logger()

    logger.info(
        "日志系统初始化完成",
        level=level,
        format_type=format_type,
        log_file=log_file,
        enable_console=enable_console,
        enable_colors=enable_colors,
    )

    return logger


def _configure_third_party_loggers() -> None:
    """配置第三方库的日志级别"""
    # 设置第三方库日志级别，避免过多噪音
    third_party_loggers = {
        "urllib3": logging.WARNING,
        "requests": logging.WARNING,
        "grpc": logging.WARNING,
        "asyncio": logging.WARNING,
        "multipart": logging.WARNING,
        "uvicorn": logging.INFO,
        "uvicorn.access": logging.WARNING,
    }

    for logger_name, level in third_party_loggers.items():
        logging.getLogger(logger_name).setLevel(level)


class JSONFormatter(logging.Formatter):
    """JSON格式化器"""

    def __init__(self, service_name: str, service_version: str):
        super().__init__()
        self.service_name = service_name
        self.service_version = service_version

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为JSON"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service_name,
            "version": self.service_version,
        }

        # 添加调用者信息
        if hasattr(record, "filename"):
            log_entry["filename"] = record.filename
        if hasattr(record, "funcName"):
            log_entry["function"] = record.funcName
        if hasattr(record, "lineno"):
            log_entry["line"] = record.lineno

        # 添加异常信息
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """彩色控制台格式化器"""

    # ANSI颜色代码
    COLORS = {
        "DEBUG": "\033[36m",  # 青色
        "INFO": "\033[32m",  # 绿色
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",  # 红色
        "CRITICAL": "\033[35m",  # 紫色
    }
    RESET = "\033[0m"

    def __init__(self) -> None:
        super().__init__(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为彩色输出"""
        # 获取颜色
        color = self.COLORS.get(record.levelname, "")

        # 格式化消息
        formatted = super().format(record)

        # 应用颜色
        if color:
            formatted = f"{color}{formatted}{self.RESET}"

        return formatted


class PlainFormatter(logging.Formatter):
    """纯文本格式化器"""

    def __init__(self) -> None:
        super().__init__(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )


class PerformanceLogger:
    """性能日志记录器"""

    def __init__(self, logger: Optional[FilteringBoundLogger] = None):
        self.logger = logger or structlog.get_logger()
        self.start_times: Dict[str, float] = {}

    def start_operation(self, operation_id: str, operation_name: str, **kwargs) -> None:
        """开始记录操作"""
        self.start_times[operation_id] = time.time()
        self.logger.info(
            "操作开始",
            operation_id=operation_id,
            operation_name=operation_name,
            **kwargs,
        )

    def end_operation(
        self, operation_id: str, operation_name: str, success: bool = True, **kwargs
    ) -> float:
        """结束记录操作"""
        start_time = self.start_times.pop(operation_id, time.time())
        duration = time.time() - start_time

        log_method = self.logger.info if success else self.logger.error
        log_method(
            "操作完成",
            operation_id=operation_id,
            operation_name=operation_name,
            duration=duration,
            success=success,
            **kwargs,
        )

        return duration

    def log_metric(self, metric_name: str, value: float, **kwargs) -> None:
        """记录指标"""
        self.logger.info(
            "性能指标", metric_name=metric_name, metric_value=value, **kwargs
        )


def get_logger(name: Optional[str] = None) -> FilteringBoundLogger:
    """获取logger实例"""
    return structlog.get_logger(name)


def log_function_call(
    logger: Optional[FilteringBoundLogger] = None,
    include_args: bool = False,
    include_result: bool = False,
):
    """函数调用日志装饰器"""
    def decorator(func):
        nonlocal logger
        if logger is None:
            logger = get_logger()

        def wrapper(*args, **kwargs):
            func_name = func.__name__
            log_data = {"function": func_name}
            
            if include_args:
                log_data.update({
                    "args": str(args),
                    "kwargs": str(kwargs)
                })

            logger.debug("函数调用开始", **log_data)

            try:
                result = func(*args, **kwargs)
                if include_result:
                    log_data["result"] = str(result)
                logger.debug("函数调用完成", **log_data)
                return result
            except Exception as e:
                log_data["error"] = str(e)
                logger.error("函数调用失败", **log_data)
                raise

        return wrapper
    return decorator