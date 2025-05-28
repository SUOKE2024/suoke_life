"""
日志配置模块

提供结构化日志、多种输出格式和性能优化的日志系统
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union

import structlog
from loguru import logger as loguru_logger

from .config import LoggingConfig, get_settings


def setup_logging(config: Optional[LoggingConfig] = None) -> None:
    """设置日志系统"""
    if config is None:
        settings = get_settings()
        config = settings.logging
    
    # 移除默认的 loguru 处理器
    loguru_logger.remove()
    
    # 设置日志格式
    if config.structured:
        if config.json_format:
            format_string = _get_json_format()
        else:
            format_string = _get_structured_format()
    else:
        format_string = config.format
    
    # 添加控制台处理器
    loguru_logger.add(
        sys.stderr,
        format=format_string,
        level=config.level,
        colorize=not config.json_format,
        serialize=config.json_format,
    )
    
    # 添加文件处理器（如果配置了文件路径）
    if config.file_path:
        file_path = Path(config.file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        loguru_logger.add(
            str(file_path),
            format=format_string,
            level=config.level,
            rotation=config.rotation,
            retention=config.retention,
            compression=config.compression,
            serialize=config.json_format,
        )
    
    # 配置 structlog
    if config.structured:
        _setup_structlog(config)


def _get_json_format() -> str:
    """获取 JSON 格式的日志格式"""
    return "{message}"


def _get_structured_format() -> str:
    """获取结构化格式的日志格式"""
    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )


def _setup_structlog(config: LoggingConfig) -> None:
    """设置 structlog"""
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if config.json_format:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


class StructuredLogger:
    """结构化日志器"""
    
    def __init__(self, name: str) -> None:
        self.name = name
        self._logger = structlog.get_logger(name)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """记录调试信息"""
        self._logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """记录信息"""
        self._logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """记录警告"""
        self._logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs: Any) -> None:
        """记录错误"""
        self._logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs: Any) -> None:
        """记录严重错误"""
        self._logger.critical(message, **kwargs)
    
    def exception(self, message: str, **kwargs: Any) -> None:
        """记录异常"""
        self._logger.exception(message, **kwargs)
    
    def bind(self, **kwargs: Any) -> "StructuredLogger":
        """绑定上下文信息"""
        new_logger = StructuredLogger(self.name)
        new_logger._logger = self._logger.bind(**kwargs)
        return new_logger


class LoggerAdapter:
    """日志适配器，统一 loguru 和 structlog 接口"""
    
    def __init__(self, name: str, use_structured: bool = True) -> None:
        self.name = name
        self.use_structured = use_structured
        
        if use_structured:
            self._logger = StructuredLogger(name)
        else:
            self._logger = loguru_logger.bind(name=name)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """记录调试信息"""
        if self.use_structured:
            self._logger.debug(message, **kwargs)
        else:
            self._logger.debug(f"[{self.name}] {message}", **kwargs)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """记录信息"""
        if self.use_structured:
            self._logger.info(message, **kwargs)
        else:
            self._logger.info(f"[{self.name}] {message}", **kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """记录警告"""
        if self.use_structured:
            self._logger.warning(message, **kwargs)
        else:
            self._logger.warning(f"[{self.name}] {message}", **kwargs)
    
    def error(self, message: str, **kwargs: Any) -> None:
        """记录错误"""
        if self.use_structured:
            self._logger.error(message, **kwargs)
        else:
            self._logger.error(f"[{self.name}] {message}", **kwargs)
    
    def critical(self, message: str, **kwargs: Any) -> None:
        """记录严重错误"""
        if self.use_structured:
            self._logger.critical(message, **kwargs)
        else:
            self._logger.critical(f"[{self.name}] {message}", **kwargs)
    
    def exception(self, message: str, **kwargs: Any) -> None:
        """记录异常"""
        if self.use_structured:
            self._logger.exception(message, **kwargs)
        else:
            self._logger.exception(f"[{self.name}] {message}", **kwargs)
    
    def bind(self, **kwargs: Any) -> "LoggerAdapter":
        """绑定上下文信息"""
        if self.use_structured:
            new_adapter = LoggerAdapter(self.name, self.use_structured)
            new_adapter._logger = self._logger.bind(**kwargs)
            return new_adapter
        else:
            return LoggerAdapter(self.name, self.use_structured)


def get_logger(name: str, use_structured: Optional[bool] = None) -> LoggerAdapter:
    """获取日志器"""
    if use_structured is None:
        settings = get_settings()
        use_structured = settings.logging.structured
    
    return LoggerAdapter(name, use_structured)


class RequestLogger:
    """请求日志器，用于记录 HTTP 请求"""
    
    def __init__(self, logger: LoggerAdapter) -> None:
        self.logger = logger
    
    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        user_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """记录请求日志"""
        self.logger.info(
            "HTTP request processed",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=round(duration * 1000, 2),
            user_id=user_id,
            **kwargs,
        )
    
    def log_error(
        self,
        method: str,
        path: str,
        error: Exception,
        user_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """记录请求错误"""
        self.logger.error(
            "HTTP request failed",
            method=method,
            path=path,
            error=str(error),
            error_type=type(error).__name__,
            user_id=user_id,
            **kwargs,
        )


class PerformanceLogger:
    """性能日志器"""
    
    def __init__(self, logger: LoggerAdapter) -> None:
        self.logger = logger
    
    def log_operation(
        self,
        operation: str,
        duration: float,
        success: bool = True,
        **kwargs: Any,
    ) -> None:
        """记录操作性能"""
        level = "info" if success else "warning"
        getattr(self.logger, level)(
            f"Operation {operation} completed",
            operation=operation,
            duration_ms=round(duration * 1000, 2),
            success=success,
            **kwargs,
        )
    
    def log_slow_operation(
        self,
        operation: str,
        duration: float,
        threshold: float = 1.0,
        **kwargs: Any,
    ) -> None:
        """记录慢操作"""
        if duration > threshold:
            self.logger.warning(
                f"Slow operation detected: {operation}",
                operation=operation,
                duration_ms=round(duration * 1000, 2),
                threshold_ms=round(threshold * 1000, 2),
                **kwargs,
            )


# 全局日志器实例
_loggers: Dict[str, LoggerAdapter] = {}


def get_cached_logger(name: str) -> LoggerAdapter:
    """获取缓存的日志器实例"""
    if name not in _loggers:
        _loggers[name] = get_logger(name)
    return _loggers[name]


# 预定义的日志器
app_logger = get_cached_logger("laoke.app")
api_logger = get_cached_logger("laoke.api")
db_logger = get_cached_logger("laoke.database")
ai_logger = get_cached_logger("laoke.ai")
knowledge_logger = get_cached_logger("laoke.knowledge")
community_logger = get_cached_logger("laoke.community")
learning_logger = get_cached_logger("laoke.learning") 