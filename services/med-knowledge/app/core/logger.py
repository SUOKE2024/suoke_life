import os
import sys
from functools import lru_cache
from typing import Dict

from loguru import logger

from app.core.config import LoggingSettings


@lru_cache()
def setup_logger(config: LoggingSettings):
    """配置日志系统"""
    # 移除默认处理器
    logger.remove()

    # 确定日志级别
    log_level = config.level.upper()

    # 配置日志格式
    log_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}"
    )
    if config.format.lower() == "json":
        log_format = (
            '{"time":"{time:YYYY-MM-DD HH:mm:ss.SSS}","level":"{level}","name":"{name}",'
            '"function":"{function}","line":"{line}","message":"{message}"}'
        )

    # 配置输出
    if config.output.lower() == "file" and config.file_path:
        # 确保日志目录存在
        log_dir = os.path.dirname(config.file_path)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        logger.add(
            config.file_path,
            level=log_level,
            format=log_format,
            rotation="10 MB",
            compression="zip",
            retention="1 week",
        )
    else:
        logger.add(sys.stderr, level=log_level, format=log_format)

    return logger


@lru_cache()
def get_logger():
    """获取日志记录器"""
    from app.core.config import get_settings
    
    settings = get_settings()
    return setup_logger(settings.logging)