"""
日志工具模块

提供统一的日志配置和管理功能。
"""

import logging
import sys
from pathlib import Path

from ..config.settings import get_settings


def setup_logging(
    level: str | None = None,
    format_type: str | None = None,
    log_file: str | None = None
) -> None:
    """设置日志配置

    Args:
        level: 日志级别
        format_type: 日志格式类型 ('json' 或 'text')
        log_file: 日志文件路径
    """
    settings = get_settings()

    # 使用参数或配置中的值
    log_level = level or settings.monitoring.log_level
    log_format = format_type or settings.monitoring.log_format
    log_file_path = log_file or settings.monitoring.log_file

    # 设置日志级别
    logging.basicConfig(level=getattr(logging, log_level.upper()))

    # 创建根日志器
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # 设置日志格式
    if log_format.lower() == 'json':
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": "%(message)s", '
            '"module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 文件处理器
    if log_file_path:
        log_path = Path(log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """获取日志器实例

    Args:
        name: 日志器名称

    Returns:
        日志器实例
    """
    return logging.getLogger(name)


# 在模块加载时自动设置日志
setup_logging()
