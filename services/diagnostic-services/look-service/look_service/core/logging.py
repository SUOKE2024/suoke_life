"""
logging - 索克生活项目模块
"""

        import inspect
from .config import settings
from loguru import logger
from pathlib import Path
from typing import Any
import structlog
import sys

"""Logging configuration for look service."""





def configure_structlog() -> None:
    """Configure structlog for structured logging."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
            if settings.monitoring.log_format == "json"
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(structlog.stdlib, settings.monitoring.log_level.upper(), 20)
        ),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def configure_loguru() -> None:
    """Configure loguru for application logging."""
    # Remove default handler
    logger.remove()

    # Console handler
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    if settings.monitoring.log_format == "json":
        log_format = "{time} | {level} | {name}:{function}:{line} | {message}"

    logger.add(
        sys.stderr,
        format=log_format,
        level=settings.monitoring.log_level,
        colorize=settings.monitoring.log_format != "json",
        serialize=settings.monitoring.log_format == "json",
        backtrace=True,
        diagnose=True,
    )

    # File handler (if configured)
    if settings.monitoring.log_file:
        log_file_path = Path(settings.monitoring.log_file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file_path,
            format=log_format,
            level=settings.monitoring.log_level,
            rotation="100 MB",
            retention="30 days",
            compression="gz",
            serialize=settings.monitoring.log_format == "json",
            backtrace=True,
            diagnose=True,
        )


def get_logger(name: str | None = None) -> Any:
    """Get a logger instance.

    Args:
        name: Logger name. If None, uses the calling module name.

    Returns:
        Logger instance.
    """
    if name is None:
        # Get the calling module name

        frame = inspect.currentframe()
        if frame and frame.f_back:
            name = frame.f_back.f_globals.get("__name__", "unknown")

    return logger.bind(service="look-service", logger_name=name)


def setup_logging() -> None:
    """Setup logging configuration."""
    configure_loguru()
    configure_structlog()


# Context manager for adding context to logs
class LogContext:
    """Context manager for adding context to logs."""

    def __init__(self, **context: Any) -> None:
        """Initialize with context data."""
        self.context = context
        self.token: Any | None = None

    def __enter__(self) -> "LogContext":
        """Enter context."""
        self.token = structlog.contextvars.bind_contextvars(**self.context)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context."""
        if self.token:
            structlog.contextvars.unbind_contextvars(*self.context.keys())


# Utility functions for common logging patterns
def log_function_call(func_name: str, **kwargs: Any) -> None:
    """Log function call with parameters."""
    logger.debug(f"Calling function: {func_name}", **kwargs)


def log_performance(operation: str, duration: float, **kwargs: Any) -> None:
    """Log performance metrics."""
    logger.info(f"Performance: {operation}", duration_ms=duration * 1000, **kwargs)


def log_error(error: Exception, context: dict[str, Any] | None = None) -> None:
    """Log error with context."""
    logger.error(
        f"Error occurred: {type(error).__name__}",
        error_message=str(error),
        error_type=type(error).__name__,
        **(context or {}),
    )


def log_api_request(method: str, path: str, status_code: int, duration: float) -> None:
    """Log API request."""
    logger.info(
        "API request",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration * 1000,
    )


# Initialize logging on module import
setup_logging()
