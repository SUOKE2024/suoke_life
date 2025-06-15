#!/usr/bin/env python3
"""
索克生活 API 网关应用工厂

提供 FastAPI 应用创建和配置功能
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from .config import Settings, get_settings
from .logging import get_logger, setup_logging
from ..api.routes import api_router
from ..middleware.auth import AuthMiddleware
from ..middleware.logging import LoggingMiddleware
from ..middleware.rate_limit import RateLimitMiddleware
from ..middleware.security import SecurityMiddleware
from ..middleware.tracing import TracingMiddleware
from ..services.health import HealthService
from ..services.metrics import MetricsService
from ..services.service_registry import ServiceRegistry

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    logger.info("🚀 启动 API 网关服务...")
    
    # 启动时初始化
    try:
        # 初始化服务注册中心
        service_registry = ServiceRegistry()
        app.state.service_registry = service_registry
        await service_registry.initialize()
        
        # 初始化健康检查服务
        health_service = HealthService()
        app.state.health_service = health_service
        await health_service.initialize()
        
        # 初始化指标服务
        metrics_service = MetricsService()
        app.state.metrics_service = metrics_service
        await metrics_service.initialize()
        
        logger.info("✅ API 网关服务启动完成")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}")
        raise
    finally:
        # 关闭时清理
        logger.info("🔄 关闭 API 网关服务...")
        
        # 清理资源
        if hasattr(app.state, "service_registry"):
            await app.state.service_registry.cleanup()
        
        if hasattr(app.state, "health_service"):
            await app.state.health_service.cleanup()
        
        if hasattr(app.state, "metrics_service"):
            await app.state.metrics_service.cleanup()
        
        logger.info("✅ API 网关服务关闭完成")


def create_app(settings: Settings = None) -> FastAPI:
    """创建生产环境 FastAPI 应用"""
    if settings is None:
        settings = get_settings()
    
    # 创建 FastAPI 应用
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="索克生活健康管理平台 API 网关",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )
    
    # 存储配置
    app.state.settings = settings
    
    # 设置中间件
    _setup_middleware(app, settings)
    
    # 设置路由
    _setup_routes(app, settings)
    
    # 设置异常处理
    _setup_exception_handlers(app)
    
    logger.info(f"🎆 {settings.app_name} v{settings.app_version} 创建完成")
    return app


def create_dev_app(settings: Settings = None) -> FastAPI:
    """创建开发环境 FastAPI 应用"""
    if settings is None:
        settings = get_settings()
    
    # 强制开发模式设置
    settings.environment = "development"
    settings.debug = True
    
    # 创建应用
    app = create_app(settings)
    
    # 开发模式特殊配置
    app.debug = True
    
    logger.info("🔧 开发模式应用创建完成")
    return app


def _setup_middleware(app: FastAPI, settings: Settings) -> None:
    """设置中间件"""
    # 信任主机中间件
    if settings.security.trusted_hosts != ["*"]:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.security.trusted_hosts,
        )
    
    # CORS 中间件
    if settings.cors.enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors.allow_origins,
            allow_credentials=settings.cors.allow_credentials,
            allow_methods=settings.cors.allow_methods,
            allow_headers=settings.cors.allow_headers,
            expose_headers=settings.cors.expose_headers,
            max_age=settings.cors.max_age,
        )
    
    # Gzip 压缩中间件
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # 自定义中间件（按顺序添加）
    app.add_middleware(TracingMiddleware, settings=settings)
    app.add_middleware(SecurityMiddleware, settings=settings)
    app.add_middleware(RateLimitMiddleware, settings=settings)
    app.add_middleware(AuthMiddleware, settings=settings)
    app.add_middleware(LoggingMiddleware, settings=settings)


def _setup_routes(app: FastAPI, settings: Settings) -> None:
    """设置路由"""
    # 添加 API 路由
    app.include_router(api_router, prefix="/api/v1")
    
    # Prometheus 指标端点
    if settings.metrics.prometheus_enabled:
        metrics_app = make_asgi_app()
        app.mount("/metrics/prometheus", metrics_app)


def _setup_exception_handlers(app: FastAPI) -> None:
    """设置异常处理器"""
    
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc) -> JSONResponse:
        """处理 404 错误"""
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "message": f"路径 {request.url.path} 不存在",
                "path": str(request.url.path),
            },
        )
    
    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc) -> JSONResponse:
        """处理 500 错误"""
        logger.error(f"内部服务器错误: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "内部服务器错误，请稍后重试",
                "path": str(request.url.path),
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """处理通用异常"""
        logger.error(f"未处理的异常: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Unexpected Error",
                "message": "发生了意外错误，请稍后重试",
                "path": str(request.url.path),
            },
        )


# 全局应用实例（用于 uvicorn 命令行启动）
app = create_app()
