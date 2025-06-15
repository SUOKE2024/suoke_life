"""
索儿智能体服务主应用模块
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging
import uvicorn

from .api.routes import api_router
from .config.settings import get_settings
from .core.database import close_database, init_database
from .core.logging import setup_logging
from .core.monitoring import setup_monitoring


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("🚀 启动索儿智能体服务...")
    
    # 初始化数据库连接
    try:
        await init_database()
        logger.info("✅ 数据库连接初始化成功")
    except Exception as e:
        logger.error(f"❌ 数据库连接初始化失败: {e}")
    
    # 设置监控
    try:
        setup_monitoring()
        logger.info("✅ 监控系统初始化成功")
    except Exception as e:
        logger.error(f"❌ 监控系统初始化失败: {e}")
    
    logger.info("🎉 索儿智能体服务启动完成")
    
    yield
    
    # 关闭时清理
    logger.info("🔄 关闭索儿智能体服务...")
    
    try:
        await close_database()
        logger.info("✅ 数据库连接关闭成功")
    except Exception as e:
        logger.error(f"❌ 数据库连接关闭失败: {e}")
    
    logger.info("👋 索儿智能体服务已关闭")


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    settings = get_settings()
    
    # 设置日志
    setup_logging()
    
    # 创建 FastAPI 应用
    app = FastAPI(
        title=settings.app_name,
        description="索儿智能体微服务 - 专注于营养分析、健康管理、生活方式建议和中医养生指导",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Gzip 压缩中间件
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # 信任主机中间件
    if settings.environment == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts,
        )
    
    # 包含API路由
    app.include_router(api_router, prefix="/api/v1")
    
    # 健康检查端点
    @app.get("/health", tags=["健康检查"])
    async def health_check():
        """健康检查端点"""
        return JSONResponse(
            content={
                "status": "healthy",
                "service": "soer-service",
                "version": "0.1.0",
                "message": "索儿智能体服务运行正常"
            }
        )
    
    # 根路径
    @app.get("/", tags=["根路径"])
    async def root():
        """根路径端点"""
        return JSONResponse(
            content={
                "service": "soer-service",
                "description": "索儿智能体微服务",
                "version": "0.1.0",
                "docs": "/docs",
                "health": "/health"
            }
        )
    
    return app


# 创建应用实例
app = create_app()


def main() -> None:
    """主函数 - 用于直接运行服务"""
    settings = get_settings()
    
    uvicorn.run(
        "soer_service.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    main()