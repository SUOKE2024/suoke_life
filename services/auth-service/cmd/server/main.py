#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证服务主模块

提供服务启动点，处理配置加载、路由和中间件注册等功能。
"""
import asyncio
import logging
import os
import sys

import uvicorn
from fastapi import FastAPI

# 临时修复导入问题
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from internal.delivery.rest.routes import register_routes
#from internal.observability.health import HealthCheck
#from internal.observability.metrics import setup_metrics
#from internal.observability.tracing import setup_tracing
#from internal.service.startup import setup_dependencies
#from pkg.logging.logger import setup_logging
#from pkg.utils.config import load_config


async def main():
    """
    认证服务主函数
    
    加载配置、设置日志、初始化FastAPI应用并启动服务。
    """
    # 设置基本日志
    logging.basicConfig(level=logging.INFO)
    logging.info("正在启动认证服务...")
    
    # 创建FastAPI应用
    app = FastAPI(
        title="认证服务API",
        description="提供用户认证、授权和账户管理功能",
        version="0.1.0",
    )
    
    # 注册REST路由
    register_routes(app)
    
    # 启动应用
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())