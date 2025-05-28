#!/usr/bin/env python3
"""
日志配置模块
Logging Configuration Module
"""

import logging
import logging.handlers
import sys
from datetime import UTC
from pathlib import Path
from typing import Any


def setup_logging(config: dict[str, Any]):
    """
    设置日志配置

    Args:
        config: 日志配置字典
    """
    # 获取配置参数
    level = config.get("level", "INFO").upper()
    format_type = config.get("format", "simple")
    log_file = config.get("file")
    max_size = config.get("max_size", "100MB")
    backup_count = config.get("backup_count", 5)
    console_output = config.get("console_output", True)

    # 设置日志级别
    log_level = getattr(logging, level, logging.INFO)

    # 创建根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 创建格式化器
    if format_type == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # 控制台输出
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # 文件输出
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # 解析文件大小
        max_bytes = _parse_size(max_size)

        # 创建轮转文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # 设置第三方库日志级别
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)


def _parse_size(size_str: str) -> int:
    """
    解析大小字符串

    Args:
        size_str: 大小字符串，如 "100MB"

    Returns:
        字节数
    """
    size_str = size_str.upper()

    if size_str.endswith("KB"):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith("MB"):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith("GB"):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        return int(size_str)


class JsonFormatter(logging.Formatter):
    """JSON 格式化器"""

    def format(self, record):
        """格式化日志记录为 JSON"""
        import json
        from datetime import datetime

        log_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加异常信息
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # 添加额外字段
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "agent_id"):
            log_entry["agent_id"] = record.agent_id

        return json.dumps(log_entry, ensure_ascii=False)


def get_logger(name: str) -> logging.Logger:
    """
    获取日志器

    Args:
        name: 日志器名称

    Returns:
        日志器实例
    """
    return logging.getLogger(name)
