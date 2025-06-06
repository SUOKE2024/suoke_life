"""
logging - 索克生活项目模块
"""

from datetime import datetime
from pathlib import Path
from structlog.types import FilteringBoundLogger
import json
import logging
import structlog
import sys
import time

"""
结构化日志配置工具

提供基于structlog的现代化日志配置，支持JSON格式、彩色输出、性能监控等功能。
"""



def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
    log_file: str | None = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True,
    enable_colors: bool = True,
    include_caller: bool = True,
    service_name: str = "listen-service",
    service_version: str = "1.0.0",
) -> FilteringBoundLogger:
    """
    设置结构化日志

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: 格式类型 (json, console, plain)
        log_file: 日志文件路径
        max_file_size: 最大文件大小
        backup_count: 备份文件数量
        enable_console: 是否启用控制台输出
        enable_colors: 是否启用彩色输出
        include_caller: 是否包含调用者信息
        service_name: 服务名称
        service_version: 服务版本

    Returns:
        配置好的logger实例
    """

    # 设置日志级别
    log_level = getattr(logging, level.upper(), logging.INFO)

    # 配置structlog处理器
    processors = [
        # 添加时间戳
        structlog.processors.TimeStamper(fmt="iso"),
        # 添加日志级别
        structlog.stdlib.add_log_level,
        # 添加服务信息
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        )
        if include_caller
        else lambda logger, method_name, event_dict: event_dict,
        # 添加服务元数据
        lambda logger, method_name, event_dict: {
            **event_dict,
            "service": service_name,
            "version": service_version,
        },
    ]

    # 配置输出格式
    if format_type == "json":
        processors.append(structlog.processors.JSONRenderer())
    elif format_type == "console":
        if enable_colors and sys.stderr.isatty():
            processors.append(
                structlog.dev.ConsoleRenderer(
                    colors=True,
                    exception_formatter=structlog.dev.rich_traceback,
                )
            )
        else:
            processors.append(structlog.dev.ConsoleRenderer(colors=False))
    else:  # plain
        processors.append(structlog.processors.KeyValueRenderer())

    # 配置structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # 配置标准库logging
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 添加控制台处理器
    if enable_console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(log_level)

        if format_type == "json":
            console_formatter = JSONFormatter(service_name, service_version)
        else:
            console_formatter = (
                ColoredFormatter() if enable_colors else PlainFormatter()
            )

        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # 添加文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)

        # 文件总是使用JSON格式
        file_formatter = JSONFormatter(service_name, service_version)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # 配置第三方库日志级别
    _configure_third_party_loggers()

    # 获取structlog logger
    logger = structlog.get_logger()

    logger.info(
        "日志系统初始化完成",
        level=level,
        format_type=format_type,
        log_file=log_file,
        enable_console=enable_console,
        enable_colors=enable_colors,
    )

    return logger

def _configure_third_party_loggers():
    """配置第三方库的日志级别"""
    # 设置第三方库日志级别，避免过多噪音
    third_party_loggers = {
        "urllib3": logging.WARNING,
        "requests": logging.WARNING,
        "grpc": logging.WARNING,
        "asyncio": logging.WARNING,
        "multipart": logging.WARNING,
        "uvicorn": logging.INFO,
        "uvicorn.access": logging.WARNING,
    }

    for logger_name, level in third_party_loggers.items():
        logging.getLogger(logger_name).setLevel(level)

class JSONFormatter(logging.Formatter):
    """JSON格式化器"""

    def __init__(self, service_name: str, service_version: str):
        super().__init__()
        self.service_name = service_name
        self.service_version = service_version

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为JSON"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service_name,
            "version": self.service_version,
        }

        # 添加调用者信息
        if hasattr(record, "filename"):
            log_entry["filename"] = record.filename
        if hasattr(record, "funcName"):
            log_entry["function"] = record.funcName
        if hasattr(record, "lineno"):
            log_entry["line"] = record.lineno

        # 添加异常信息
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # 添加额外字段
        if hasattr(record, "__dict__"):
            for key, value in record.__dict__.items():
                if key not in [
                    "name",
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "lineno",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                    "getMessage",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                ]:
                    log_entry[key] = value

        return json.dumps(log_entry, ensure_ascii=False, default=str)

class ColoredFormatter(logging.Formatter):
    """彩色控制台格式化器"""

    # ANSI颜色代码
    COLORS = {
        "DEBUG": "\033[36m",  # 青色
        "INFO": "\033[32m",  # 绿色
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",  # 红色
        "CRITICAL": "\033[35m",  # 紫色
    }
    RESET = "\033[0m"

    def __init__(self):
        super().__init__()
        self.fmt = (
            "{color}[{levelname:8}]{reset} "
            "{asctime} | {name:20} | {funcName:15} | {message}"
        )

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为彩色文本"""
        color = self.COLORS.get(record.levelname, "")

        formatted = self.fmt.format(
            color=color,
            reset=self.RESET,
            levelname=record.levelname,
            asctime=self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            name=record.name,
            funcName=record.funcName,
            message=record.getMessage(),
        )

        # 添加异常信息
        if record.exc_info:
            formatted += "\n" + self.formatException(record.exc_info)

        return formatted

class PlainFormatter(logging.Formatter):
    """纯文本格式化器"""

    def __init__(self):
        super().__init__(
            fmt="[{levelname:8}] {asctime} | {name:20} | {funcName:15} | {message}",
            datefmt="%Y-%m-%d %H:%M:%S",
            style="{",
        )

class PerformanceLogger:
    """性能日志记录器"""

    def __init__(self, logger: FilteringBoundLogger | None = None):
        self.logger = logger or structlog.get_logger()
        self.start_times: dict[str, float] = {}

    def start_operation(self, operation_id: str, operation_name: str, **kwargs) -> None:
        """开始记录操作"""
        self.start_times[operation_id] = time.time()
        self.logger.info(
            "操作开始",
            operation_id=operation_id,
            operation_name=operation_name,
            **kwargs,
        )

    def end_operation(
        self, operation_id: str, operation_name: str, success: bool = True, **kwargs
    ) -> float:
        """结束记录操作"""
        start_time = self.start_times.pop(operation_id, time.time())
        duration = time.time() - start_time

        log_method = self.logger.info if success else self.logger.error
        log_method(
            "操作完成",
            operation_id=operation_id,
            operation_name=operation_name,
            duration=duration,
            success=success,
            **kwargs,
        )

        return duration

    def log_metric(self, metric_name: str, value: int | float, **kwargs) -> None:
        """记录指标"""
        self.logger.info(
            "性能指标", metric_name=metric_name, metric_value=value, **kwargs
        )

class AuditLogger:
    """审计日志记录器"""

    def __init__(self, logger: FilteringBoundLogger | None = None):
        self.logger = logger or structlog.get_logger("audit")

    def log_audio_analysis(
        self,
        user_id: str | None,
        audio_hash: str,
        analysis_type: str,
        success: bool,
        duration: float,
        **kwargs,
    ) -> None:
        """记录音频分析审计日志"""
        self.logger.info(
            "音频分析审计",
            event_type="audio_analysis",
            user_id=user_id,
            audio_hash=audio_hash,
            analysis_type=analysis_type,
            success=success,
            duration=duration,
            **kwargs,
        )

    def log_tcm_diagnosis(
        self,
        user_id: str | None,
        diagnosis_id: str,
        constitution_type: str,
        emotion_state: str,
        confidence_score: float,
        **kwargs,
    ) -> None:
        """记录中医诊断审计日志"""
        self.logger.info(
            "中医诊断审计",
            event_type="tcm_diagnosis",
            user_id=user_id,
            diagnosis_id=diagnosis_id,
            constitution_type=constitution_type,
            emotion_state=emotion_state,
            confidence_score=confidence_score,
            **kwargs,
        )

    def log_cache_operation(
        self, operation: str, cache_key: str, hit: bool, **kwargs
    ) -> None:
        """记录缓存操作审计日志"""
        self.logger.debug(
            "缓存操作审计",
            event_type="cache_operation",
            operation=operation,
            cache_key=cache_key,
            cache_hit=hit,
            **kwargs,
        )

class SecurityLogger:
    """安全日志记录器"""

    def __init__(self, logger: FilteringBoundLogger | None = None):
        self.logger = logger or structlog.get_logger("security")

    def log_authentication_attempt(
        self,
        user_id: str | None,
        success: bool,
        ip_address: str | None = None,
        user_agent: str | None = None,
        **kwargs,
    ) -> None:
        """记录认证尝试"""
        self.logger.info(
            "认证尝试",
            event_type="authentication",
            user_id=user_id,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            **kwargs,
        )

    def log_authorization_failure(
        self,
        user_id: str | None,
        resource: str,
        action: str,
        ip_address: str | None = None,
        **kwargs,
    ) -> None:
        """记录授权失败"""
        self.logger.warning(
            "授权失败",
            event_type="authorization_failure",
            user_id=user_id,
            resource=resource,
            action=action,
            ip_address=ip_address,
            **kwargs,
        )

    def log_suspicious_activity(
        self,
        activity_type: str,
        description: str,
        user_id: str | None = None,
        ip_address: str | None = None,
        **kwargs,
    ) -> None:
        """记录可疑活动"""
        self.logger.error(
            "可疑活动",
            event_type="suspicious_activity",
            activity_type=activity_type,
            description=description,
            user_id=user_id,
            ip_address=ip_address,
            **kwargs,
        )

class LogContext:
    """日志上下文管理器"""

    def __init__(self, logger: FilteringBoundLogger, **context):
        self.logger = logger
        self.context = context
        self.bound_logger = None

    def __enter__(self) -> FilteringBoundLogger:
        self.bound_logger = self.logger.bind(**self.context)
        return self.bound_logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.bound_logger.error(
                "上下文执行异常",
                exception_type=exc_type.__name__,
                exception_message=str(exc_val),
                exc_info=True,
            )

def get_logger(name: str | None = None) -> FilteringBoundLogger:
    """获取logger实例"""
    return structlog.get_logger(name)

def log_function_call(
    logger: FilteringBoundLogger | None = None,
    include_args: bool = False,
    include_result: bool = False,
):
    """函数调用日志装饰器"""

    def decorator(func):
        nonlocal logger
        if logger is None:
            logger = structlog.get_logger(func.__module__)

        def wrapper(*args, **kwargs):
            function_name = f"{func.__module__}.{func.__qualname__}"

            log_data = {"function": function_name}
            if include_args:
                log_data["args"] = args
                log_data["kwargs"] = kwargs

            logger.debug("函数调用开始", **log_data)

            start_time = time.time()
            try:
                result = func(*args, **kwargs)

                duration = time.time() - start_time
                log_data["duration"] = duration
                log_data["success"] = True

                if include_result:
                    log_data["result"] = result

                logger.debug("函数调用完成", **log_data)
                return result

            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    "函数调用异常",
                    function=function_name,
                    duration=duration,
                    error=str(e),
                    exc_info=True,
                )
                raise

        return wrapper

    return decorator

# 全局logger实例
performance_logger = PerformanceLogger()
audit_logger = AuditLogger()
security_logger = SecurityLogger()
