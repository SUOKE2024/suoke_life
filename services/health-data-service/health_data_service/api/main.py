"""
索克生活健康数据服务 - FastAPI 应用主入口

提供健康数据管理的REST API接口，包括：
- 健康数据的CRUD操作
- 数据验证和处理
- 错误处理和日志记录
- API文档生成
"""

import asyncio
import logging
import signal
import sys
import time
from collections.abc import AsyncGenerator
from collections.abc import Awaitable
from collections.abc import Callable
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from prometheus_client import Counter
from prometheus_client import Histogram
from prometheus_client import generate_latest
from starlette.middleware.base import BaseHTTPMiddleware

from health_data_service.api.routes import health_data_router
from health_data_service.core.config import settings
from health_data_service.core.database import get_database
from health_data_service.core.exceptions import DatabaseError
from health_data_service.core.exceptions import NotFoundError
from health_data_service.core.exceptions import ValidationError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus 指标
REQUEST_COUNT = Counter(
    'health_data_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'health_data_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

ERROR_COUNT = Counter(
    'health_data_errors_total',
    'Total number of errors',
    ['error_type']
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Prometheus 监控中间件"""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)

        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("健康数据服务启动中...")

    # 初始化数据库连接
    try:
        # 这里只是测试连接，不需要实际使用
        db_gen = get_database()
        _ = await db_gen.__anext__()
        await db_gen.aclose()
        logger.info("数据库连接初始化成功")
    except Exception as e:
        logger.error(f"数据库连接初始化失败: {e}")
        sys.exit(1)

    yield

    # 关闭时清理
    logger.info("健康数据服务关闭中...")


# 创建FastAPI应用
app = FastAPI(
    title="索克生活健康数据服务",
    description="基于AI的健康数据管理和分析服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)
app.add_middleware(PrometheusMiddleware)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """处理验证错误"""
    logger.warning(f"验证错误: {exc.message}")
    return JSONResponse(
        status_code=400,
        content={"error": "validation_error", "message": exc.message},
    )


@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    """处理资源不存在错误"""
    logger.warning(f"资源不存在: {exc.message}")
    return JSONResponse(
        status_code=404,
        content={"error": "not_found", "message": exc.message},
    )


@app.exception_handler(DatabaseError)
async def database_exception_handler(request: Request, exc: DatabaseError) -> JSONResponse:
    """处理数据库错误"""
    logger.error(f"数据库错误: {exc.message}")
    return JSONResponse(
        status_code=500,
        content={"error": "database_error", "message": "内部服务器错误"},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """处理HTTP异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "http_error", "message": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理通用异常"""
    logger.error(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "message": "内部服务器错误"},
    )


@app.get("/")
async def root() -> dict[str, str]:
    """根路径"""
    return {
        "service": "索克生活健康数据服务",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """健康检查端点"""
    try:
        # 检查数据库连接
        db_gen = get_database()
        _ = await db_gen.__anext__()
        # 这里应该执行一个简单的查询来测试连接
        # await db.execute(text("SELECT 1"))
        await db_gen.aclose()

        return {
            "status": "healthy",
            "timestamp": time.time(),
            "database": "connected",
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=503, detail="服务不可用") from e


@app.get("/metrics")
async def metrics() -> Response:
    """Prometheus 指标端点"""
    metrics_data = generate_latest()
    # generate_latest() 总是返回 bytes
    metrics_content = metrics_data.decode('utf-8')
    return Response(metrics_content, media_type="text/plain")


# 包含路由
app.include_router(health_data_router, prefix="/api/v1", tags=["health-data"])


def setup_signal_handlers() -> None:
    """设置信号处理器"""
    def signal_handler(signum: int, frame: Any) -> None:
        logger.info(f"收到信号 {signum}，正在关闭服务...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def run_server() -> None:
    """运行服务器"""
    setup_signal_handlers()

    uvicorn.run(
        "health_data_service.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    run_server()
