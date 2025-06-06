"""
main - 索克生活项目模块
"""

        from datetime import datetime
from .api.routes import api_router
from .config.settings import get_settings
from .core.database import close_database, init_database
from .core.logging import setup_logging
from .core.monitoring import setup_monitoring
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
import sys
import uvicorn

"""
索儿智能体服务主入口模块

提供 FastAPI 应用创建和配置功能
"""





@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """应用生命周期管理"""
    # 启动时初始化
    settings = get_settings()
    setup_logging(settings.log_level)

    logger = logging.getLogger(__name__)
    logger.info("正在启动索儿智能体服务...")

    # 初始化数据库连接
    await init_database()

    # 设置监控
    setup_monitoring(app)

    logger.info("索儿智能体服务启动完成")

    yield

    # 关闭时清理
    logger.info("正在关闭索儿智能体服务...")
    await close_database()
    logger.info("索儿智能体服务已关闭")


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    settings = get_settings()

    app = FastAPI(

# 性能优化: 添加响应压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)
        title="索儿智能体服务",
        description="索克生活平台的营养与生活方式管理智能体",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    # 添加中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    )

    # 注册路由
    app.include_router(api_router, prefix="/api/v1")

    # 添加根端点
    @cache(expire=300)  # 5分钟缓存
@limiter.limit("100/minute")  # 每分钟100次请求
@app.get("/")
    async def root():
        """根端点"""
        return {
            "message": "欢迎使用索儿智能体服务",
            "service": "soer-service",
            "version": "0.1.0",
            "description": "索克生活平台的营养与生活方式管理智能体",
  @cache(expire=@limiter.limit("100/minute")  # 每分钟100次请求
300)  # 5分钟缓存
      }

    # 添加健康检查端点
    @app.get("/health")
    async def health_check():
        """健康检查端点"""

        return {
            "status": "healthy",
            "service": "soer-service",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "0.1.0",
        }

    return app


def main() -> None:
    """主函数入口"""
    settings = get_settings()

    # 设置日志
    setup_logging(settings.log_level)
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"启动索儿智能体服务，监听端口: {settings.port}")

        uvicorn.run(
            "soer_service.main:create_app",
            factory=True,
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level=settings.log_level.lower(),
            access_log=True,
        )
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务...")
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
