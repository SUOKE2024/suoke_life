#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志配置和工具模块
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Union

from internal.model.config import LoggingConfig


def setup_logging(config: LoggingConfig) -> None:
    """
    配置日志系统
    
    Args:
        config: 日志配置对象
    """
    # 获取根日志器
    root_logger = logging.getLogger()
    
    # 设置日志级别
    level = getattr(logging, config.level.upper(), logging.INFO)
    root_logger.setLevel(level)
    
    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # 设置日志格式
    formatter = logging.Formatter(config.format)
    console_handler.setFormatter(formatter)
    
    # 添加控制台处理器
    root_logger.addHandler(console_handler)
    
    # 如果配置了日志文件，添加文件处理器
    if config.file:
        file_path = Path(config.file)
        
        # 确保日志目录存在
        os.makedirs(file_path.parent, exist_ok=True)
        
        # 创建轮转文件处理器
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=config.max_size_mb * 1024 * 1024,
            backupCount=config.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        
        # 添加文件处理器
        root_logger.addHandler(file_handler)
    
    # 配置特定模块的日志级别
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('grpc').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    获取命名日志器
    
    Args:
        name: 日志器名称，通常为模块名
        
    Returns:
        命名日志器
    """
    return logging.getLogger(name)


class ServiceLogger:
    """服务日志工具类，用于统一服务日志格式"""
    
    def __init__(self, name: str):
        """
        初始化日志器
        
        Args:
            name: 日志器名称
        """
        self.logger = logging.getLogger(name)
    
    def debug(self, msg: str, *args, **kwargs) -> None:
        """记录DEBUG级别日志"""
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs) -> None:
        """记录INFO级别日志"""
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs) -> None:
        """记录WARNING级别日志"""
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs) -> None:
        """记录ERROR级别日志"""
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs) -> None:
        """记录CRITICAL级别日志"""
        self.logger.critical(msg, *args, **kwargs)
    
    def exception(self, msg: str, *args, **kwargs) -> None:
        """记录异常信息"""
        self.logger.exception(msg, *args, **kwargs)
    
    def audit(self, msg: str, user_id: Optional[str] = None, 
              action: Optional[str] = None, *args, **kwargs) -> None:
        """
        记录审计日志
        
        Args:
            msg: 日志消息
            user_id: 用户ID
            action: 执行的操作
        """
        audit_msg = f"AUDIT: {msg}"
        if user_id:
            audit_msg = f"AUDIT [User: {user_id}]: {msg}"
        if action:
            audit_msg = f"AUDIT [Action: {action}]: {msg}"
        if user_id and action:
            audit_msg = f"AUDIT [User: {user_id}, Action: {action}]: {msg}"
        
        self.logger.info(audit_msg, *args, **kwargs)
    
    def transaction(self, transaction_id: str, msg: str, *args, **kwargs) -> None:
        """
        记录区块链交易日志
        
        Args:
            transaction_id: 交易ID
            msg: 日志消息
        """
        tx_msg = f"TRANSACTION [{transaction_id}]: {msg}"
        self.logger.info(tx_msg, *args, **kwargs) 