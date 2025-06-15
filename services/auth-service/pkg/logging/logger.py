#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日志设置模块

提供日志格式化、级别设置和输出配置功能。
"""
import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", log_format: str = "simple") -> None:
    """
    设置日志配置
    
    Args:
        level: 日志级别，默认为INFO
        log_format: 日志格式，默认为simple，可选json
    """
    # 设置日志级别
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 清除现有处理器
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)
    
    # 创建处理器
    handler = logging.StreamHandler(sys.stdout)
    
    # 设置格式
    if log_format.lower() == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    
    # 禁用第三方库的一些过于详细的日志
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


class JsonFormatter(logging.Formatter):
    """JSON格式的日志格式化器"""
    
    def format(self, record):
        """格式化日志记录为JSON格式"""
        import json
        from datetime import datetime
        
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        
        # 添加异常信息（如果存在）
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        # 添加自定义属性（如果存在）
        for key, value in record.__dict__.items():
            if key not in ["args", "asctime", "created", "exc_info", "exc_text", 
                          "filename", "funcName", "id", "levelname", "levelno", 
                          "lineno", "module", "msecs", "message", "msg", "name", 
                          "pathname", "process", "processName", "relativeCreated", 
                          "stack_info", "thread", "threadName"]:
                log_data[key] = value
        
        return json.dumps(log_data) 