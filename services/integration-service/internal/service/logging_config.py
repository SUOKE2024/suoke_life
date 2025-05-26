"""
Logging Configuration
"""

import logging
import logging.handlers
import sys
from pathlib import Path
import structlog
from typing import Any, Dict


def setup_logging(log_level: str = "INFO"):
    """设置日志配置"""
    
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
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # 配置标准库logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=getattr(logging, log_level.upper()),
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 设置第三方库日志级别
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


class StructuredLogger:
    """结构化日志器"""
    
    def __init__(self, name: str):
        self.logger = structlog.get_logger(name)
    
    def info(self, message: str, **kwargs):
        """信息日志"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """警告日志"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """错误日志"""
        self.logger.error(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """调试日志"""
        self.logger.debug(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """严重错误日志"""
        self.logger.critical(message, **kwargs)
    
    def bind(self, **kwargs) -> "StructuredLogger":
        """绑定上下文"""
        new_logger = StructuredLogger(self.logger.name)
        new_logger.logger = self.logger.bind(**kwargs)
        return new_logger


def get_logger(name: str) -> StructuredLogger:
    """获取结构化日志器"""
    return StructuredLogger(name)


class LoggerMixin:
    """日志混入类"""
    
    @property
    def logger(self) -> StructuredLogger:
        """获取日志器"""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger 