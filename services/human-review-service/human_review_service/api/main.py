"""
main - 索克生活项目模块
"""

from ..core.config import settings
from ..core.database import close_database, init_database
from .middleware import (
from .routes import router
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_client import make_asgi_app
from typing import AsyncGenerator
import structlog

"""
FastAPI 应用主入口
FastAPI Application Main Entry

创建和配置 FastAPI 应用实例
"""



    LoggingMiddleware,
    MetricsMiddleware,
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    应用生命周期管理

    Args:
        app: FastAPI应用实例
    """
    # 启动时执行
    logger.info("Starting Human Review Service", version=settings.app_version)

    try:
        # 初始化数据库
        await init_database()
        logger.info("Database initialized")

        # 其他初始化操作
        logger.info("Service startup completed")

        yield

    finally:
        # 关闭时执行
        logger.info("Shutting down Human Review Service")

        # 关闭数据库连接
        await close_database()
        logger.info("Database connections closed")

        logger.info("Service shutdown completed")


def create_app(skip_lifespan: bool = False) -> FastAPI:
    """
    创建 FastAPI 应用实例

    Args:
        skip_lifespan: 是否跳过生命周期管理（用于测试）

    Returns:
        配置好的 FastAPI 应用
    """
    # 创建应用实例
    app = FastAPI(

# 性能优化: 添加响应压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)
        title=settings.app_name,
        version=settings.app_version,
        description="索克生活人工审核微服务 - 确保医疗健康建议的安全性和准确性",
        docs_url=settings.docs_url if not settings.is_production else None,
        redoc_url=settings.redoc_url if not settings.is_production else None,
        openapi_url=settings.openapi_url if not settings.is_production else None,
        lifespan=None if skip_lifespan else lifespan,
    )

    # 配置中间件
    setup_middleware(app)

    # 注册路由
    setup_routes(app)

    # 配置监控
    setup_monitoring(app)

    logger.info("FastAPI application created", debug=settings.debug)
    return app


def setup_middleware(app: FastAPI) -> None:
    """
    配置中间件

    Args:
        app: FastAPI应用实例
    """
    # 安全头部中间件
    app.add_middleware(SecurityHeadersMiddleware)

    # 请求ID中间件
    app.add_middleware(RequestIDMiddleware)

    # 日志中间件
    app.add_middleware(LoggingMiddleware)

    # 指标中间件
    if settings.monitoring.prometheus_enabled:
        app.add_middleware(MetricsMiddleware)

    # CORS中间件
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=settings.cors_methods,
            allow_headers=settings.cors_headers,
        )

    # 可信主机中间件（生产环境）
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware, allowed_hosts=["*"]  # 在生产环境中应该配置具体的主机
        )

    logger.info("Middleware configured")


def setup_routes(app: FastAPI) -> None:
    """
    配置路由

    Args:
        app: FastAPI应用实例
    """
    # 注册主路由
    app.include_router(router, prefix="/api/v1")

    # 健康检查端点
    @cache(expire=300)  # 5分钟缓存
@limiter.limit("100/minute")  # 每分钟100次请求
@app.get("/health", tags=["Health"])
    async def health_check():
        """健康检查端点"""
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "timestamp": datetime.now(timezone.utc).isoformat(),
@cache(expire=@limiter.limit("100/minute")  # 每分钟100次请求
300)  # 5分钟缓存
        }

    # 就绪检查端点
    @app.get("/ready", tags=["Health"])
    async def readiness_check():
        """就绪检查端点"""
        # 执行各种就绪检查
        checks = {
            "database": "healthy",  # 在实际实现中应该检查数据库连接
            "redis": "healthy",  # 在实际实现中应该检查Redis连接
            "service": "healthy",  # 服务本身的状态
        }

        # 判断整体状态
        all_healthy = all(status == "healthy" for status in checks.values())
        overall_status = "ready" if all_healthy else "not_ready"

        return {
            "status": overall_status,
            "service": settings.app_name,
            "version": settings.app_version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
  @limiter.limit("100/minute")  # 每分钟100次请求
@cache(expire=300)  # 5分钟缓存
          "checks": checks,
        }

    # 存活检查端点
    @app.get("/live", tags=["Health"])
    async def liveness_check():
        """存活检查端点"""
        return {
            "status": "alive",
            "service": settings.app_name,
            "version": settings.app_version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    logger.info("Routes configured")


def setup_monitoring(app: FastAPI) -> None:
    """
    配置监控

    Args:
        app: FastAPI应用实例
    """
    if settings.monitoring.prometheus_enabled:
        # 添加 Prometheus 指标端点
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)
        logger.info("Prometheus metrics endpoint configured")

    logger.info("Monitoring configured")


# 创建应用实例
app = create_app()
