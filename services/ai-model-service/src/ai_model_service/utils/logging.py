"""日志配置工具"""

import logging
import sys
from typing import Any, Optional

import structlog
from structlog.stdlib import LoggerFactory


def setup_logging(
    level: str = "INFO",
    json_logs: bool = False,
    service_name: str = "ai-model-service",
    service_version: str = "unknown",
) -> None:
    """设置结构化日志

    Args:
        level: 日志级别
        json_logs: 是否使用JSON格式
        service_name: 服务名称
        service_version: 服务版本
    """
    # 设置日志级别
    log_level = getattr(logging, level.upper(), logging.INFO)

    # 配置标准库日志
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # 配置structlog处理器
    processors = [
        # 添加服务信息
        structlog.processors.add_log_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # 添加服务元数据
    def add_service_info(logger: Any, method_name: str, event_dict: dict) -> dict:
        event_dict["service"] = service_name
        event_dict["version"] = service_version
        return event_dict

    processors.insert(0, add_service_info)

    if json_logs:
        # JSON格式输出
        processors.append(structlog.processors.JSONRenderer())
    else:
        # 开发友好的格式
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=True, exception_formatter=structlog.dev.plain_traceback
            )
        )

    # 配置structlog
    structlog.configure(
        processors=processors,  # type: ignore
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # 配置第三方库的日志级别
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(log_level)
    logging.getLogger("kubernetes").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: Optional[str] = None) -> Any:
    """获取结构化日志器

    Args:
        name: 日志器名称

    Returns:
        结构化日志器
    """
    return structlog.get_logger(name)
