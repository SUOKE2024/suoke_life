#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
人工审核服务主入口

启动FastAPI应用服务器，提供AI辅助的人工审核功能
"""
import asyncio
import logging
import signal
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from internal.config.settings import get_settings
from internal.database.connection import init_database, close_database
from internal.redis.connection import init_redis, close_redis
from internal.tasks.celery_app import init_celery
from internal.observability.logging_config import setup_logging
from internal.observability.metrics import setup_metrics
from internal.observability.tracing import setup_tracing
from api.rest.review_api import router as review_router
from api.rest.ai_api import router as ai_router
from api.rest.workflow_api import router as workflow_router
from api.rest.admin_api import router as admin_router
from api.rest.health_api import router as health_router

# 配置日志
logger = logging.getLogger(__name__)

# 全局变量
shutdown_event = asyncio.Event()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    settings = get_settings()
    
    # 启动时执行
    logger.info("人工审核服务启动中...")
    
    try:
        # 初始化数据库连接
        await init_database()
        logger.info("数据库连接初始化完成")
        
        # 初始化Redis连接
        await init_redis()
        logger.info("Redis连接初始化完成")
        
        # 初始化Celery
        init_celery()
        logger.info("Celery初始化完成")
        
        # 设置监控
        if settings.monitoring.metrics_enabled:
            setup_metrics(app)
            logger.info("指标收集初始化完成")
        
        if settings.monitoring.tracing_enabled:
            setup_tracing(app)
            logger.info("链路追踪初始化完成")
        
        # 启动后台任务
        background_tasks = []
        
        # 健康检查任务
        async def health_check_task():
            while not shutdown_event.is_set():
                try:
                    # 执行健康检查逻辑
                    await asyncio.sleep(30)  # 每30秒检查一次
                except Exception as e:
                    logger.error(f"健康检查失败: {e}")
                    await asyncio.sleep(30)
        
        # 指标收集任务
        async def metrics_collection_task():
            while not shutdown_event.is_set():
                try:
                    # 收集自定义指标
                    await asyncio.sleep(60)  # 每分钟收集一次
                except Exception as e:
                    logger.error(f"指标收集失败: {e}")
                    await asyncio.sleep(60)
        
        # 启动后台任务
        background_tasks.append(asyncio.create_task(health_check_task()))
        background_tasks.append(asyncio.create_task(metrics_collection_task()))
        
        logger.info("人工审核服务启动完成")
        
        yield
        
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        raise
    
    finally:
        # 关闭时执行
        logger.info("人工审核服务关闭中...")
        
        # 设置关闭事件
        shutdown_event.set()
        
        # 等待后台任务完成
        for task in background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # 关闭连接
        await close_redis()
        await close_database()
        
        logger.info("人工审核服务已关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    settings = get_settings()
    
    # 设置日志
    setup_logging(settings.monitoring.log_level)
    
    # 创建FastAPI应用
    app = FastAPI(
        title="索克生活人工审核服务",
        description="提供AI辅助的人工审核和质量控制功能",
        version=settings.app_version,
        docs_url="/docs" if not settings.environment == "production" else None,
        redoc_url="/redoc" if not settings.environment == "production" else None,
        lifespan=lifespan,
        openapi_tags=[
            {
                "name": "审核管理",
                "description": "审核任务的创建、查询和管理"
            },
            {
                "name": "AI预审",
                "description": "AI辅助的内容预审和风险评估"
            },
            {
                "name": "工作流",
                "description": "审核工作流程管理"
            },
            {
                "name": "管理",
                "description": "系统管理和配置"
            },
            {
                "name": "健康检查",
                "description": "服务健康状态检查"
            }
        ]
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.cors_origins,
        allow_credentials=True,
        allow_methods=settings.security.cors_methods,
        allow_headers=["*"],
    )
    
    # 添加受信任主机中间件（生产环境）
    if settings.environment == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*.suoke.life"]
        )
    
    # 添加请求处理中间件
    @app.middleware("http")
    async def process_request(request: Request, call_next):
        start_time = time.time()
        
        # 生成请求ID
        request_id = f"req_{int(time.time() * 1000)}"
        request.state.request_id = request_id
        
        # 记录请求开始
        logger.info(
            f"请求开始: {request.method} {request.url.path}",
            extra={"request_id": request_id}
        )
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Service"] = "human-review-service"
            
            # 记录请求完成
            logger.info(
                f"请求完成: {request.method} {request.url.path} - "
                f"状态码: {response.status_code} - "
                f"处理时间: {process_time:.4f}s",
                extra={"request_id": request_id}
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"请求异常: {request.method} {request.url.path} - "
                f"错误: {str(e)} - "
                f"处理时间: {process_time:.4f}s",
                extra={"request_id": request_id},
                exc_info=True
            )
            raise
    
    # 添加全局异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", "unknown")
        
        logger.error(
            f"未处理的异常: {exc}",
            extra={"request_id": request_id},
            exc_info=True
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "内部服务器错误",
                "message": "服务暂时不可用，请稍后重试",
                "request_id": request_id,
                "service": "human-review-service"
            }
        )
    
    # 注册路由
    app.include_router(
        review_router,
        prefix="/api/v1/reviews",
        tags=["审核管理"]
    )
    app.include_router(
        ai_router,
        prefix="/api/v1/ai",
        tags=["AI预审"]
    )
    app.include_router(
        workflow_router,
        prefix="/api/v1/workflow",
        tags=["工作流"]
    )
    app.include_router(
        admin_router,
        prefix="/api/v1/admin",
        tags=["管理"]
    )
    app.include_router(
        health_router,
        prefix="/health",
        tags=["健康检查"]
    )
    
    # 添加根路径
    @app.get("/", summary="服务信息", description="获取服务基本信息")
    async def root():
        return {
            "service": "索克生活人工审核服务",
            "version": settings.app_version,
            "environment": settings.environment,
            "status": "运行中",
            "timestamp": int(time.time()),
            "docs": "/docs" if not settings.environment == "production" else "不可用",
            "features": [
                "AI辅助预审",
                "多维度质量评估",
                "智能优先级排序",
                "专家协作平台",
                "实时异常检测"
            ]
        }
    
    # 初始化Prometheus指标
    if settings.monitoring.metrics_enabled:
        instrumentator = Instrumentator(
            should_group_status_codes=False,
            should_ignore_untemplated=True,
            should_respect_env_var=True,
            should_instrument_requests_inprogress=True,
            excluded_handlers=["/health", "/metrics"],
            env_var_name="ENABLE_METRICS",
            inprogress_name="inprogress",
            inprogress_labels=True,
        )
        instrumentator.instrument(app).expose(app)
    
    return app


def setup_signal_handlers():
    """设置信号处理器"""
    def handle_signal(sig, frame):
        logger.info(f"收到信号 {sig}，准备关闭服务...")
        shutdown_event.set()
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, handle_signal)   # Ctrl+C
    signal.signal(signal.SIGTERM, handle_signal)  # kill命令
    
    # 在Windows上SIGTSTP不可用
    if hasattr(signal, "SIGTSTP"):
        signal.signal(signal.SIGTSTP, handle_signal)  # Ctrl+Z


def main():
    """主函数"""
    settings = get_settings()
    
    # 设置信号处理器
    setup_signal_handlers()
    
    # 创建应用
    app = create_app()
    
    # 启动服务器
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.monitoring.log_level.lower(),
        reload=settings.environment == "development",
        workers=1 if settings.environment == "development" else settings.workers,
        access_log=True,
        use_colors=True,
        server_header=False,
        date_header=False,
    )


if __name__ == "__main__":
    main() 