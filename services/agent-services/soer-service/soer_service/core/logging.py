"""
日志配置模块

提供结构化日志配置和管理
"""

import logging
import logging.handlers
import os
import sys
from typing import Any

import structlog
from pythonjsonlogger.jsonlogger import JsonFormatter

from ..config.settings import get_settings


def setup_logging() -> None:
    """设置日志配置"""
    settings = get_settings()
    
    # 配置基础日志级别
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # 清除现有的处理器
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    
    if settings.environment == "production":
        # 生产环境使用 JSON 格式
        json_formatter = JsonFormatter(
            fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
        )
        console_handler.setFormatter(json_formatter)
    else:
        # 开发环境使用彩色格式
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)-20s - %(levelname)-8s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
    
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了日志目录）
    if hasattr(settings, 'log_file') and settings.log_file:
        log_dir = os.path.dirname(settings.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            settings.log_file,
            maxBytes=100 * 1024 * 1024,  # 100MB
            backupCount=5,
            encoding='utf-8'
        )
        
        # 文件日志使用 JSON 格式
        json_formatter = JsonFormatter(
            fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
        )
        file_handler.setFormatter(json_formatter)
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)
    
    # 设置根日志级别
    root_logger.setLevel(log_level)
    
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
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # 静默一些第三方库的日志
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"📋 日志系统初始化完成 (级别: {settings.log_level})")


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """获取结构化日志记录器"""
    return structlog.get_logger(name)


class LoggingMiddleware:
    """日志中间件"""
    
    def __init__(self, app):
        self.app = app
        self.logger = get_logger(__name__)
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # 记录请求开始
            self.logger.info(
                "Request started",
                method=scope["method"],
                path=scope["path"],
                query_string=scope.get("query_string", b"").decode(),
            )
        
        await self.app(scope, receive, send)


# 获取默认日志记录器的便捷函数
def get_default_logger() -> logging.Logger:
    """获取默认的 Python 日志记录器"""
    return logging.getLogger("soer_service")