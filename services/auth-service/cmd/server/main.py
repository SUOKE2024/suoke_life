#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
索克生活APP认证服务
主入口文件

该服务提供用户认证、授权和访问控制功能，是索克生活APP微服务系统的核心服务之一。
"""
import asyncio
import logging
import os
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

# 将项目根目录添加到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from internal.delivery.rest.routes import register_routes
from internal.delivery.grpc.server import serve as serve_grpc
from internal.repository.init_db import init_database
from internal.service.startup import setup_dependencies
from internal.observability.health import HealthCheck
from internal.observability.metrics import setup_metrics
from internal.observability.tracing import setup_tracing
from pkg.logging.logger import setup_logging
from pkg.utils.config import load_config

# 创建FastAPI应用
app = FastAPI(
    title="索克生活APP认证服务",
    description="提供用户认证、授权和访问控制功能",
    version="1.0.0",
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化操作"""
    # 加载配置
    config = load_config()
    app.state.config = config
    
    # 设置日志
    setup_logging(config.logging.level, config.logging.format)
    
    # 设置指标收集
    setup_metrics(app, "1.0.0", {
        "name": "auth-service",
        "environment": config.environment
    })
    
    # 设置链路追踪
    setup_tracing(app, config.tracing)
    
    # 初始化数据库
    await init_database(config.database)
    
    # 设置依赖项
    await setup_dependencies(app, config)
    
    # 创建健康检查服务
    app.state.health_checker = HealthCheck(app)
    
    # 启动gRPC服务器（在后台运行）
    asyncio.create_task(serve_grpc(config.grpc.port))
    
    logging.info("认证服务启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理操作"""
    # 关闭数据库连接
    if hasattr(app.state, "db_pool"):
        await app.state.db_pool.close()
    
    # 关闭Redis连接
    if hasattr(app.state, "redis_pool"):
        await app.state.redis_pool.close()
    
    # 关闭Pulsar连接
    if hasattr(app.state, "pulsar_client"):
        app.state.pulsar_client.close()
    
    logging.info("认证服务已关闭")

# 注册路由
register_routes(app)

# 添加健康检查端点
@app.get("/health", tags=["健康检查"])
async def health_check():
    """全面健康检查"""
    return await app.state.health_checker.full_health_check()

@app.get("/health/live", tags=["健康检查"])
async def liveness_check():
    """存活检查"""
    return await app.state.health_checker.liveness_check()

@app.get("/health/ready", tags=["健康检查"])
async def readiness_check():
    """就绪检查"""
    return await app.state.health_checker.readiness_check()

# 添加全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logging.error(f"全局异常: {str(exc)}", exc_info=exc)
    
    return Response(
        content=f"服务器内部错误: {str(exc)}",
        status_code=500
    )

if __name__ == "__main__":
    # 获取配置
    port = int(os.environ.get("PORT", "8080"))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    
    # 启动服务
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    )