#!/usr/bin/env python

"""
统一日志管理模块
"""

from datetime import datetime
import json
import logging
import os
import sys
from typing import Any

try:
    import structlog

    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False

class JSONFormatter(logging.Formatter):
    """JSON格式化器"""

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为JSON"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 添加额外字段
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data, ensure_ascii=False)

class ContextFilter(logging.Filter):
    """上下文过滤器，添加额外的上下文信息"""

    def __init__(self, context: dict[str, Any] | None = None):
        super().__init__()
        self.context = context or {}

    def filter(self, record: logging.LogRecord) -> bool:
        """添加上下文信息到日志记录"""
        if not hasattr(record, "extra_fields"):
            record.extra_fields = {}

        record.extra_fields.update(self.context)
        return True

class InquiryLogger:
    """问诊服务专用日志器"""

    def __init__(self, name: str, config: dict[str, Any] | None = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(name)
        self._context: dict[str, Any] = {}

        # 设置日志级别
        level = self.config.get("level", "INFO")
        self.logger.setLevel(getattr(logging, level.upper()))

    def add_context(self, **kwargs) -> "InquiryLogger":
        """添加上下文信息"""
        new_context = self._context.copy()
        new_context.update(kwargs)

        new_logger = InquiryLogger(self.name, self.config)
        new_logger._context = new_context
        new_logger.logger = self.logger

        return new_logger

    def _log_with_context(self, level: str, message: str, **kwargs) -> None:
        """带上下文的日志记录"""
        extra_fields = self._context.copy()
        extra_fields.update(kwargs)

        # 创建LogRecord并添加额外字段
        record = self.logger.makeRecord(
            self.logger.name, getattr(logging, level.upper()), "", 0, message, (), None
        )
        record.extra_fields = extra_fields

        self.logger.handle(record)

    def debug(self, message: str, **kwargs) -> None:
        """调试日志"""
        self._log_with_context("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """信息日志"""
        self._log_with_context("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """警告日志"""
        self._log_with_context("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """错误日志"""
        self._log_with_context("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """严重错误日志"""
        self._log_with_context("CRITICAL", message, **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        """异常日志"""
        kwargs["exc_info"] = True
        self._log_with_context("ERROR", message, **kwargs)

def setup_logging(config: dict[str, Any]) -> None:
    """设置日志配置"""
    # 获取配置
    level = config.get("level", "INFO")
    log_format = config.get(
        "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_path = config.get("file_path")
    max_file_size = config.get("max_file_size", 10 * 1024 * 1024)  # 10MB
    backup_count = config.get("backup_count", 5)
    enable_structured_logging = config.get("enable_structured_logging", False)

    # 设置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 创建格式化器
    if enable_structured_logging:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(log_format)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 文件处理器
    if file_path:
        # 确保日志目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # 添加上下文过滤器
    context_filter = ContextFilter({"service": "inquiry-service", "version": "1.0.0"})

    for handler in root_logger.handlers:
        handler.addFilter(context_filter)

    # 设置第三方库的日志级别
    logging.getLogger("grpc").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    print(f"日志系统初始化完成，级别: {level}")

def get_logger(name: str, config: dict[str, Any] | None = None) -> InquiryLogger:
    """获取问诊服务日志器"""
    return InquiryLogger(name, config)

def setup_structlog(config: dict[str, Any]) -> None:
    """设置structlog（如果可用）"""
    if not STRUCTLOG_AVAILABLE:
        return

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
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

class LoggingMiddleware:
    """日志中间件"""

    def __init__(self, logger: InquiryLogger):
        self.logger = logger

    async def __call__(self, request, call_next):
        """处理请求日志"""
        start_time = datetime.now()

        # 记录请求开始
        self.logger.info(
            "请求开始",
            method=getattr(request, "method", "UNKNOWN"),
            path=getattr(request, "url", {}).get("path", "UNKNOWN"),
            client_ip=getattr(request, "client", {}).get("host", "UNKNOWN"),
        )

        try:
            response = await call_next(request)

            # 记录请求完成
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(
                "请求完成",
                status_code=getattr(response, "status_code", "UNKNOWN"),
                duration_seconds=duration,
            )

            return response

        except Exception as e:
            # 记录请求错误
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.error(
                "请求失败",
                error=str(e),
                error_type=type(e).__name__,
                duration_seconds=duration,
            )
            raise

def log_function_call(
    logger: InquiryLogger, include_args: bool = False, include_result: bool = False
):
    """函数调用日志装饰器"""

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"

            log_data = {"function": func_name}
            if include_args:
                log_data["args"] = str(args)
                log_data["kwargs"] = str(kwargs)

            logger.debug("函数调用开始", **log_data)

            try:
                result = await func(*args, **kwargs)

                if include_result:
                    log_data["result"] = str(result)

                logger.debug("函数调用完成", **log_data)
                return result

            except Exception as e:
                log_data["error"] = str(e)
                log_data["error_type"] = type(e).__name__
                logger.error("函数调用失败", **log_data)
                raise

        def sync_wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"

            log_data = {"function": func_name}
            if include_args:
                log_data["args"] = str(args)
                log_data["kwargs"] = str(kwargs)

            logger.debug("函数调用开始", **log_data)

            try:
                result = func(*args, **kwargs)

                if include_result:
                    log_data["result"] = str(result)

                logger.debug("函数调用完成", **log_data)
                return result

            except Exception as e:
                log_data["error"] = str(e)
                log_data["error_type"] = type(e).__name__
                logger.error("函数调用失败", **log_data)
                raise

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

class AuditLogger:
    """审计日志器"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.logger = get_logger("audit", config)

    def log_user_action(
        self,
        user_id: str,
        action: str,
        resource: str,
        result: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """记录用户操作"""
        self.logger.info(
            "用户操作",
            user_id=user_id,
            action=action,
            resource=resource,
            result=result,
            details=details or {},
        )

    def log_system_event(
        self,
        event_type: str,
        description: str,
        severity: str = "INFO",
        details: dict[str, Any] | None = None,
    ) -> None:
        """记录系统事件"""
        log_method = getattr(self.logger, severity.lower(), self.logger.info)
        log_method(
            "系统事件",
            event_type=event_type,
            description=description,
            details=details or {},
        )

    def log_security_event(
        self,
        event_type: str,
        source_ip: str,
        user_id: str | None = None,
        description: str = "",
        details: dict[str, Any] | None = None,
    ) -> None:
        """记录安全事件"""
        self.logger.warning(
            "安全事件",
            event_type=event_type,
            source_ip=source_ip,
            user_id=user_id,
            description=description,
            details=details or {},
        )
