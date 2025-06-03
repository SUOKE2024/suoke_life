#!/usr/bin/env python3

"""
日志工具
提供统一的日志配置和管理
"""

import json
import logging
import sys
from pathlib import Path

def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: str | None = None,
    format_string: str | None = None,
) -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别
        log_file: 日志文件路径
        format_string: 日志格式字符串

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)

    # 如果日志文件路径存在, 确保日志目录存在
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # 设置日志级别
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    logger.setLevel(level_map.get(level.upper(), logging.INFO))

    # 如果已经有处理器, 先清空
    if logger.handlers:
        logger.handlers = []

    # 创建格式化器
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(format_string)

    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 如果指定了日志文件, 创建文件处理器
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

class JsonFormatter(logging.Formatter):
    """JSON格式日志格式化器"""

    def format(self, record):
        """格式化日志记录"""
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }

        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 添加额外字段
        for key, value in record.__dict__.items():
            if key not in [
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "id",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            ]:
                log_data[key] = value

        return json.dumps(log_data)

def log_request(logger, request_id, method, endpoint, payload=None):
    """记录API请求"""
    logger.info(
        "API请求",
        extra={
            "request_id": request_id,
            "method": method,
            "endpoint": endpoint,
            "payload": payload,
        },
    )

def log_response(logger, request_id, status_code, response_body=None):
    """记录API响应"""
    logger.info(
        "API响应",
        extra={
            "request_id": request_id,
            "status_code": status_code,
            "response": response_body,
        },
    )

def log_error(logger, request_id, error_message, exception=None):
    """记录错误信息"""
    logger.error(
        error_message,
        extra={
            "request_id": request_id,
            "exception": str(exception) if exception else None,
        },
        exc_info=bool(exception),
    )
