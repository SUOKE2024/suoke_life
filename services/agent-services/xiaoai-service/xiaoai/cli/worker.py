#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小艾智能体工作进程模块
XiaoAI Agent Worker Module

提供小艾智能体的后台工作进程管理功能。
"""

from __future__ import annotations

import signal
import sys
from pathlib import Path
from typing import Optional

from celery import Celery
from loguru import logger

from xiaoai.config.dynamic_config_manager import DynamicConfigManager


def create_celery_app(config_manager: DynamicConfigManager) -> Celery:
    """
    创建 Celery 应用实例
    
    Args:
        config_manager: 配置管理器
        
    Returns:
        Celery 应用实例
    """
    # 获取 Celery 配置
    celery_config = config_manager.get_section("celery", {})
    
    # 创建 Celery 应用
    app = Celery(
        "xiaoai-worker",
        broker=celery_config.get("broker_url", "redis://localhost:6379/0"),
        backend=celery_config.get("result_backend", "redis://localhost:6379/0"),
    )
    
    # 配置 Celery
    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="Asia/Shanghai",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=celery_config.get("task_time_limit", 300),  # 5分钟
        task_soft_time_limit=celery_config.get("task_soft_time_limit", 240),  # 4分钟
        worker_prefetch_multiplier=celery_config.get("worker_prefetch_multiplier", 1),
        worker_max_tasks_per_child=celery_config.get("worker_max_tasks_per_child", 1000),
        worker_disable_rate_limits=celery_config.get("worker_disable_rate_limits", False),
        result_expires=celery_config.get("result_expires", 3600),  # 1小时
    )
    
    # 自动发现任务
    app.autodiscover_tasks([
        "xiaoai.service.tasks",
        "xiaoai.four_diagnosis.tasks", 
        "xiaoai.agent.tasks",
        "xiaoai.integration.tasks",
    ])
    
    return app


def run_worker(
    concurrency: int = 4,
    queue: str = "default",
    config: Optional[str] = None,
) -> None:
    """
    启动小艾智能体工作进程
    
    Args:
        concurrency: 并发工作数量
        queue: 队列名称
        config: 配置文件路径
    """
    # 加载配置
    config_manager = DynamicConfigManager()
    if config:
        config_path = Path(config)
        if config_path.exists():
            config_manager.load_config(config_path)
            logger.info(f"已加载配置文件: {config_path}")
    
    # 获取工作进程配置
    worker_config = config_manager.get_section("worker", {})
    
    # 合并配置
    final_concurrency = worker_config.get("concurrency", concurrency)
    final_queue = worker_config.get("queue", queue)
    
    logger.info(f"启动小艾智能体工作进程")
    logger.info(f"并发数: {final_concurrency}")
    logger.info(f"队列: {final_queue}")
    
    # 创建 Celery 应用
    app = create_celery_app(config_manager)
    
    # 设置信号处理
    def signal_handler(signum: int, frame) -> None:
        logger.info(f"收到信号 {signum}，正在关闭工作进程...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动工作进程
    try:
        app.worker_main([
            "worker",
            f"--concurrency={final_concurrency}",
            f"--queues={final_queue}",
            "--loglevel=info",
            "--without-gossip",
            "--without-mingle",
            "--without-heartbeat",
        ])
    except Exception as e:
        logger.error(f"工作进程启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_worker() 