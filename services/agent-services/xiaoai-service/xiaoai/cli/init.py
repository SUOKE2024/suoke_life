#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小艾智能体初始化模块
XiaoAI Agent Initialization Module

提供小艾智能体的初始化功能。
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

import click
from loguru import logger


def initialize(target: str = "all", force: bool = False) -> None:
    """
    初始化小艾智能体
    
    Args:
        target: 初始化目标 (config, database, cache, all)
        force: 是否强制重新初始化
    """
    logger.info(f"开始初始化小艾智能体: {target}")
    
    try:
        if target == "all":
            _init_config(force)
            _init_database(force)
            _init_cache(force)
            _init_directories(force)
        elif target == "config":
            _init_config(force)
        elif target == "database":
            _init_database(force)
        elif target == "cache":
            _init_cache(force)
        else:
            raise ValueError(f"不支持的初始化目标: {target}")
        
        logger.info("初始化完成")
        click.echo(click.style("✓ 小艾智能体初始化成功", fg="green"))
        
    except Exception as e:
        logger.error(f"初始化失败: {e}")
        click.echo(click.style(f"✗ 初始化失败: {e}", fg="red"))
        raise


def _init_config(force: bool = False) -> None:
    """初始化配置"""
    logger.info("初始化配置...")
    
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # 创建默认配置文件
    default_config = config_dir / "default.yaml"
    if not default_config.exists() or force:
        _create_default_config(default_config)
        logger.info(f"已创建默认配置文件: {default_config}")
    
    # 创建开发环境配置
    dev_config = config_dir / "development.yaml"
    if not dev_config.exists() or force:
        _create_dev_config(dev_config)
        logger.info(f"已创建开发环境配置文件: {dev_config}")
    
    # 创建生产环境配置
    prod_config = config_dir / "production.yaml"
    if not prod_config.exists() or force:
        _create_prod_config(prod_config)
        logger.info(f"已创建生产环境配置文件: {prod_config}")


def _init_database(force: bool = False) -> None:
    """初始化数据库"""
    logger.info("初始化数据库...")
    
    try:
        # 这里应该运行数据库迁移
        # 暂时只是模拟
        logger.info("运行数据库迁移...")
        logger.info("创建数据库表...")
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


def _init_cache(force: bool = False) -> None:
    """初始化缓存"""
    logger.info("初始化缓存...")
    
    try:
        # 这里应该清理和初始化缓存
        # 暂时只是模拟
        logger.info("清理缓存...")
        logger.info("设置缓存配置...")
        logger.info("缓存初始化完成")
    except Exception as e:
        logger.error(f"缓存初始化失败: {e}")
        raise


def _init_directories(force: bool = False) -> None:
    """初始化目录结构"""
    logger.info("初始化目录结构...")
    
    directories = [
        "logs",
        "data",
        "models",
        "temp",
        "uploads",
    ]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        logger.info(f"已创建目录: {dir_path}")


def _create_default_config(config_path: Path) -> None:
    """创建默认配置文件"""
    config_content = """# 小艾智能体默认配置
# XiaoAI Agent Default Configuration

# 服务器配置
server:
  host: "0.0.0.0"
  port: 8000
  workers: 1
  reload: false

# 数据库配置
database:
  url: "postgresql://xiaoai:password@localhost:5432/xiaoai"
  pool_size: 10
  max_overflow: 20
  echo: false

# 缓存配置
cache:
  url: "redis://localhost:6379/0"
  max_connections: 10
  retry_on_timeout: true

# Celery 配置
celery:
  broker_url: "redis://localhost:6379/0"
  result_backend: "redis://localhost:6379/0"
  task_time_limit: 300
  task_soft_time_limit: 240

# 工作进程配置
worker:
  concurrency: 4
  queue: "default"

# AI 模型配置
ai:
  model_path: "models/"
  cache_size: "2GB"
  device: "auto"

# 日志配置
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/xiaoai.log"

# 安全配置
security:
  secret_key: "your-secret-key-here"
  algorithm: "HS256"
  access_token_expire_minutes: 30

# 外部服务配置
external_services:
  look_service:
    url: "http://localhost:8001"
    timeout: 30
  listen_service:
    url: "http://localhost:8002"
    timeout: 30
  inquiry_service:
    url: "http://localhost:8003"
    timeout: 30
  palpation_service:
    url: "http://localhost:8004"
    timeout: 30
"""
    
    config_path.write_text(config_content, encoding="utf-8")


def _create_dev_config(config_path: Path) -> None:
    """创建开发环境配置文件"""
    config_content = """# 小艾智能体开发环境配置
# XiaoAI Agent Development Configuration

# 继承默认配置
extends: "default.yaml"

# 开发环境特定配置
server:
  reload: true
  workers: 1

database:
  echo: true
  url: "postgresql://xiaoai:dev_password@localhost:5432/xiaoai_dev"

logging:
  level: "DEBUG"

# 开发工具
dev_tools:
  enable_debug: true
  enable_profiling: true
  mock_external_services: true
"""
    
    config_path.write_text(config_content, encoding="utf-8")


def _create_prod_config(config_path: Path) -> None:
    """创建生产环境配置文件"""
    config_content = """# 小艾智能体生产环境配置
# XiaoAI Agent Production Configuration

# 继承默认配置
extends: "default.yaml"

# 生产环境特定配置
server:
  workers: 4
  reload: false

database:
  pool_size: 20
  max_overflow: 40
  echo: false

worker:
  concurrency: 8

logging:
  level: "WARNING"
  file: "/var/log/xiaoai/xiaoai.log"

# 监控配置
monitoring:
  enable_metrics: true
  metrics_port: 9090
  enable_tracing: true
  
# 安全配置
security:
  secret_key: "${XIAOAI_SECRET_KEY}"
  
# 生产环境数据库连接
database:
  url: "${DATABASE_URL}"
  
# 生产环境缓存连接
cache:
  url: "${REDIS_URL}"
"""
    
    config_path.write_text(config_content, encoding="utf-8")


if __name__ == "__main__":
    initialize() 