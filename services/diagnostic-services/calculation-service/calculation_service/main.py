"""
算诊服务主程序
索克生活 - 传统中医算诊微服务
"""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from .api.routes import router
from .config.settings import get_settings
from .middleware.error_handler import ErrorHandlerMiddleware
from .middleware.logging_middleware import LoggingMiddleware
from .middleware.rate_limiter import RateLimiterMiddleware
from .utils.cache import cache_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    settings = get_settings()
    logging.info(f"启动算诊服务 {settings.APP_NAME} v{settings.VERSION}")

    # 初始化缓存管理器
    await cache_manager.initialize()

    yield

    # 关闭时清理
    await cache_manager.cleanup()
    logging.info("算诊服务已关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    settings = get_settings()

    app = FastAPI(
        title="索克生活 - 算诊服务",
        description="传统中医算诊（五诊）微服务，提供五运六气、八卦体质、子午流注等算诊功能",
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 添加Gzip压缩中间件
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 添加自定义中间件
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(RateLimiterMiddleware)

    # 注册路由
    app.include_router(router)

    # 根路径
    @app.get("/", tags=["基础"])
    async def root():
        """服务信息"""
        return {
            "service": "索克生活 - 算诊服务",
            "version": settings.VERSION,
            "description": "传统中医算诊微服务",
            "status": "running",
            "features": [
                "子午流注分析",
                "八字体质分析",
                "八卦配属分析",
                "五运六气分析",
                "综合算诊分析",
            ],
        }

    # 健康检查
    @app.get("/ping", tags=["基础"])
    async def ping():
        """健康检查"""
        return {"status": "ok", "message": "pong"}

    # 缓存状态
    @app.get("/cache/stats", tags=["管理"])
    async def cache_stats():
        """缓存统计信息"""
        stats = await cache_manager.get_stats()
        return {"cache_stats": stats}

    # 清理缓存
    @app.post("/cache/clear", tags=["管理"])
    async def clear_cache():
        """清理所有缓存"""
        await cache_manager.clear_all()
        return {"message": "缓存已清理"}

    return app


# 创建应用实例
app = create_app()


def main() -> None:
    """主函数 - 启动服务"""
    settings = get_settings()

    # 配置日志
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL), format=settings.LOG_FORMAT
    )

    # 启动服务
    uvicorn.run(
        "calculation_service.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main()
