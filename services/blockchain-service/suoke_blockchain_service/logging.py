"""
结构化日志模块

使用 structlog 提供结构化日志记录功能。
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

from .config import settings


def configure_logging() -> None:
    """配置结构化日志"""

    # 配置标准库日志
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.monitoring.log_level.upper()),
    )

    # 配置 structlog
    processors: list[Any] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.monitoring.log_format == "json":
        # JSON 格式输出(生产环境)
        processors.append(structlog.processors.JSONRenderer())
    else:
        # 彩色控制台输出(开发环境)
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True),
        ])

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """获取结构化日志记录器"""
    return structlog.get_logger(name)


class LoggerMixin:
    """日志记录器混入类"""

    @property
    def logger(self) -> Any:
        """获取当前类的日志记录器"""
        return get_logger(self.__class__.__name__)


# 预配置的日志记录器
logger = get_logger("blockchain_service")
grpc_logger = get_logger("grpc")
blockchain_logger = get_logger("blockchain")
database_logger = get_logger("database")
security_logger = get_logger("security")
