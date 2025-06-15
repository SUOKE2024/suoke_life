"""
日志配置模块
"""

import inspect
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from loguru import logger

from .config import settings


def configure_structlog() -> None:
    """配置structlog"""
    
    # 配置处理器
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    # 根据格式选择渲染器
    if settings.monitoring.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def configure_loguru() -> None:
    """配置loguru"""
    
    # 移除默认处理器
    logger.remove()
    
    # 配置控制台输出
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
    )
    
    # 配置文件输出
    if settings.monitoring.log_file:
        log_file_path = Path(settings.monitoring.log_file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file_path,
            format=log_format,
            level=settings.monitoring.log_level,
            rotation="1 day",
            retention="30 days",
            compression="gz",
            serialize=settings.monitoring.log_format == "json",
        )


def get_logger(name: Optional[str] = None) -> Any:
    """获取日志记录器
    
    Args:
        name: 日志记录器名称，如果为None则自动获取调用者模块名
        
    Returns:
        日志记录器实例
    """
    if name is None:
        # 自动获取调用者的模块名
        frame = inspect.currentframe()
        if frame and frame.f_back:
            name = frame.f_back.f_globals.get("__name__", "unknown")
    
    return logger.bind(name=name)


def setup_logging() -> None:
    """设置日志系统"""
    configure_loguru()
    configure_structlog()
    
    logger.info(
        "日志系统初始化完成",
        log_level=settings.monitoring.log_level,
        log_format=settings.monitoring.log_format,
        log_file=settings.monitoring.log_file,
    )


def log_error(
    message: str,
    exception: Optional[Exception] = None,
    **kwargs: Any
) -> None:
    """记录错误日志
    
    Args:
        message: 错误消息
        exception: 异常对象
        **kwargs: 额外的上下文信息
    """
    log_data = {"message": message, **kwargs}
    
    if exception:
        log_data["exception"] = {
            "type": type(exception).__name__,
            "message": str(exception),
        }
    
    logger.error(**log_data)


def log_request(
    method: str,
    url: str,
    status_code: int,
    duration: float,
    **kwargs: Any
) -> None:
    """记录请求日志
    
    Args:
        method: HTTP方法
        url: 请求URL
        status_code: 状态码
        duration: 请求耗时
        **kwargs: 额外的上下文信息
    """
    logger.info(
        "HTTP请求",
        method=method,
        url=url,
        status_code=status_code,
        duration=f"{duration:.3f}s",
        **kwargs
    )


def log_analysis(
    analysis_type: str,
    duration: float,
    success: bool,
    **kwargs: Any
) -> None:
    """记录分析日志
    
    Args:
        analysis_type: 分析类型
        duration: 分析耗时
        success: 是否成功
        **kwargs: 额外的上下文信息
    """
    logger.info(
        "分析完成",
        analysis_type=analysis_type,
        duration=f"{duration:.3f}s",
        success=success,
        **kwargs
    )


# 初始化日志系统
setup_logging()


def main() -> None:
    """主函数 - 用于测试"""
    test_logger = get_logger(__name__)
    test_logger.info("日志模块测试")
    test_logger.debug("调试信息")
    test_logger.warning("警告信息")
    test_logger.error("错误信息")


if __name__ == "__main__":
    main()
