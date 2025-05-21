#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import json
from datetime import datetime


class JsonFormatter(logging.Formatter):
    """JSON格式日志格式化器"""
    
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, "service_name"):
            log_record["service"] = record.service_name
            
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        if hasattr(record, "trace_id"):
            log_record["trace_id"] = record.trace_id
            
        if hasattr(record, "span_id"):
            log_record["span_id"] = record.span_id
        
        return json.dumps(log_record)


def setup_logger(config):
    """
    配置全局日志记录器
    
    Args:
        config: 日志配置
            level: 日志级别
            format: 日志格式（text或json）
            output: 日志输出位置（stdout, stderr或file）
            file_path: 日志文件路径（仅当output为file时有效）
    
    Returns:
        logging.Logger: 配置好的根日志记录器
    """
    # 获取根日志记录器
    root_logger = logging.getLogger()
    
    # 清除已有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 设置日志级别
    level = getattr(logging, config.level.upper(), logging.INFO)
    root_logger.setLevel(level)
    
    # 创建处理器
    if config.output.lower() == "stdout":
        handler = logging.StreamHandler(sys.stdout)
    elif config.output.lower() == "stderr":
        handler = logging.StreamHandler(sys.stderr)
    elif config.output.lower() == "file":
        # 确保日志目录存在
        log_dir = os.path.dirname(config.file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 创建按大小轮转的文件处理器
        handler = RotatingFileHandler(
            config.file_path, 
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
    else:
        handler = logging.StreamHandler(sys.stdout)
    
    # 创建格式化器
    if config.format.lower() == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    
    # 添加一个特殊的处理器，将错误以上级别的日志同时输出到stderr
    if config.output.lower() != "stderr":
        error_handler = logging.StreamHandler(sys.stderr)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
    
    return root_logger 