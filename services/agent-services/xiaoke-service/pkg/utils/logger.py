#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志工具
提供统一的日志配置和辅助函数
"""

import os
import logging
import logging.handlers
import json
from typing import Dict, Any, Optional


def setup_logger(
    service_name: str = "xiaoke-service",
    log_level: str = None,
    log_file: str = None,
    log_format: str = None,
) -> logging.Logger:
    """
    设置日志记录器

    Args:
        service_name: 服务名称
        log_level: 日志级别
        log_file: 日志文件路径
        log_format: 日志格式

    Returns:
        配置好的日志记录器
    """
    # 从环境变量读取配置
    log_level = log_level or os.getenv("LOG_LEVEL", "INFO")
    log_file = log_file or os.getenv("LOG_FILE", "logs/xiaoke-service.log")

    # 确保日志目录存在
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # 设置日志级别
    level = getattr(logging, log_level)

    # 创建记录器
    logger = logging.getLogger(service_name)
    logger.setLevel(level)

    # 如果已经有处理器，先清空
    if logger.handlers:
        logger.handlers = []

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # 文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(level)

    # 设置日志格式
    if log_format == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 添加处理器
    logger.addHandler(console_handler)
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
