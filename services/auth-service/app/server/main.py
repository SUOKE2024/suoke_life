#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证服务主入口

启动FastAPI应用服务器。
"""
import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
import time

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from internal.config.settings import get_settings
from internal.service.metrics_service import get_metrics_service
from internal.delivery.rest.auth_handler import router as auth_router
from internal.delivery.rest.user_handler import router as user_router
from internal.delivery.rest.admin_handler import router as admin_router
from internal.delivery.rest.health_handler import router as health_router


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("认证服务启动中...")
    
    # 初始化指标服务
    metrics_service = get_metrics_service()
    
    # 启动后台任务
    async def collect_metrics_task():
        while True:
            try:
                await metrics_service.collect_all_metrics()
                await asyncio.sleep(60)  # 每分钟收集一次指标
            except Exception as e:
                logger.error(f"指标收集失败: {e}")
                await asyncio.sleep(60)
    
    # 创建后台任务
    metrics_task = asyncio.create_task(collect_metrics_task())
    
    logger.info("认证服务启动完成")
    
    yield
    
    # 关闭时执行
    logger.info("认证服务关闭中...")
    metrics_task.cancel()
    try:
        await metrics_task
    except asyncio.CancelledError:
        pass
    logger.info("认证服务已关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    settings = get_settings()
    
    # 创建FastAPI应用
    app = FastAPI(
        title="索克生活认证服务",
        description="提供用户认证、授权和用户管理功能",
        version="1.0.0",
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
        lifespan=lifespan
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 添加受信任主机中间件
    if settings.environment == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*.suokelife.com"]
        )
    
    # 添加请求处理中间件
    @app.middleware("http")
    async def process_request(request: Request, call_next):
        start_time = time.time()
        
        # 记录请求开始
        logger.info(f"请求开始: {request.method} {request.url}")
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录指标
        metrics_service = get_metrics_service()
        metrics_service.record_request_duration(
            process_time,
            request.method,
            str(request.url.path)
        )
        
        # 添加响应头
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Service"] = "auth-service"
        
        # 记录请求完成
        logger.info(
            f"请求完成: {request.method} {request.url} - "
            f"状态码: {response.status_code} - "
            f"处理时间: {process_time:.4f}s"
        )
        
        return response
    
    # 添加全局异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"未处理的异常: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "内部服务器错误",
                "message": "服务暂时不可用，请稍后重试",
                "request_id": getattr(request.state, "request_id", None)
            }
        )
    
    # 注册路由
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["认证"])
    app.include_router(user_router, prefix="/api/v1/users", tags=["用户"])
    app.include_router(admin_router, prefix="/api/v1/admin", tags=["管理"])
    app.include_router(health_router, prefix="/health", tags=["健康检查"])
    
    # 添加根路径
    @app.get("/")
    async def root():
        return {
            "service": "索克生活认证服务",
            "version": "1.0.0",
            "status": "运行中",
            "docs": "/docs" if settings.environment != "production" else "不可用"
        }
    
    # 初始化Prometheus指标
    if settings.enable_metrics:
        instrumentator = Instrumentator()
        instrumentator.instrument(app).expose(app)
    
    return app


def main():
    """主函数"""
    settings = get_settings()
    
    # 创建应用
    app = create_app()
    
    # 启动服务器
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        reload=settings.environment == "development",
        workers=1 if settings.environment == "development" else settings.workers
    )


if __name__ == "__main__":
    main()