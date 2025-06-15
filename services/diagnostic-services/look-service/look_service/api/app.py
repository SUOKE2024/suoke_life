"""
FastAPI应用工厂和配置
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_client import make_asgi_app

from ..core.config import settings
from ..core.logging import get_logger
from ..exceptions import setup_exception_handlers
from ..middleware import (
    LoggingMiddleware,
    MetricsMiddleware,
    RateLimitMiddleware,
    SecurityMiddleware,
)
from .models import FHIRObservationResponse, LookDiagnosisRequest, LookDiagnosisResult
from .routes import api_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    # 启动时的初始化
    logger.info("Look Service 正在启动...")
    
    # 初始化数据库连接
    # await init_database()
    
    # 初始化机器学习模型
    # await init_ml_models()
    
    logger.info("Look Service 启动完成")
    
    yield
    
    # 关闭时的清理
    logger.info("Look Service 正在关闭...")
    
    # 清理数据库连接
    # await cleanup_database()
    
    # 清理机器学习模型
    # await cleanup_ml_models()
    
    logger.info("Look Service 关闭完成")


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    
    # 创建FastAPI应用
    app = FastAPI(
        title="Look Service",
        description="索克生活望诊微服务 - 基于计算机视觉的中医望诊智能分析系统",
        version=settings.service.service_version,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )
    
    # 配置CORS
    if settings.service.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.service.cors_origins,
            allow_credentials=True,
            allow_methods=settings.service.cors_methods,
            allow_headers=settings.service.cors_headers,
        )
    
    # 配置受信任主机
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # 在生产环境中应该配置具体的主机
        )
    
    # 添加自定义中间件
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    # 注册异常处理器
    setup_exception_handlers(app)
    
    # 注册路由
    app.include_router(api_router, prefix="/api/v1")
    
    # 添加Prometheus指标端点
    if settings.monitoring.enable_metrics:
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)
    
    # 添加健康检查端点
    @app.get("/health")
    async def health_check() -> Dict[str, Any]:
        """基础健康检查"""
        return {
            "status": "healthy",
            "service": "look-service",
            "version": settings.service.service_version,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    @app.get("/health/ready")
    async def readiness_check() -> Dict[str, Any]:
        """就绪状态检查"""
        # 检查数据库连接
        # db_healthy = await check_database_health()
        
        # 检查机器学习模型
        # ml_healthy = await check_ml_models_health()
        
        return {
            "status": "ready",
            "service": "look-service",
            "version": settings.service.service_version,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "database": "healthy",  # db_healthy
                "ml_models": "healthy",  # ml_healthy
            }
        }
    
    @app.get("/health/live")
    async def liveness_check() -> Dict[str, Any]:
        """存活状态检查"""
        return {
            "status": "alive",
            "service": "look-service",
            "version": settings.service.service_version,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    return app


def main() -> None:
    """主函数 - 用于测试"""
    app = create_app()
    logger.info("FastAPI应用创建成功")


if __name__ == "__main__":
    main()
