#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
老克智能体服务 - 日志工具
配置结构化日志记录和文件输出
"""

import os
import sys
import json
import logging
import logging.handlers
from typing import Optional, Dict, Any, Union
from datetime import datetime

from .config import Config

def setup_logger(logger: logging.Logger, level: str = "INFO") -> None:
    """
    设置日志记录器
    
    Args:
        logger: 日志记录器实例
        level: 日志级别
    """
    # 转换日志级别字符串为常量
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # 清除可能存在的处理器
    if logger.handlers:
        logger.handlers.clear()
    
    # 设置日志级别
    logger.setLevel(numeric_level)
    
    # 加载配置
    config = Config()
    log_config = config.get_section("logging")
    
    # 获取日志格式
    log_format = log_config.get("format", "json")
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # 设置格式化器
    if log_format.lower() == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(name)s] %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 如果配置了文件日志，添加文件处理器
    log_file = log_config.get("file_path")
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 获取轮换设置
        rotation_size = log_config.get("rotation", 10) * 1024 * 1024  # MB转字节
        backup_count = log_config.get("backups", 5)
        
        # 创建轮换文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=rotation_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # 避免日志被父级记录器重复记录
    logger.propagate = False
    
    logger.debug(f"日志记录器已配置，级别: {level}, 格式: {log_format}")

class JsonFormatter(logging.Formatter):
    """
    JSON格式的日志格式化器
    将日志记录格式化为结构化的JSON字符串
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录为JSON字符串
        
        Args:
            record: 日志记录
            
        Returns:
            str: JSON格式的日志字符串
        """
        # 基本日志信息
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        # 添加额外的上下文信息
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        # 添加其他额外信息
        for key, value in record.__dict__.items():
            if key not in ["args", "exc_info", "exc_text", "msg", "message", "levelname", 
                          "levelno", "pathname", "filename", "module", "name", "lineno", 
                          "funcName", "created", "asctime", "msecs", "relativeCreated",
                          "thread", "threadName", "processName", "process"]:
                log_data[key] = value
        
        return json.dumps(log_data)

def get_logger(name: str, level: str = None) -> logging.Logger:
    """
    获取指定名称的记录器
    
    Args:
        name: 记录器名称
        level: 日志级别，如果为None则使用配置中的值
        
    Returns:
        logging.Logger: 日志记录器实例
    """
    logger = logging.getLogger(name)
    
    # 如果未指定级别，从配置中获取
    if level is None:
        config = Config()
        level = config.get("logging.level", "INFO")
    
    # 设置记录器
    setup_logger(logger, level)
    
    return logger 