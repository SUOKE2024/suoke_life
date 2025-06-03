"""
应用程序工厂模块

创建和配置 FastAPI 应用程序实例，集成中间件、路由、
异常处理等组件。
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from ..api.routes import api_router
from ..middleware.auth import AuthMiddleware
from ..middleware.logging import LoggingMiddleware
from ..middleware.rate_limit import RateLimitMiddleware
from ..middleware.security import SecurityMiddleware
from ..middleware.tracing import TracingMiddleware
from ..services.health import HealthService
from ..services.metrics import MetricsService
from ..services.service_registry import ServiceRegistry
from .config import Settings, get_settings
from .logging import get_logger, setup_logging

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用程序生命周期管理"""
    settings = get_settings()
    
    # 启动时初始化
    logger.info("Starting Suoke API Gateway", version=settings.app_version)
    
    try:
        # 初始化服务注册表
        service_registry = ServiceRegistry(settings)
        await service_registry.initialize()
        app.state.service_registry = service_registry
        
        # 初始化健康检查服务
        health_service = HealthService(settings)
        await health_service.initialize()
        app.state.health_service = health_service
        
        # 初始化指标服务
        metrics_service = MetricsService(settings)
        await metrics_service.initialize()
        app.state.metrics_service = metrics_service
        
        logger.info("API Gateway started successfully")
        
        yield
        
    except Exception as e:
        logger.error("Failed to start API Gateway", error=str(e), exc_info=True)
        raise
    finally:
        # 关闭时清理
        logger.info("Shutting down API Gateway")
        
        # 清理服务注册表
        if hasattr(app.state, "service_registry"):
            await app.state.service_registry.cleanup()
        
        # 清理健康检查服务
        if hasattr(app.state, "health_service"):
            await app.state.health_service.cleanup()
        
        # 清理指标服务
        if hasattr(app.state, "metrics_service"):
            await app.state.metrics_service.cleanup()
        
        logger.info("API Gateway shutdown complete")

def create_app(settings: Settings | None = None) -> FastAPI:
    """创建 FastAPI 应用程序实例"""
    if settings is None:
        settings = get_settings()
    
    # 设置日志
    setup_logging(settings)
    
    # 创建 FastAPI 应用
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="索克生活 API 网关服务 - 统一的微服务入口和路由管理",
        docs_url="/docs" if settings.is_development() else None,
        redoc_url="/redoc" if settings.is_development() else None,
        openapi_url="/openapi.json" if settings.is_development() else None,
        lifespan=lifespan,
    )
    
    # 添加中间件
    setup_middleware(app, settings)
    
    # 添加路由
    setup_routes(app, settings)
    
    # 添加异常处理器
    setup_exception_handlers(app)
    
    # 存储设置到应用状态
    app.state.settings = settings
    
    return app

def setup_middleware(app: FastAPI, settings: Settings) -> None:
    """设置中间件"""
    
    # 信任的主机中间件（安全）
    if settings.allowed_hosts != ["*"]:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts,
        )
    
    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allow_origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )
    
    # Gzip 压缩中间件
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # 自定义中间件（按执行顺序添加）
    app.add_middleware(TracingMiddleware)  # 链路追踪
    app.add_middleware(SecurityMiddleware)  # 安全头
    app.add_middleware(LoggingMiddleware)  # 请求日志
    app.add_middleware(RateLimitMiddleware)  # 限流
    app.add_middleware(AuthMiddleware)  # 认证

def setup_routes(app: FastAPI, settings: Settings) -> None:
    """设置路由"""
    
    # API 路由
    app.include_router(api_router, prefix="/api/v1")
    
    # 新增功能路由
    app.include_router(websocket_router)  # WebSocket 路由
    app.include_router(oauth2_router)     # OAuth2 路由
    app.include_router(tracing_router)    # 分布式追踪路由
    app.include_router(admin_router)      # 管理界面路由
    app.include_router(metrics_router)    # 指标路由
    
    # 健康检查路由
    @app.get("/health")
    async def health_check():
        """健康检查端点"""
        return {"status": "healthy", "service": "api-gateway"}
    
    @app.get("/health/ready")
    async def readiness_check(request: Request):
        """就绪检查端点"""
        health_service = getattr(request.app.state, "health_service", None)
        if health_service:
            is_ready = await health_service.check_readiness()
            if is_ready:
                return {"status": "ready"}
            else:
                return JSONResponse(
                    status_code=503,
                    content={"status": "not ready"}
                )
        return {"status": "ready"}
    
    @app.get("/health/live")
    async def liveness_check():
        """存活检查端点"""
        return {"status": "alive"}
    
    # 指标端点
    if settings.monitoring.enabled:
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)
    
    # 根路径
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "docs": "/docs" if settings.is_development() else None,
        }

def setup_exception_handlers(app: FastAPI) -> None:
    """设置异常处理器"""
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """全局异常处理器"""
        logger.error(
            "Unhandled exception",
            path=request.url.path,
            method=request.method,
            error=str(exc),
            exc_info=True,
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "path": request.url.path,
            }
        )
    
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        """404 异常处理器"""
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not found",
                "message": f"Path {request.url.path} not found",
                "path": request.url.path,
            }
        )
    
    @app.exception_handler(405)
    async def method_not_allowed_handler(request: Request, exc):
        """405 异常处理器"""
        return JSONResponse(
            status_code=405,
            content={
                "error": "Method not allowed",
                "message": f"Method {request.method} not allowed for {request.url.path}",
                "path": request.url.path,
                "method": request.method,
            }
        )

# 用于开发的便捷函数
def create_dev_app() -> FastAPI:
    """创建开发环境应用"""
    from .config import Settings
    
    settings = Settings(
        debug=True,
        environment="development",
        log_level="DEBUG",
        secret_key="dev-secret-key-change-in-production-32chars",
    )
    
    return create_app(settings) 