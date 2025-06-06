"""
logging - 索克生活项目模块
"""

from loguru import logger
from typing import Dict, Any
import logging
import os
import sys

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志配置工具
"""



class InterceptHandler(logging.Handler):
    """
    将标准库logging记录转发到loguru的处理程序
    """
    
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
            
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
            
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(config: Dict[str, Any]):
    """
    配置日志
    
    Args:
        config: 日志配置字典
    """
    # 提取日志配置
    log_level = config.get('level', 'INFO')
    log_format = config.get('format', '{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}')
    log_file = config.get('file')
    
    # 移除默认的日志处理器
    logger.remove()
    
    # 添加控制台日志处理器
    logger.add(
        sys.stdout,
        format=log_format,
        level=log_level,
        colorize=True
    )
    
    # 如果配置了日志文件，则添加文件日志处理器
    if log_file:
        # 确保日志目录存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logger.add(
            log_file,
            format=log_format,
            level=log_level,
            rotation="500 MB",   # 日志文件达到500MB时轮转
            retention="10 days"  # 保留10天的日志
        )
    
    # 替换标准库的日志处理器
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    
    # 替换常见库的日志处理器
    for logger_name in (
        "uvicorn", "uvicorn.error", "uvicorn.access", 
        "fastapi", "gunicorn", "gunicorn.error", "gunicorn.access",
        "grpc", "elasticsearch", "httpx"
    ):
        lib_logger = logging.getLogger(logger_name)
        lib_logger.handlers = [InterceptHandler()]
        lib_logger.propagate = False
    
    logger.info(f"日志已配置，级别: {log_level}")
    
    return logger