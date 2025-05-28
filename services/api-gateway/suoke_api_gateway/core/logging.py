"""
日志配置模块

使用 structlog 提供结构化日志记录，支持 JSON 格式输出，
便于日志聚合和分析。
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from rich.console import Console
from rich.logging import RichHandler

from .config import Settings


def setup_logging(settings: Optional[Settings] = None) -> None:
    """设置日志配置"""
    if settings is None:
        from .config import get_settings
        settings = get_settings()
    
    # 配置标准库日志
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": settings.log_format,
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "rich.logging.RichHandler",
                "level": settings.log_level,
                "formatter": "standard",
                "show_time": True,
                "show_path": True,
                "rich_tracebacks": True,
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console"],
                "level": settings.log_level,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "fastapi": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "grpc": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
    
    # 如果指定了日志文件，添加文件处理器
    if settings.log_file:
        log_file_path = Path(settings.log_file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        logging_config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": settings.log_level,
            "formatter": "json" if settings.is_production() else "standard",
            "filename": str(log_file_path),
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
            "encoding": "utf-8",
        }
        
        # 为所有日志器添加文件处理器
        for logger_name in logging_config["loggers"]:
            logging_config["loggers"][logger_name]["handlers"].append("file")
    
    # 应用日志配置
    logging.config.dictConfig(logging_config)
    
    # 配置 structlog
    configure_structlog(settings)


def configure_structlog(settings: Settings) -> None:
    """配置 structlog"""
    
    # 选择处理器
    if settings.is_production():
        # 生产环境使用 JSON 格式
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
        # 开发环境使用彩色输出
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """获取结构化日志器"""
    return structlog.get_logger(name)


class LoggerMixin:
    """日志器混入类"""
    
    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """获取当前类的日志器"""
        return get_logger(self.__class__.__name__)


def log_request_response(
    method: str,
    url: str,
    status_code: int,
    response_time: float,
    request_size: int = 0,
    response_size: int = 0,
    user_id: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """记录请求响应日志"""
    logger = get_logger("api.access")
    
    logger.info(
        "API request processed",
        method=method,
        url=url,
        status_code=status_code,
        response_time_ms=round(response_time * 1000, 2),
        request_size_bytes=request_size,
        response_size_bytes=response_size,
        user_id=user_id,
        **kwargs,
    )


def log_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> None:
    """记录错误日志"""
    logger = get_logger("api.error")
    
    error_context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        **(context or {}),
        **kwargs,
    }
    
    logger.error(
        "An error occurred",
        **error_context,
        exc_info=True,
    )


def log_performance(
    operation: str,
    duration: float,
    **kwargs: Any,
) -> None:
    """记录性能日志"""
    logger = get_logger("api.performance")
    
    logger.info(
        "Performance metric",
        operation=operation,
        duration_ms=round(duration * 1000, 2),
        **kwargs,
    )


def log_security_event(
    event_type: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """记录安全事件日志"""
    logger = get_logger("api.security")
    
    logger.warning(
        "Security event",
        event_type=event_type,
        user_id=user_id,
        ip_address=ip_address,
        **kwargs,
    ) 