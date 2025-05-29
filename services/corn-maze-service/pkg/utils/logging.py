#!/usr/bin/env python3

"""
日志配置工具
"""

import logging
import logging.handlers
from pathlib import Path
import sys
from typing import Any

from pkg.utils.config import get_value


def setup_logging(_config: dict[str, Any] | None = None) -> None:
    """
    配置日志系统

    Args:
        _config: 配置字典，如果为None则使用配置模块加载（当前未使用）
    """
    # 获取日志配置
    level_name = get_value("logging.level", "INFO")
    log_format = get_value("logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_file = get_value("logging.file", "logs/corn-maze-service.log")
    max_size = get_value("logging.max_size", 10 * 1024 * 1024)  # 默认10MB
    backup_count = get_value("logging.backup_count", 5)
    stdout = get_value("logging.stdout", True)

    # 设置根日志记录器
    root_logger = logging.getLogger()

    # 清除现有处理程序
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 设置日志级别
    level = getattr(logging, level_name.upper(), logging.INFO)
    root_logger.setLevel(level)

    # 创建格式器
    formatter = logging.Formatter(log_format)

    # 添加文件处理程序
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # 创建滚动文件处理程序
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # 添加控制台处理程序
    if stdout:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # 设置第三方库的日志级别
    # 这些库通常很嘈杂，我们降低他们的日志级别
    quiet_loggers = ["aiosqlite", "grpc._cython", "grpc_reflection"]
    for logger_name in quiet_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    logging.getLogger(__name__).info(f"日志系统初始化完成, 级别: {level_name}")


def get_logger(name: str) -> logging.Logger:
    """
    获取命名日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        logging.Logger: 日志记录器
    """
    return logging.getLogger(name)


class RequestLogger:
    """请求日志记录器"""

    def __init__(self, method_name: str):
        """
        初始化请求日志记录器

        Args:
            method_name: 请求方法名
        """
        self.logger = logging.getLogger(f"grpc.{method_name}")
        self.method_name = method_name

    def __enter__(self):
        """进入上下文"""
        self.logger.info(f"开始处理请求: {self.method_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        if exc_type:
            self.logger.error(f"请求处理失败: {self.method_name}, 错误: {exc_val}", exc_info=True)
        else:
            self.logger.info(f"请求处理完成: {self.method_name}")

        return False  # 不抑制异常
