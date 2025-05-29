"""日志管理模块"""

import sys
from pathlib import Path
from typing import Any

from loguru import logger

from health_data_service.core.config import settings


def setup_logging() -> None:
    """设置日志配置"""
    # 移除默认处理器
    logger.remove()

    # 控制台日志
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    if settings.logging.json_logs:
        # JSON格式日志
        logger.add(
            sys.stdout,
            format="{time} {level} {name} {function} {line} {message}",
            level=settings.logging.level,
            serialize=True,
        )
    else:
        # 彩色格式日志
        logger.add(
            sys.stdout,
            format=console_format,
            level=settings.logging.level,
            colorize=True,
        )

    # 文件日志
    if settings.logging.file_enabled:
        log_path = Path(settings.logging.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # 普通日志文件
        logger.add(
            log_path,
            format=settings.logging.format,
            level=settings.logging.level,
            rotation=settings.logging.file_rotation,
            retention=settings.logging.file_retention,
            compression="gz",
            enqueue=True,
        )

        # 错误日志文件
        error_log_path = log_path.parent / f"{log_path.stem}_error{log_path.suffix}"
        logger.add(
            error_log_path,
            format=settings.logging.format,
            level="ERROR",
            rotation=settings.logging.file_rotation,
            retention=settings.logging.file_retention,
            compression="gz",
            enqueue=True,
        )


def get_logger(name: str | None = None) -> Any:
    """获取日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器实例
    """
    if name:
        return logger.bind(name=name)
    return logger


def log_request(
    method: str,
    url: str,
    status_code: int,
    duration: float,
    user_id: str | None = None,
    **kwargs: Any,
) -> None:
    """记录HTTP请求日志

    Args:
        method: HTTP方法
        url: 请求URL
        status_code: 状态码
        duration: 请求耗时(秒)
        user_id: 用户ID
        **kwargs: 其他参数
    """
    extra_data = {
        "method": method,
        "url": url,
        "status_code": status_code,
        "duration": duration,
        "user_id": user_id,
        **kwargs,
    }

    if status_code >= 500:
        logger.error("HTTP Request", **extra_data)
    elif status_code >= 400:
        logger.warning("HTTP Request", **extra_data)
    else:
        logger.info("HTTP Request", **extra_data)


def log_database_operation(
    operation: str,
    table: str,
    duration: float,
    affected_rows: int | None = None,
    service: str | None = None,
    error: str | None = None,
    **kwargs: Any,
) -> None:
    """记录数据库操作日志"""
    log_data = {
        "operation": operation,
        "table": table,
        "duration": f"{duration:.3f}s",
        "service": service or "unknown",
    }

    if affected_rows is not None:
        log_data["affected_rows"] = str(affected_rows)

    if error:
        log_data["error"] = error
        logger.error(f"数据库操作失败: {log_data}")
    else:
        logger.info(f"数据库操作成功: {log_data}")


def log_ml_inference(
    model_name: str,
    input_shape: tuple,
    duration: float,
    success: bool = True,
    error: str | None = None,
    **kwargs: Any,
) -> None:
    """记录机器学习推理日志

    Args:
        model_name: 模型名称
        input_shape: 输入形状
        duration: 推理耗时(秒)
        success: 是否成功
        error: 错误信息
        **kwargs: 其他参数
    """
    extra_data = {
        "model_name": model_name,
        "input_shape": input_shape,
        "duration": duration,
        "success": success,
        "error": error,
        **kwargs,
    }

    if not success:
        logger.error("ML Inference Failed", **extra_data)
    elif duration > 5.0:  # 慢推理
        logger.warning("Slow ML Inference", **extra_data)
    else:
        logger.info("ML Inference", **extra_data)


def log_cache_operation(
    operation: str,
    key: str,
    hit: bool | None = None,
    duration: float | None = None,
    **kwargs: Any,
) -> None:
    """记录缓存操作日志

    Args:
        operation: 操作类型(GET, SET, DELETE)
        key: 缓存键
        hit: 是否命中(仅GET操作)
        duration: 操作耗时(秒)
        **kwargs: 其他参数
    """
    extra_data = {
        "operation": operation,
        "key": key,
        "hit": hit,
        "duration": duration,
        **kwargs,
    }

    logger.debug("Cache Operation", **extra_data)


# 初始化日志
setup_logging()
