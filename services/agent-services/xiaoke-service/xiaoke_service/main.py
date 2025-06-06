"""
main - 索克生活项目模块
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from xiaoke_service.api.routes import api_router
from xiaoke_service.core.config import settings
from xiaoke_service.core.exceptions import XiaokeServiceError
from xiaoke_service.core.logging import get_logger, get_request_logger
from xiaoke_service.middleware.auth import AuthMiddleware
from xiaoke_service.middleware.logging import LoggingMiddleware
from xiaoke_service.middleware.rate_limit import RateLimitMiddleware
from xiaoke_service.services.database import DatabaseManager
from xiaoke_service.services.health import HealthChecker
import signal
import sys
import uvicorn

"""
小克智能体服务主入口

基于 FastAPI 构建的现代化微服务, 提供中医辨证论治和健康管理功能。
"""




logger = get_logger(__name__)
request_logger = get_request_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """应用生命周期管理"""

    # 启动时初始化
    logger.info("Starting Xiaoke Service", version=settings.service.service_version)

    try:
        # 初始化数据库连接
        db_manager = DatabaseManager()
        await db_manager.initialize()
        app.state.db_manager = db_manager

        # 初始化健康检查器
        health_checker = HealthChecker()
        await health_checker.initialize()
        app.state.health_checker = health_checker

        logger.info("Xiaoke Service started successfully")

        yield

    except Exception as e:
        logger.error("Failed to start Xiaoke Service", error=str(e))
        raise
    finally:
        # 关闭时清理资源
        logger.info("Shutting down Xiaoke Service")

        if hasattr(app.state, "db_manager"):
            await app.state.db_manager.close()

        if hasattr(app.state, "health_checker"):
            await app.state.health_checker.close()

        logger.info("Xiaoke Service shutdown completed")


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""

    app = FastAPI(

# 性能优化: 添加响应压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)
        title="小克智能体服务",
        description="索克生活健康管理平台的核心AI智能体, 专注于中医辨证论治和个性化健康管理",
        version=settings.service.service_version,
        docs_url=settings.service.docs_url if settings.service.debug else None,
        redoc_url=settings.service.redoc_url if settings.service.debug else None,
        openapi_url="/openapi.json" if settings.service.debug else None,
        lifespan=lifespan,
    )

    # 配置中间件
    setup_middleware(app)

    # 配置路由
    setup_routes(app)

    # 配置异常处理
    setup_exception_handlers(app)

    return app


def setup_middleware(app: FastAPI) -> None:
    """配置中间件"""

    # 配置信任主机中间件以提高安全性
    allowed_hosts = (
        ["*"] if settings.service.debug else ["localhost", "127.0.0.1", "testserver"]
    )
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts,
    )

    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.cors_origins,
        allow_credentials=settings.security.cors_credentials,
        allow_methods=settings.security.cors_methods,
        allow_headers=settings.security.cors_headers,
    )

    # 自定义中间件
    app.add_middleware(LoggingMiddleware)

    if settings.service.rate_limit_enabled:
        app.add_middleware(RateLimitMiddleware)

    app.add_middleware(AuthMiddleware)


def setup_routes(app: FastAPI) -> None:
    """配置路由"""

    # API 路由
    app.include_router(
        api_router,
        prefix=settings.service.api_prefix,
    )

    # 健康检查路由
    @cache(expire=300)  # 5分钟缓存
@limiter.limit("100/minute")  # 每分钟100次请求
@app.get("/health")
    async def health_check() -> dict:
        """健康检查端点"""
        if hasattr(app.state, "health_checker"):
            return await app.state.health_checker.check_health()
        r@cache(expire=@limiter.limit("100/minute")  # 每分钟100次请求
300)  # 5分钟缓存
eturn {"status": "ok"}

    @app.get("/ready")
    async def readiness_check() -> dict:
        """就绪检查端点"""
        if hasattr(app.state, "health_checker"):
            return await app.state.health_checker.check_readiness()
        return {"status": "ready"}

    # 指标端点
    if settings.monitoring.metrics_enabled:
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)


def setup_exception_handlers(app: FastAPI) -> None:
    """配置异常处理器"""

    @app.exception_handler(XiaokeServiceError)
    async def xiaoke_service_exception_handler(
        request: Request, exc: XiaokeServiceError
    ) -> JSONResponse:
        """处理小克服务异常"""
        logger.error(
            "Service error occurred",
            error_code=exc.error_code,
            error_message=exc.message,
            path=str(request.url),
            method=request.method,
        )

        return JSONResponse(
            status_code=400,
            content=exc.to_dict(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """处理通用异常"""
        logger.exception(
            "Unexpected error occurred",
            error_type=type(exc).__name__,
            error_message=str(exc),
            path=str(request.url),
            method=request.method,
        )

        return JSONResponse(
            status_code=500,
            content={
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": {} if not settings.service.debug else {"error": str(exc)},
            },
        )


def setup_signal_handlers() -> None:
    """设置信号处理器"""

    def signal_handler(signum: int, _frame) -> None:
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


# 创建应用实例
app = create_app()


def main() -> None:
    """主函数"""
    setup_signal_handlers()

    logger.info(
        "Starting Xiaoke Service",
        host=settings.service.host,
        port=settings.service.port,
        environment=settings.service.environment,
        debug=settings.service.debug,
    )

    uvicorn.run(
        "xiaoke_service.main:app",
        host=settings.service.host,
        port=settings.service.port,
        workers=settings.service.workers if not settings.service.debug else 1,
        reload=settings.service.debug,
        log_level=settings.monitoring.log_level.lower(),
        access_log=False,  # 使用自定义日志中间件
    )


if __name__ == "__main__":
    main()
