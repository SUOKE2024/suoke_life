"""
日志记录模块

该模块提供统一的日志记录功能，支持不同级别的日志和结构化输出。
"""
import json
import logging
import os
import sys
import traceback
from typing import Any, Dict, Optional, Union

# 日志级别映射
LOG_LEVEL_MAP = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

# 默认日志配置
DEFAULT_LOG_LEVEL = os.getenv("USER_SERVICE_LOG_LEVEL", "info").lower()
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.getenv("USER_SERVICE_LOG_FILE", "logs/user-service.log")

# 确保日志目录存在
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

class Logger:
    """
    日志记录器
    
    提供统一的日志记录接口，支持结构化日志输出和多种输出目标。
    """
    
    def __init__(self, name: str, level: str = DEFAULT_LOG_LEVEL):
        """
        初始化日志记录器
        
        Args:
            name: 记录器名称
            level: 日志级别
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(LOG_LEVEL_MAP.get(level, logging.INFO))
        
        # 添加控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
        self.logger.addHandler(console_handler)
        
        # 添加文件处理器
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
        self.logger.addHandler(file_handler)
    
    def _format_message(self, message: str, extra: Optional[Dict[str, Any]] = None) -> str:
        """
        格式化日志消息，支持结构化输出
        
        Args:
            message: 日志消息
            extra: 附加信息
            
        Returns:
            格式化后的消息
        """
        if not extra:
            return message
        
        try:
            extra_json = json.dumps(extra, ensure_ascii=False, default=str)
            return f"{message} | {extra_json}"
        except Exception:
            return f"{message} | (无法序列化的附加信息)"
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """
        记录调试级别日志
        
        Args:
            message: 日志消息
            extra: 附加信息
        """
        self.logger.debug(self._format_message(message, extra))
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """
        记录信息级别日志
        
        Args:
            message: 日志消息
            extra: 附加信息
        """
        self.logger.info(self._format_message(message, extra))
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """
        记录警告级别日志
        
        Args:
            message: 日志消息
            extra: 附加信息
        """
        self.logger.warning(self._format_message(message, extra))
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        """
        记录错误级别日志
        
        Args:
            message: 日志消息
            extra: 附加信息
            exc_info: 是否包含异常信息
        """
        if exc_info:
            error_info = {
                "traceback": traceback.format_exc()
            }
            if extra:
                extra.update(error_info)
            else:
                extra = error_info
        
        self.logger.error(self._format_message(message, extra))
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = True):
        """
        记录严重错误级别日志
        
        Args:
            message: 日志消息
            extra: 附加信息
            exc_info: 是否包含异常信息
        """
        if exc_info:
            error_info = {
                "traceback": traceback.format_exc()
            }
            if extra:
                extra.update(error_info)
            else:
                extra = error_info
        
        self.logger.critical(self._format_message(message, extra))

# 创建默认日志记录器
default_logger = Logger("user_service")

def get_logger(name: str) -> Logger:
    """
    获取指定名称的日志记录器
    
    Args:
        name: 记录器名称
        
    Returns:
        日志记录器
    """
    return Logger(name) 