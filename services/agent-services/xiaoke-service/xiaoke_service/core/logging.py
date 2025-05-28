"""
日志配置模块

使用 structlog 和 loguru 提供结构化日志记录，
支持JSON格式输出、链路追踪、性能监控等功能。
"""

import sys
from pathlib import Path
from typing import Any

import structlog
from loguru import logger as loguru_logger

from xiaoke_service.core.config import settings


def configure_structlog() -> None:
    """配置 structlog"""

    # 配置处理器链
    processors = [
        # 添加时间戳
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        # 添加调用信息
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        ),
        # 添加进程信息
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        # 格式化异常
        structlog.dev.set_exc_info,
    ]

    # 根据配置选择输出格式
    if settings.monitoring.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    # 配置 structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def configure_loguru() -> None:
    """配置 loguru"""

    # 移除默认处理器
    loguru_logger.remove()

    # 配置控制台输出
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    if settings.monitoring.log_format == "json":
        log_format = "{time} | {level} | {name}:{function}:{line} | {message}"

    loguru_logger.add(
        sys.stderr,
        format=log_format,
        level=settings.monitoring.log_level,
        colorize=settings.monitoring.log_format != "json",
        serialize=settings.monitoring.log_format == "json",
        backtrace=True,
        diagnose=True,
    )

    # 配置文件输出
    if settings.monitoring.log_file:
        log_file = Path(settings.monitoring.log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        loguru_logger.add(
            str(log_file),
            format=log_format,
            level=settings.monitoring.log_level,
            rotation="100 MB",
            retention="30 days",
            compression="gz",
            serialize=True,  # 文件总是使用JSON格式
            backtrace=True,
            diagnose=True,
        )


class StructuredLogger:
    """结构化日志记录器"""

    def __init__(self, name: str):
        self.name = name
        self._logger = structlog.get_logger(name)
        self._loguru = loguru_logger.bind(logger=name)

    def debug(self, message: str, **kwargs: Any) -> None:
        """记录调试信息"""
        self._logger.debug(message, **kwargs)
        self._loguru.debug(f"{message} | {kwargs}" if kwargs else message)

    def info(self, message: str, **kwargs: Any) -> None:
        """记录信息"""
        self._logger.info(message, **kwargs)
        self._loguru.info(f"{message} | {kwargs}" if kwargs else message)

    def warning(self, message: str, **kwargs: Any) -> None:
        """记录警告"""
        self._logger.warning(message, **kwargs)
        self._loguru.warning(f"{message} | {kwargs}" if kwargs else message)

    def error(self, message: str, **kwargs: Any) -> None:
        """记录错误"""
        self._logger.error(message, **kwargs)
        self._loguru.error(f"{message} | {kwargs}" if kwargs else message)

    def critical(self, message: str, **kwargs: Any) -> None:
        """记录严重错误"""
        self._logger.critical(message, **kwargs)
        self._loguru.critical(f"{message} | {kwargs}" if kwargs else message)

    def exception(self, message: str, **kwargs: Any) -> None:
        """记录异常"""
        self._logger.exception(message, **kwargs)
        self._loguru.exception(f"{message} | {kwargs}" if kwargs else message)

    def bind(self, **kwargs: Any) -> "StructuredLogger":
        """绑定上下文信息"""
        new_logger = StructuredLogger(self.name)
        new_logger._logger = self._logger.bind(**kwargs)
        new_logger._loguru = self._loguru.bind(**kwargs)
        return new_logger


class RequestLogger:
    """请求日志记录器"""

    def __init__(self, logger: StructuredLogger):
        self.logger = logger

    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        user_id: str | None = None,
        request_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """记录HTTP请求"""
        self.logger.info(
            "HTTP request processed",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=round(duration * 1000, 2),
            user_id=user_id,
            request_id=request_id,
            **kwargs,
        )

    def log_error(
        self,
        method: str,
        path: str,
        error: Exception,
        user_id: str | None = None,
        request_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """记录请求错误"""
        self.logger.error(
            "HTTP request error",
            method=method,
            path=path,
            error_type=type(error).__name__,
            error_message=str(error),
            user_id=user_id,
            request_id=request_id,
            **kwargs,
        )


class AILogger:
    """AI操作日志记录器"""

    def __init__(self, logger: StructuredLogger):
        self.logger = logger

    def log_inference(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        duration: float,
        user_id: str | None = None,
        session_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """记录AI推理"""
        self.logger.info(
            "AI inference completed",
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            duration_ms=round(duration * 1000, 2),
            user_id=user_id,
            session_id=session_id,
            **kwargs,
        )

    def log_knowledge_query(
        self,
        query: str,
        results_count: int,
        duration: float,
        knowledge_base: str = "default",
        user_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """记录知识库查询"""
        self.logger.info(
            "Knowledge base query",
            query_length=len(query),
            results_count=results_count,
            duration_ms=round(duration * 1000, 2),
            knowledge_base=knowledge_base,
            user_id=user_id,
            **kwargs,
        )


def get_logger(name: str) -> StructuredLogger:
    """获取结构化日志记录器"""
    return StructuredLogger(name)


def get_request_logger(name: str) -> RequestLogger:
    """获取请求日志记录器"""
    return RequestLogger(get_logger(name))


def get_ai_logger(name: str) -> AILogger:
    """获取AI日志记录器"""
    return AILogger(get_logger(name))


# 初始化日志配置
def init_logging() -> None:
    """初始化日志配置"""
    configure_structlog()
    configure_loguru()


# 在模块导入时自动初始化
init_logging()
