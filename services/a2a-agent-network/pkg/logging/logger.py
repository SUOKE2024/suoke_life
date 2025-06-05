#!/usr/bin/env python3
"""
日志记录器模块
Logger Module
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any, Dict

import structlog


def setup_logging(config: Dict[str, Any]) -> None:
    """
    设置日志记录器

    Args:
        config: 日志配置字典
    """
    # 获取配置参数
    level = config.get("level", "INFO").upper()
    log_format = config.get("format", "text")
    log_file = config.get("file")
    max_size = config.get("max_size", "100MB")
    backup_count = config.get("backup_count", 5)
    console_output = config.get("console_output", True)

    # 设置根日志级别
    logging.root.setLevel(getattr(logging, level))

    # 清除现有处理器
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # 配置 structlog
    if log_format.lower() == "json":
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer(colors=console_output),
        ]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # 创建格式化器
    if log_format.lower() == "json":
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": "%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # 控制台处理器
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level))
        console_handler.setFormatter(formatter)
        logging.root.addHandler(console_handler)

    # 文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # 解析文件大小
        max_bytes = _parse_size(max_size)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(getattr(logging, level))
        file_handler.setFormatter(formatter)
        logging.root.addHandler(file_handler)

    # 设置第三方库日志级别
    _configure_third_party_loggers()

    # 记录初始化信息
    logger = logging.getLogger(__name__)
    logger.info(f"日志系统已初始化，级别: {level}, 格式: {log_format}")


def _parse_size(size_str: str) -> int:
    """
    解析文件大小字符串

    Args:
        size_str: 大小字符串，如 "100MB", "1GB"

    Returns:
        字节数
    """
    size_str = size_str.upper().strip()
    
    if size_str.endswith("KB"):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith("MB"):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith("GB"):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        # 默认为字节
        return int(size_str)


def _configure_third_party_loggers() -> None:
    """配置第三方库的日志级别"""
    # 设置第三方库日志级别为 WARNING，减少噪音
    third_party_loggers = [
        "urllib3",
        "requests",
        "aiohttp",
        "grpc",
        "motor",
        "pymongo",
        "flask",
        "werkzeug",
    ]

    for logger_name in third_party_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.BoundLogger:
    """
    获取结构化日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        结构化日志记录器
    """
    return structlog.get_logger(name)


class LoggerMixin:
    """日志记录器混入类"""

    @property
    def logger(self) -> structlog.BoundLogger:
        """获取日志记录器"""
        return get_logger(self.__class__.__name__)


# 预定义的日志记录器
def get_access_logger() -> structlog.BoundLogger:
    """获取访问日志记录器"""
    return get_logger("access")


def get_error_logger() -> structlog.BoundLogger:
    """获取错误日志记录器"""
    return get_logger("error")


def get_performance_logger() -> structlog.BoundLogger:
    """获取性能日志记录器"""
    return get_logger("performance")


def get_security_logger() -> structlog.BoundLogger:
    """获取安全日志记录器"""
    return get_logger("security")


# 日志装饰器
def log_function_call(logger: structlog.BoundLogger = None):
    """
    记录函数调用的装饰器

    Args:
        logger: 日志记录器，如果为 None 则使用默认记录器
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_logger = logger or get_logger(func.__module__)
            func_logger.info(
                "函数调用开始",
                function=func.__name__,
                args=len(args),
                kwargs=list(kwargs.keys()),
            )
            
            try:
                result = func(*args, **kwargs)
                func_logger.info(
                    "函数调用成功",
                    function=func.__name__,
                )
                return result
            except Exception as e:
                func_logger.error(
                    "函数调用失败",
                    function=func.__name__,
                    error=str(e),
                    exc_info=True,
                )
                raise
        
        return wrapper
    return decorator


def log_async_function_call(logger: structlog.BoundLogger = None):
    """
    记录异步函数调用的装饰器

    Args:
        logger: 日志记录器，如果为 None 则使用默认记录器
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            func_logger = logger or get_logger(func.__module__)
            func_logger.info(
                "异步函数调用开始",
                function=func.__name__,
                args=len(args),
                kwargs=list(kwargs.keys()),
            )
            
            try:
                result = await func(*args, **kwargs)
                func_logger.info(
                    "异步函数调用成功",
                    function=func.__name__,
                )
                return result
            except Exception as e:
                func_logger.error(
                    "异步函数调用失败",
                    function=func.__name__,
                    error=str(e),
                    exc_info=True,
                )
                raise
        
        return wrapper
    return decorator


# 上下文管理器
class LogContext:
    """日志上下文管理器"""

    def __init__(self, logger: structlog.BoundLogger, **context):
        """
        初始化日志上下文

        Args:
            logger: 日志记录器
            **context: 上下文信息
        """
        self.logger = logger
        self.context = context
        self.bound_logger = None

    def __enter__(self) -> structlog.BoundLogger:
        """进入上下文"""
        self.bound_logger = self.logger.bind(**self.context)
        return self.bound_logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        if exc_type:
            self.bound_logger.error(
                "上下文执行异常",
                exc_type=exc_type.__name__,
                exc_val=str(exc_val),
                exc_info=True,
            )
        return False


# 性能监控装饰器
import time
from functools import wraps


def log_performance(threshold_seconds: float = 1.0, logger: structlog.BoundLogger = None):
    """
    记录函数执行性能的装饰器

    Args:
        threshold_seconds: 性能阈值（秒），超过此时间会记录警告
        logger: 日志记录器
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_logger = logger or get_performance_logger()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if execution_time > threshold_seconds:
                    func_logger.warning(
                        "函数执行时间超过阈值",
                        function=func.__name__,
                        execution_time=execution_time,
                        threshold=threshold_seconds,
                    )
                else:
                    func_logger.debug(
                        "函数执行完成",
                        function=func.__name__,
                        execution_time=execution_time,
                    )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                func_logger.error(
                    "函数执行异常",
                    function=func.__name__,
                    execution_time=execution_time,
                    error=str(e),
                    exc_info=True,
                )
                raise
        
        return wrapper
    return decorator


def log_async_performance(threshold_seconds: float = 1.0, logger: structlog.BoundLogger = None):
    """
    记录异步函数执行性能的装饰器

    Args:
        threshold_seconds: 性能阈值（秒），超过此时间会记录警告
        logger: 日志记录器
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            func_logger = logger or get_performance_logger()
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if execution_time > threshold_seconds:
                    func_logger.warning(
                        "异步函数执行时间超过阈值",
                        function=func.__name__,
                        execution_time=execution_time,
                        threshold=threshold_seconds,
                    )
                else:
                    func_logger.debug(
                        "异步函数执行完成",
                        function=func.__name__,
                        execution_time=execution_time,
                    )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                func_logger.error(
                    "异步函数执行异常",
                    function=func.__name__,
                    execution_time=execution_time,
                    error=str(e),
                    exc_info=True,
                )
                raise
        
        return wrapper
    return decorator
