#!/usr/bin/env python3
"""
日志聚合模块
提供统一的日志收集、格式化、路由和存储功能
"""

from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
import json
import logging
import os
import sys
import traceback
from typing import Any

from pythonjsonlogger import jsonlogger
import structlog

# 尝试导入可选的日志后端
try:
    import logstash

    HAS_LOGSTASH = True
except ImportError:
    HAS_LOGSTASH = False

try:
    from fluent import sender

    HAS_FLUENT = True
except ImportError:
    HAS_FLUENT = False


class LogLevel(Enum):
    """日志级别"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogContext:
    """日志上下文"""

    service_name: str
    service_version: str
    environment: str
    instance_id: str
    trace_id: str | None = None
    span_id: str | None = None
    user_id: str | None = None
    request_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {k: v for k, v in asdict(self).items() if v is not None}


class LogFormatter:
    """日志格式化器基类"""

    def format(self, record: dict[str, Any]) -> str:
        """格式化日志记录"""
        raise NotImplementedError


class JSONLogFormatter(LogFormatter):
    """JSON格式化器"""

    def format(self, record: dict[str, Any]) -> str:
        """格式化为JSON"""
        # 确保时间戳格式
        if "timestamp" in record and isinstance(record["timestamp"], datetime):
            record["timestamp"] = record["timestamp"].isoformat()

        return json.dumps(record, ensure_ascii=False)


class StructuredLogFormatter(LogFormatter):
    """结构化日志格式化器"""

    def __init__(self, format_string: str | None = None):
        self.format_string = (
            format_string or "{timestamp} [{level}] {service_name} - {message}"
        )

    def format(self, record: dict[str, Any]) -> str:
        """格式化为结构化文本"""
        return self.format_string.format(**record)


class LogRouter:
    """日志路由器"""

    def __init__(self):
        self.routes: dict[str, list[logging.Handler]] = {"default": []}

    def add_route(self, pattern: str, handler: logging.Handler):
        """添加路由规则"""
        if pattern not in self.routes:
            self.routes[pattern] = []
        self.routes[pattern].append(handler)

    def route(self, record: logging.LogRecord) -> list[logging.Handler]:
        """根据记录路由到处理器"""
        handlers = []

        # 检查每个路由模式
        for pattern, route_handlers in self.routes.items():
            if self._match_pattern(pattern, record):
                handlers.extend(route_handlers)

        # 如果没有匹配的路由，使用默认路由
        if not handlers and "default" in self.routes:
            handlers = self.routes["default"]

        return handlers

    def _match_pattern(self, pattern: str, record: logging.LogRecord) -> bool:
        """匹配路由模式"""
        if pattern == "default":
            return True

        # 简单的模式匹配（可以扩展为更复杂的规则）
        if pattern.startswith("level:"):
            level = pattern.split(":")[1]
            return record.levelname == level

        if pattern.startswith("service:"):
            service = pattern.split(":")[1]
            return getattr(record, "service_name", "") == service

        if pattern.startswith("module:"):
            module = pattern.split(":")[1]
            return record.module.startswith(module)

        return False


class LogAggregator:
    """日志聚合器"""

    def __init__(
        self,
        context: LogContext,
        formatter: LogFormatter | None = None,
        enable_console: bool = True,
        enable_file: bool = True,
        log_file: str = "app.log",
        enable_logstash: bool = False,
        logstash_host: str = "localhost",
        logstash_port: int = 5959,
        enable_fluentd: bool = False,
        fluentd_tag: str = "suoke.life",
        fluentd_host: str = "localhost",
        fluentd_port: int = 24224,
    ):
        self.context = context
        self.formatter = formatter or JSONLogFormatter()
        self.router = LogRouter()

        # 配置structlog
        self._configure_structlog()

        # 配置标准logging
        self._configure_standard_logging()

        # 添加处理器
        if enable_console:
            self._add_console_handler()

        if enable_file:
            self._add_file_handler(log_file)

        if enable_logstash and HAS_LOGSTASH:
            self._add_logstash_handler(logstash_host, logstash_port)

        if enable_fluentd and HAS_FLUENT:
            self._add_fluentd_handler(fluentd_tag, fluentd_host, fluentd_port)

        self.logger = structlog.get_logger()

    def _configure_structlog(self):
        """配置structlog"""
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
                self._add_context,
                structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    def _configure_standard_logging(self):
        """配置标准logging"""
        # 设置根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

        # 清除现有处理器
        root_logger.handlers = []

    def _add_context(self, logger, method_name, event_dict):
        """添加上下文信息到日志"""
        event_dict.update(self.context.to_dict())
        return event_dict

    def _add_console_handler(self):
        """添加控制台处理器"""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

        # 使用JSON格式化器
        json_formatter = jsonlogger.JsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s", timestamp=True
        )
        handler.setFormatter(json_formatter)

        # 添加到默认路由
        self.router.add_route("default", handler)
        logging.getLogger().addHandler(handler)

    def _add_file_handler(self, log_file: str):
        """添加文件处理器"""
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=100 * 1024 * 1024,  # 100MB
            backupCount=10,
        )
        handler.setLevel(logging.DEBUG)

        # 使用JSON格式化器
        json_formatter = jsonlogger.JsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s", timestamp=True
        )
        handler.setFormatter(json_formatter)

        # 添加到默认路由
        self.router.add_route("default", handler)
        logging.getLogger().addHandler(handler)

    def _add_logstash_handler(self, host: str, port: int):
        """添加Logstash处理器"""
        if not HAS_LOGSTASH:
            self.logger.warning("python-logstash未安装，跳过Logstash处理器")
            return

        handler = logstash.TCPLogstashHandler(
            host=host,
            port=port,
            version=1,
            tags=[self.context.service_name, self.context.environment],
        )
        handler.setLevel(logging.INFO)

        # 添加到默认路由
        self.router.add_route("default", handler)
        logging.getLogger().addHandler(handler)

    def _add_fluentd_handler(self, tag: str, host: str, port: int):
        """添加Fluentd处理器"""
        if not HAS_FLUENT:
            self.logger.warning("fluent-logger未安装，跳过Fluentd处理器")
            return

        # 创建Fluentd发送器
        self.fluent_sender = sender.FluentSender(tag, host=host, port=port)

        # 创建自定义处理器
        class FluentHandler(logging.Handler):
            def __init__(self, sender_obj, context):
                super().__init__()
                self.sender = sender_obj
                self.context = context

            def emit(self, record):
                try:
                    # 构建日志数据
                    log_data = {
                        "timestamp": datetime.now().isoformat(),
                        "level": record.levelname,
                        "logger": record.name,
                        "message": record.getMessage(),
                        "module": record.module,
                        "function": record.funcName,
                        "line": record.lineno,
                        **self.context.to_dict(),
                    }

                    # 添加异常信息
                    if record.exc_info:
                        log_data["exception"] = traceback.format_exception(
                            *record.exc_info
                        )

                    # 发送到Fluentd
                    self.sender.emit(record.name, log_data)
                except Exception as e:
                    print(f"发送日志到Fluentd失败: {e}")

        handler = FluentHandler(self.fluent_sender, self.context)
        handler.setLevel(logging.INFO)

        # 添加到默认路由
        self.router.add_route("default", handler)
        logging.getLogger().addHandler(handler)

    def get_logger(self, name: str | None = None) -> structlog.BoundLogger:
        """获取日志器"""
        if name:
            return structlog.get_logger(name)
        return self.logger

    def debug(self, message: str, **kwargs):
        """记录调试日志"""
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs):
        """记录信息日志"""
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """记录警告日志"""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs):
        """记录错误日志"""
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs):
        """记录严重错误日志"""
        self.logger.critical(message, **kwargs)

    def exception(self, message: str, **kwargs):
        """记录异常日志"""
        self.logger.exception(message, **kwargs)

    def add_route(self, pattern: str, handler: logging.Handler):
        """添加日志路由"""
        self.router.add_route(pattern, handler)
        logging.getLogger().addHandler(handler)

    def set_context(self, **kwargs):
        """更新日志上下文"""
        for key, value in kwargs.items():
            if hasattr(self.context, key):
                setattr(self.context, key, value)

    def with_context(self, **kwargs) -> structlog.BoundLogger:
        """创建带有额外上下文的日志器"""
        return self.logger.bind(**kwargs)


# 全局日志聚合器注册表
_aggregators: dict[str, LogAggregator] = {}


def get_log_aggregator(
    service_name: str,
    service_version: str = "1.0.0",
    environment: str = "development",
    instance_id: str | None = None,
    **kwargs,
) -> LogAggregator:
    """获取或创建日志聚合器"""
    if service_name not in _aggregators:
        context = LogContext(
            service_name=service_name,
            service_version=service_version,
            environment=environment,
            instance_id=instance_id or f"{service_name}-{os.getpid()}",
        )

        _aggregators[service_name] = LogAggregator(context, **kwargs)

    return _aggregators[service_name]


# 便捷函数
def setup_logging(
    service_name: str,
    service_version: str = "1.0.0",
    environment: str = "development",
    log_level: str = "INFO",
    **kwargs,
) -> LogAggregator:
    """
    设置日志系统

    Args:
        service_name: 服务名称
        service_version: 服务版本
        environment: 环境（development, staging, production）
        log_level: 日志级别
        **kwargs: 其他LogAggregator参数

    Returns:
        LogAggregator: 日志聚合器实例
    """
    # 设置日志级别
    numeric_level = getattr(logging, log_level.upper(), None)
    if isinstance(numeric_level, int):
        logging.getLogger().setLevel(numeric_level)

    # 创建日志聚合器
    aggregator = get_log_aggregator(
        service_name=service_name,
        service_version=service_version,
        environment=environment,
        **kwargs,
    )

    return aggregator
