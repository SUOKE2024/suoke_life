"""认证服务主启动文件"""

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from auth_service.api.rest.router import api_router
from auth_service.config.settings import get_settings
from auth_service.core.database import DatabaseManager
from auth_service.core.redis import RedisManager
from auth_service.middleware.logging import LoggingMiddleware
from auth_service.middleware.metrics import MetricsMiddleware
from auth_service.middleware.security import SecurityMiddleware


# 配置结构化日志
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    settings = get_settings()
    
    # 启动时初始化
    logger.info("正在启动认证服务", version=settings.app_version)
    
    # 初始化数据库
    db_manager = DatabaseManager(settings.database)
    await db_manager.initialize()
    app.state.db_manager = db_manager
    
    # 初始化Redis
    redis_manager = RedisManager(settings.redis)
    await redis_manager.initialize()
    app.state.redis_manager = redis_manager
    
    logger.info("认证服务启动完成")
    
    yield
    
    # 关闭时清理
    logger.info("正在关闭认证服务")
    
    # 关闭Redis连接
    await redis_manager.close()
    
    # 关闭数据库连接
    await db_manager.close()
    
    logger.info("认证服务已关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="索克生活认证服务 - 提供用户认证、授权和账户管理功能",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )
    
    # 添加中间件
    setup_middleware(app, settings)
    
    # 添加路由
    app.include_router(api_router, prefix="/api/v1")
    
    # 健康检查端点
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {"status": "healthy", "service": "auth-service"}
    
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "status": "running"
        }
    
    return app


def setup_middleware(app: FastAPI, settings) -> None:
    """设置中间件"""
    
    # 信任主机中间件
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"] if settings.debug else ["localhost", "127.0.0.1"]
    )
    
    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )
    
    # 自定义中间件
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    if settings.enable_metrics:
        app.add_middleware(MetricsMiddleware)


def setup_signal_handlers() -> None:
    """设置信号处理器"""
    def signal_handler(signum, frame):
        logger.info(f"收到信号 {signum}，正在关闭服务")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main() -> None:
    """主函数"""
    settings = get_settings()
    
    # 设置日志级别
    logging.basicConfig(
        level=getattr(logging, settings.server.log_level.upper()),
        format="%(message)s"
    )
    
    # 设置信号处理器
    setup_signal_handlers()
    
    # 创建应用
    app = create_app()
    
    # 启动服务器
    uvicorn.run(
        app,
        host=settings.server.host,
        port=settings.server.port,
        workers=settings.server.workers,
        reload=settings.server.reload,
        log_level=settings.server.log_level,
        access_log=settings.debug,
    )


if __name__ == "__main__":
    main() 