"""
主应用模块

创建和配置FastAPI应用实例。
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..config.settings import get_settings
from ..utils.logger import get_logger
from .blockchain import router as blockchain_router
from .health import router as health_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """应用生命周期管理"""
    # 启动时的初始化
    logger.info("区块链服务启动中...")

    try:
        # 这里可以添加启动时的初始化逻辑
        # 比如初始化数据库连接、区块链客户端等
        logger.info("区块链服务启动完成")
        yield
    finally:
        # 关闭时的清理
        logger.info("区块链服务关闭中...")
        # 这里可以添加清理逻辑
        logger.info("区块链服务已关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用实例

    Returns:
        配置好的FastAPI应用实例
    """
    settings = get_settings()

    # 创建应用实例
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="索克生活区块链服务 - 健康数据的区块链存储、验证和访问控制",
        debug=settings.debug,
        lifespan=lifespan
    )

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(health_router, prefix="/health", tags=["健康检查"])
    app.include_router(blockchain_router, prefix="/api/v1/blockchain", tags=["区块链"])

    # 根路径
    @app.get("/", summary="根路径", description="返回服务基本信息")
    async def root():
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "environment": settings.environment
        }

    logger.info("FastAPI应用创建完成", extra={
        "app_name": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug
    })

    return app
