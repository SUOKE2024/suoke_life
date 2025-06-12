"""老克智能体服务日志管理模块"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger

from .config import LoggingConfig, get_config


class LoggerManager:
    """日志管理器"""

    def __init__(self):
        self._initialized = False
        self._config: Optional[LoggingConfig] = None

    def setup_logging(self, config: Optional[LoggingConfig] = None) -> None:
        """设置日志配置"""
        if self._initialized:
            return

        if config is None:
            app_config = get_config()
            config = app_config.logging

        self._config = config

        # 清除默认处理器
        logger.remove()

        # 设置控制台日志
        if config.console_enabled:
            self._setup_console_logging(config)

        # 设置文件日志
        if config.file_enabled:
            self._setup_file_logging(config)

        # 设置结构化日志过滤器
        self._setup_filters()

        self._initialized = True
        logger.info("日志系统初始化完成")

    def _setup_console_logging(self, config: LoggingConfig) -> None:
        """设置控制台日志"""
        console_format = self._get_console_format(config)

        logger.add(
            sys.stdout,
            format=console_format,
            level=config.level,
            colorize=config.console_colored,
            backtrace=True,
            diagnose=True,
            enqueue=True,
        )

    def _setup_file_logging(self, config: LoggingConfig) -> None:
        """设置文件日fd7"""
        # 确保日志目录存在
        log_file = Path(config.file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_format = self._get_file_format(config)

        logger.add(
            config.file_path,
            format=file_format,
            level=config.level,
            rotation=config.file_max_size,
            retention=config.file_backup_count,
            compression="gz",
            backtrace=True,
            diagnose=True,
            enqueue=True,
            serialize=False,
        )

    def _get_console_format(self, config: LoggingConfig) -> str:
        """获取控制台日志格式"""
        if config.console_colored:
            return (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            )
        else:
            return (
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                "{level: <8} | "
                "{name}:{function}:{line} | "
                "{message}"
            )

    def _get_file_format(self, config: LoggingConfig) -> str:
        """获取文件日志格式"""
        return (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{process.id} | "
            "{thread.id} | "
            "{name}:{function}:{line} | "
            "{message} | "
            "{extra}"
        )

    def _setup_filters(self) -> None:
        """设置日志过滤器"""

        # 过滤敏感信息
        def filter_sensitive_info(record):
            message = record["message"]

            # 过滤API密钥
            if "api_key" in message.lower() or "password" in message.lower():
                record["message"] = self._mask_sensitive_data(message)

            return record

        logger.configure(patcher=filter_sensitive_info)

    def _mask_sensitive_data(self, message: str) -> str:
        """隐藏敏感数据"""
        import re

        # 隐藏API密钥
        message = re.sub(
            r'(api_key["\s]*[:=]["\s]*)[^"\s,}]+',
            r"\1***",
            message,
            flags=re.IGNORECASE,
        )

        # 隐藏密码
        message = re.sub(
            r'(password["\s]*[:=]["\s]*)[^"\s,}]+',
            r"\1***",
            message,
            flags=re.IGNORECASE,
        )

        return message

    def get_logger(self, name: str) -> Any:
        """获取指定名称的日志器"""
        if not self._initialized:
            self.setup_logging()

        return logger.bind(name=name)

    def add_context(self, **kwargs) -> Any:
        """添加上下文信息"""
        return logger.bind(**kwargs)

    def log_request(
        self, method: str, path: str, user_id: Optional[str] = None, **kwargs
    ) -> None:
        """记录请求日志"""
        context = {"event_type": "request", "method": method, "path": path, **kwargs}

        if user_id:
            context["user_id"] = user_id

        logger.bind(**context).info(f"{method} {path}")

    def log_response(
        self, method: str, path: str, status_code: int, duration_ms: float, **kwargs
    ) -> None:
        """记录响应日志"""
        context = {
            "event_type": "response",
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            **kwargs,
        }

        level = "info"
        if status_code >= 400:
            level = "warning" if status_code < 500 else "error"

        getattr(logger.bind(**context), level)(
            f"{method} {path} - {status_code} ({duration_ms:.2f}ms)"
        )

    def log_ai_interaction(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        duration_ms: float,
        **kwargs,
    ) -> None:
        """记录AI交互日志"""
        context = {
            "event_type": "ai_interaction",
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "duration_ms": duration_ms,
            **kwargs,
        }

        logger.bind(**context).info(
            f"AI交互: {model} - {prompt_tokens + completion_tokens} tokens ({duration_ms:.2f}ms)"
        )

    def log_database_operation(
        self,
        operation: str,
        table: str,
        duration_ms: float,
        affected_rows: Optional[int] = None,
        **kwargs,
    ) -> None:
        """记录数据库操作日志"""
        context = {
            "event_type": "database_operation",
            "operation": operation,
            "table": table,
            "duration_ms": duration_ms,
            **kwargs,
        }

        if affected_rows is not None:
            context["affected_rows"] = affected_rows

        logger.bind(**context).info(
            f"数据库操作: {operation} {table} ({duration_ms:.2f}ms)"
        )

    def log_cache_operation(
        self,
        operation: str,
        key: str,
        hit: Optional[bool] = None,
        duration_ms: Optional[float] = None,
        **kwargs,
    ) -> None:
        """记录缓存操作日志"""
        context = {
            "event_type": "cache_operation",
            "operation": operation,
            "key": key,
            **kwargs,
        }

        if hit is not None:
            context["hit"] = hit

        if duration_ms is not None:
            context["duration_ms"] = duration_ms

        message = f"缓存操作: {operation} {key}"
        if hit is not None:
            message += f" ({'HIT' if hit else 'MISS'})"
        if duration_ms is not None:
            message += f" ({duration_ms:.2f}ms)"

        logger.bind(**context).info(message)

    def log_error(
        self, error: Exception, context: Optional[Dict[str, Any]] = None, **kwargs
    ) -> None:
        """记录错误日志"""
        log_context = {
            "event_type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            **kwargs,
        }

        if context:
            log_context.update(context)

        logger.bind(**log_context).error(f"错误: {error}")

    def log_performance(self, operation: str, duration_ms: float, **kwargs) -> None:
        """记录性能日志"""
        context = {
            "event_type": "performance",
            "operation": operation,
            "duration_ms": duration_ms,
            **kwargs,
        }

        level = "info"
        if duration_ms > 5000:  # 5秒
            level = "warning"
        elif duration_ms > 10000:  # 10秒
            level = "error"

        getattr(logger.bind(**context), level)(
            f"性能监控: {operation} ({duration_ms:.2f}ms)"
        )

    def log_security_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        **kwargs,
    ) -> None:
        """记录安全事件日志"""
        context = {
            "event_type": "security_event",
            "security_event_type": event_type,
            **kwargs,
        }

        if user_id:
            context["user_id"] = user_id

        if ip_address:
            context["ip_address"] = ip_address

        logger.bind(**context).warning(f"安全事件: {event_type}")

    def log_business_event(
        self, event_type: str, user_id: Optional[str] = None, **kwargs
    ) -> None:
        """记录业务事件日志"""
        context = {
            "event_type": "business_event",
            "business_event_type": event_type,
            **kwargs,
        }

        if user_id:
            context["user_id"] = user_id

        logger.bind(**context).info(f"业务事件: {event_type}")


# 全局日志管理器实例
logger_manager = LoggerManager()


def setup_logging(config: Optional[LoggingConfig] = None) -> None:
    """设置日志系统"""
    logger_manager.setup_logging(config)


def get_logger(name: str) -> Any:
    """获取日志器"""
    return logger_manager.get_logger(name)


def log_request(
    method: str, path: str, user_id: Optional[str] = None, **kwargs
) -> None:
    """记录请求日志"""
    logger_manager.log_request(method, path, user_id, **kwargs)


def log_response(
    method: str, path: str, status_code: int, duration_ms: float, **kwargs
) -> None:
    """记录响应日志"""
    logger_manager.log_response(method, path, status_code, duration_ms, **kwargs)


def log_ai_interaction(
    model: str, prompt_tokens: int, completion_tokens: int, duration_ms: float, **kwargs
) -> None:
    """记录AI交互日志"""
    logger_manager.log_ai_interaction(
        model, prompt_tokens, completion_tokens, duration_ms, **kwargs
    )


def log_database_operation(
    operation: str,
    table: str,
    duration_ms: float,
    affected_rows: Optional[int] = None,
    **kwargs,
) -> None:
    """记录数据库操作日志"""
    logger_manager.log_database_operation(
        operation, table, duration_ms, affected_rows, **kwargs
    )


def log_cache_operation(
    operation: str,
    key: str,
    hit: Optional[bool] = None,
    duration_ms: Optional[float] = None,
    **kwargs,
) -> None:
    """记录缓存操作日志"""
    logger_manager.log_cache_operation(operation, key, hit, duration_ms, **kwargs)


def log_error(
    error: Exception, context: Optional[Dict[str, Any]] = None, **kwargs
) -> None:
    """记录错误日志"""
    logger_manager.log_error(error, context, **kwargs)


def log_performance(operation: str, duration_ms: float, **kwargs) -> None:
    """记录性能日志"""
    logger_manager.log_performance(operation, duration_ms, **kwargs)


def log_security_event(
    event_type: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    **kwargs,
) -> None:
    """记录安全事件日志"""
    logger_manager.log_security_event(event_type, user_id, ip_address, **kwargs)


def log_business_event(
    event_type: str, user_id: Optional[str] = None, **kwargs
) -> None:
    """记录业务事件日志"""
    logger_manager.log_business_event(event_type, user_id, **kwargs)
