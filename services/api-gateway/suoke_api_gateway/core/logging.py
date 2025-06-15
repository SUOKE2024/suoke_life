#!/usr/bin/env python3
"""
索克生活 API 网关日志配置

提供结构化日志记录和配置管理。
"""

from .config import get_settings, Settings
from pathlib import Path
from typing import Any, Dict, Optional
import logging
import logging.config
import structlog
import sys
import time
from datetime import datetime


def setup_logging(settings: Optional[Settings] = None) -> None:
    """设置日志配置"""
    if settings is None:
        settings = get_settings()

    # 配置标准库日志
    logging.basicConfig(
        level=logging.INFO if not settings.debug else logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )

    # 配置structlog
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
            structlog.processors.JSONRenderer() if not settings.debug else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """获取结构化日志记录器"""
    return structlog.get_logger(name)


def log_request_response(
    method: str,
    url: str,
    status_code: int,
    response_time: float,
    request_size: int = 0,
    response_size: int = 0,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    client_ip: Optional[str] = None,
) -> None:
    """记录请求响应日志"""
    logger = get_logger("gateway.request")
    
    logger.info(
        "Request completed",
        method=method,
        url=url,
        status_code=status_code,
        response_time=response_time,
        request_size=request_size,
        response_size=response_size,
        user_id=user_id,
        request_id=request_id,
        client_ip=client_ip,
    )


def log_security_event(
    event_type: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    path: Optional[str] = None,
    method: Optional[str] = None,
    **kwargs: Any
) -> None:
    """记录安全事件日志"""
    logger = get_logger("gateway.security")
    
    logger.warning(
        "Security event",
        event_type=event_type,
        user_id=user_id,
        ip_address=ip_address,
        path=path,
        method=method,
        timestamp=datetime.utcnow().isoformat(),
        **kwargs
    )


def log_performance_metric(
    metric_name: str,
    value: float,
    unit: str = "ms",
    tags: Optional[Dict[str, str]] = None,
) -> None:
    """记录性能指标日志"""
    logger = get_logger("gateway.performance")
    
    logger.info(
        "Performance metric",
        metric_name=metric_name,
        value=value,
        unit=unit,
        tags=tags or {},
        timestamp=time.time(),
    )


def log_service_event(
    service_name: str,
    event_type: str,
    instance_id: Optional[str] = None,
    **kwargs: Any
) -> None:
    """记录服务事件日志"""
    logger = get_logger("gateway.service")
    
    logger.info(
        "Service event",
        service_name=service_name,
        event_type=event_type,
        instance_id=instance_id,
        timestamp=datetime.utcnow().isoformat(),
        **kwargs
    )


def log_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    logger_name: str = "gateway.error"
) -> None:
    """记录错误日志"""
    logger = get_logger(logger_name)
    
    logger.error(
        "Error occurred",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {},
        timestamp=datetime.utcnow().isoformat(),
        exc_info=True
    )


# 全局日志设置标志
_logging_configured = False


def ensure_logging_configured() -> None:
    """确保日志已配置"""
    global _logging_configured
    
    if not _logging_configured:
        setup_logging()
        _logging_configured = True


# 自动配置日志
ensure_logging_configured()