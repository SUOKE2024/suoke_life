#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服务启动依赖设置模块

初始化和配置服务所需的依赖项。
"""
import logging

from fastapi import FastAPI


async def setup_dependencies(app: FastAPI, config) -> None:
    """
    设置服务依赖
    
    Args:
        app: FastAPI应用实例
        config: 配置对象
    """
    logging.info("设置服务依赖")
    
    # 存储配置到应用状态
    app.state.config = config
    
    # 注册健康检查依赖项
    if hasattr(app.state, "health_checker") and hasattr(app.state, "db_pool"):
        app.state.health_checker.register_dependency(
            "database",
            lambda: check_database(app.state.db_pool)
        )
    
    logging.info("服务依赖设置完成")


async def check_database(db_pool):
    """
    检查数据库连接是否正常
    
    Args:
        db_pool: 数据库连接池
        
    Returns:
        bool: 数据库是否可用
    """
    try:
        async with db_pool.acquire() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logging.error(f"数据库健康检查失败: {str(e)}")
        return False 