#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小艾智能体服务器启动模块
XiaoAI Agent Server Module

提供小艾智能体的服务器启动和管理功能。
"""

from __future__ import annotations

import asyncio
import signal
import sys
from pathlib import Path
from typing import Optional

import uvicorn
from loguru import logger

from xiaoai.config.dynamic_config_manager import DynamicConfigManager


def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    workers: int = 1,
    reload: bool = False,
    config: Optional[str] = None,
) -> None:
    """
    启动小艾智能体服务器
    
    Args:
        host: 服务器绑定地址
        port: 服务器端口
        workers: 工作进程数量
        reload: 是否启用自动重载
        config: 配置文件路径
    """
    # 加载配置
    config_manager = DynamicConfigManager()
    if config:
        config_path = Path(config)
        if config_path.exists():
            config_manager.load_config(config_path)
            logger.info(f"已加载配置文件: {config_path}")
    
    # 获取服务器配置
    server_config = config_manager.get_section("server", {})
    
    # 合并配置
    final_host = server_config.get("host", host)
    final_port = server_config.get("port", port)
    final_workers = server_config.get("workers", workers)
    
    logger.info(f"启动小艾智能体服务器")
    logger.info(f"地址: {final_host}:{final_port}")
    logger.info(f"工作进程: {final_workers}")
    logger.info(f"自动重载: {reload}")
    
    # 设置信号处理
    def signal_handler(signum: int, frame) -> None:
        logger.info(f"收到信号 {signum}，正在关闭服务器...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动服务器
    try:
        uvicorn.run(
            "xiaoai.delivery.app:create_app",
            factory=True,
            host=final_host,
            port=final_port,
            workers=final_workers if not reload else 1,
            reload=reload,
            reload_dirs=["xiaoai"] if reload else None,
            log_level="info",
            access_log=True,
            use_colors=True,
            loop="asyncio",
        )
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_server() 