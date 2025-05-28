"""
老克智能体服务器主入口

基于 FastAPI 的现代化 Web 服务器
"""

import asyncio
import signal
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict

import click
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from laoke_service.core.config import get_settings
from laoke_service.core.exceptions import LaoKeServiceError
from laoke_service.core.logging import setup_logging, get_logger, RequestLogger
from laoke_service.core.agent import LaoKeAgent
from laoke_service.api.routes import api_router
from laoke_service.api.middleware import (
    LoggingMiddleware,
    MetricsMiddleware,
    ErrorHandlingMiddleware,
)


# 全局变量
agent: LaoKeAgent = None
logger = None
request_logger = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用程序生命周期管理"""
    global agent, logger, request_logger
    
    # 启动时初始化
    settings = get_settings()
    setup_logging(settings.logging)
    
    logger = get_logger("laoke.server")
    request_logger = RequestLogger(logger)
    
    logger.info("启动老克智能体服务", version=settings.app_version)
    
    try:
        # 初始化智能体
        agent = LaoKeAgent(settings)
        await agent.initialize()
        
        # 将智能体实例添加到应用状态
        app.state.agent = agent
        app.state.settings = settings
        app.state.logger = logger
        
        logger.info("服务启动完成")
        
        yield
        
    except Exception as e:
        logger.error("服务启动失败", error=str(e))
        raise
    finally:
        # 关闭时清理
        logger.info("正在关闭服务...")
        # 这里可以添加清理逻辑
        logger.info("服务已关闭")


def create_app() -> FastAPI:
    """创建 FastAPI 应用程序"""
    settings = get_settings()
    
    app = FastAPI(
        title="老克智能体服务",
        description="索克生活平台的知识传播和社区管理智能体",
        version="1.0.0",
        docs_url="/docs" if settings.is_development() else None,
        redoc_url="/redoc" if settings.is_development() else None,
        openapi_url="/openapi.json" if not settings.is_production() else None,
        lifespan=lifespan,
    )
    
    # 添加中间件
    _add_middleware(app, settings)
    
    # 添加路由
    _add_routes(app, settings)
    
    # 添加异常处理器
    _add_exception_handlers(app)
    
    return app


def _add_middleware(app: FastAPI, settings) -> None:
    """添加中间件"""
    
    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.server.cors_origins,
        allow_credentials=True,
        allow_methods=settings.server.cors_methods,
        allow_headers=settings.server.cors_headers,
    )
    
    # 受信任主机中间件
    if settings.is_production():
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # 在生产环境中应该配置具体的主机
        )
    
    # 自定义中间件
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(LoggingMiddleware)


def _add_routes(app: FastAPI, settings) -> None:
    """添加路由"""
    
    # API 路由
    app.include_router(api_router, prefix="/api/v1")
    
    # 健康检查
    @app.get("/health")
    async def health_check():
        """健康检查端点"""
        return {"status": "healthy", "service": "laoke-service"}
    
    @app.get("/health/ready")
    async def readiness_check(request: Request):
        """就绪检查端点"""
        try:
            agent = getattr(request.app.state, 'agent', None)
            if agent is None:
                raise HTTPException(status_code=503, detail="Agent not initialized")
            
            status = await agent.get_agent_status()
            return {"status": "ready", "agent": status}
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Service not ready: {e}")
    
    @app.get("/health/live")
    async def liveness_check():
        """存活检查端点"""
        return {"status": "alive", "service": "laoke-service"}
    
    # Prometheus 指标
    if settings.monitoring.prometheus_enabled:
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)


def _add_exception_handlers(app: FastAPI) -> None:
    """添加异常处理器"""
    
    @app.exception_handler(LaoKeServiceError)
    async def laoke_service_error_handler(request: Request, exc: LaoKeServiceError):
        """处理服务特定异常"""
        logger = getattr(request.app.state, 'logger', None)
        if logger:
            logger.error(
                "服务异常",
                error_code=exc.error_code,
                error_message=exc.message,
                path=str(request.url),
                method=request.method
            )
        
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """处理 HTTP 异常"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": exc.detail
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """处理一般异常"""
        logger = getattr(request.app.state, 'logger', None)
        if logger:
            logger.error(
                "未处理的异常",
                error=str(exc),
                error_type=type(exc).__name__,
                path=str(request.url),
                method=request.method
            )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Internal server error"
                }
            }
        )


def setup_signal_handlers():
    """设置信号处理器"""
    def signal_handler(signum, frame):
        logger.info(f"收到信号 {signum}，正在关闭服务...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


@click.command()
@click.option("--host", default="0.0.0.0", help="服务器监听地址")
@click.option("--port", default=8080, help="服务器端口")
@click.option("--workers", default=1, help="工作进程数")
@click.option("--reload", is_flag=True, help="开发模式自动重载")
@click.option("--log-level", default="info", help="日志级别")
def main(host: str, port: int, workers: int, reload: bool, log_level: str):
    """启动老克智能体服务器"""
    
    # 设置信号处理器
    setup_signal_handlers()
    
    # 获取配置
    settings = get_settings()
    
    # 覆盖命令行参数
    if host != "0.0.0.0":
        settings.server.host = host
    if port != 8080:
        settings.server.port = port
    if workers != 1:
        settings.server.workers = workers
    
    # 创建应用
    app = create_app()
    
    # 配置 uvicorn
    uvicorn_config = {
        "app": app,
        "host": settings.server.host,
        "port": settings.server.port,
        "log_level": log_level,
        "access_log": True,
        "reload": reload or settings.is_development(),
        "workers": 1 if reload else settings.server.workers,
    }
    
    # 性能优化配置
    if not reload and not settings.is_development():
        uvicorn_config.update({
            "loop": "uvloop",
            "http": "httptools",
            "ws": "websockets",
        })
    
    # 启动服务器
    try:
        uvicorn.run(**uvicorn_config)
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"服务器启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 