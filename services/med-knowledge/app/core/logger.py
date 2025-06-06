"""
logger - 索克生活项目模块
"""

    from app.core.config import get_settings
from app.core.config import LoggingSettings
from loguru import logger
import os
import sys




# 全局 logger 实例
_logger_instance = None


def setup_logger(config: LoggingSettings):
    """配置日志系统"""
    global _logger_instance

    if _logger_instance is not None:
        return _logger_instance

    # 移除默认处理器
    logger.remove()

    # 确定日志级别
    log_level = config.level.upper()

    # 配置日志格式
    log_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}"
    if config.format.lower() == "json":
        log_format = (
            '{{"time":"{time:YYYY-MM-DD HH:mm:ss.SSS}","level":"{level}","name":"{name}",'
            '"function":"{function}","line":"{line}","message":"{message}"}}'
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

    _logger_instance = logger
    return logger


def get_logger():
    """获取日志记录器"""
    global _logger_instance

    if _logger_instance is not None:
        return _logger_instance


    settings = get_settings()
    return setup_logger(settings.logging)
