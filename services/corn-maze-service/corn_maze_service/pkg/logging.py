"""
结构化日志配置

使用 structlog 提供结构化日志记录功能。
"""

import logging
from typing import Any

import structlog
from structlog.types import EventDict, Processor

from corn_maze_service.config import get_settings

def add_correlation_id(_logger: Any, _method_name: str, event_dict: EventDict) -> EventDict:
    """添加关联ID到日志事件"""
    # 这里可以从上下文中获取请求ID或追踪ID
    # event_dict["correlation_id"] = get_correlation_id()
    return event_dict

def add_service_info(_logger: Any, _method_name: str, event_dict: EventDict) -> EventDict:
    """添加服务信息到日志事件"""
    settings = get_settings()
    event_dict["service"] = settings.app_name
    event_dict["version"] = settings.app_version
    event_dict["environment"] = settings.environment
    return event_dict

def setup_logging() -> None:
    """设置结构化日志"""
    settings = get_settings()

    # 配置标准库日志
    logging.config.dictConfig(settings.get_log_config())

    # 配置 structlog
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        add_service_info,
        add_correlation_id,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.is_development():
        # 开发环境使用彩色输出
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True)
        ])
    else:
        # 生产环境使用JSON格式
        processors.extend([
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ])

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLogger().level
        ),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )

def get_logger(name: str) -> Any:
    """获取结构化日志记录器"""
    return structlog.get_logger(name)
