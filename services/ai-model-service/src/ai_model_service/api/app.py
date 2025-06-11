"""FastAPI应用创建和配置"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from kubernetes import config

from ..config.settings import get_settings
from ..core.manager import CloudModelManager
from ..utils.k8s import KubernetesClient
from ..utils.metrics import MetricsCollector
from .v1.health import router as health_router
from .v1.models import router as models_router

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    settings = get_settings()

    try:
        logger.info("正在初始化AI模型服务组件...")

        # 初始化Kubernetes客户端
        try:
            if settings.kubernetes.in_cluster:
                config.load_incluster_config()
            else:
                config.load_kube_config(config_file=settings.kubernetes.config_path)
        except Exception as e:
            logger.warning("Kubernetes配置加载失败，使用模拟模式", error=str(e))

        k8s_client = KubernetesClient(namespace=settings.kubernetes.namespace)

        # 初始化指标收集器
        metrics = None
        if settings.monitoring.enabled:
            metrics = MetricsCollector()
            await metrics.start()

        # 初始化模型管理器
        manager = CloudModelManager(k8s_client=k8s_client, metrics=metrics)
        await manager.start()

        # 将组件添加到应用状态
        app.state.settings = settings
        app.state.manager = manager
        app.state.metrics = metrics
        app.state.k8s_client = k8s_client

        logger.info("AI模型服务组件初始化完成")

        yield

    except Exception as e:
        logger.error("应用启动失败", error=str(e))
        raise
    finally:
        # 清理资源
        logger.info("正在关闭AI模型服务组件...")

        if hasattr(app.state, "manager") and app.state.manager:
            await app.state.manager.shutdown()

        if hasattr(app.state, "metrics") and app.state.metrics:
            await app.state.metrics.shutdown()

        logger.info("AI模型服务组件已关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    settings = get_settings()

    # 创建FastAPI应用
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="索克生活AI模型管理服务",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # 添加CORS中间件
    if settings.security.allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.security.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # 添加路由
    app.include_router(health_router, prefix="/health", tags=["健康检查"])

    app.include_router(models_router, prefix="/api/v1", tags=["模型管理"])

    # 指标端点
    @app.get("/metrics", include_in_schema=False)
    async def metrics() -> Any:
        """Prometheus指标端点"""
        if hasattr(app.state, "metrics") and app.state.metrics:
            return app.state.metrics.generate_latest()
        return JSONResponse({"error": "指标收集器未启用"}, status_code=503)

    # 根路径
    @app.get("/", include_in_schema=False)
    async def root() -> dict:
        """根路径"""
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "docs": "/docs",
            "health": "/health",
        }

    # 全局异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Any, exc: Any) -> JSONResponse:
        """全局异常处理器"""
        logger.error(
            "未处理的异常",
            path=request.url.path,
            method=request.method,
            error=str(exc),
            exc_info=True,
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": "内部服务器错误",
                "message": "服务遇到了意外错误，请稍后重试",
            },
        )

    return app
