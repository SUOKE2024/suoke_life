"""
小克智能体服务主入口

基于 FastAPI 构建的高性能异步微服务，提供中医辨证论治和个性化健康管理功能。
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from typing import Dict, Any
import signal
import sys
import uvicorn

from xiaoke_service.api.routes import api_router
from xiaoke_service.core.config import settings
from xiaoke_service.core.exceptions import XiaokeServiceError
from xiaoke_service.core.logging import get_logger, get_request_logger
from xiaoke_service.middleware.auth import AuthMiddleware
from xiaoke_service.middleware.logging import LoggingMiddleware
from xiaoke_service.middleware.rate_limit import RateLimitMiddleware
from xiaoke_service.services.database import DatabaseManager
from xiaoke_service.services.health import HealthChecker
from xiaoke_service.services.ai_service import AIService
from xiaoke_service.services.knowledge_service import KnowledgeService
from xiaoke_service.services.accessibility_service import AccessibilityService

# 初始化日志
logger = get_logger(__name__)
request_logger = get_request_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    logger.info("启动小克智能体服务", version=settings.service.service_version)
    
    # 启动时初始化
    try:
        # 初始化数据库连接
        db_manager = DatabaseManager()
        await db_manager.initialize()
        app.state.db_manager = db_manager
        
                # 初始化健康检查器
        health_checker = HealthChecker()
        await health_checker.initialize()
        app.state.health_checker = health_checker
        
        # 初始化AI服务
        ai_service = AIService()
        await ai_service.initialize()
        app.state.ai_service = ai_service
        
        # 初始化知识库服务
        knowledge_service = KnowledgeService()
        await knowledge_service.initialize()
        app.state.knowledge_service = knowledge_service
        
        # 初始化无障碍服务
        accessibility_service = AccessibilityService()
        await accessibility_service.initialize()
        app.state.accessibility_service = accessibility_service

        logger.info("小克智能体服务启动完成", 
                   services_count=5,
                   ai_enabled=True,
                   knowledge_base_enabled=True,
                   accessibility_enabled=True)
        
    except Exception as e:
        logger.error("服务启动失败", error=str(e))
        raise
    
    yield
    
    # 关闭时清理
    try:
        logger.info("正在关闭小克智能体服务")
        
                # 清理所有服务
        cleanup_tasks = []
        
        if hasattr(app.state, "accessibility_service"):
            cleanup_tasks.append(app.state.accessibility_service.close())
        if hasattr(app.state, "knowledge_service"):
            cleanup_tasks.append(app.state.knowledge_service.close())
        if hasattr(app.state, "ai_service"):
            cleanup_tasks.append(app.state.ai_service.close())
        if hasattr(app.state, "health_checker"):
            cleanup_tasks.append(app.state.health_checker.close())
        if hasattr(app.state, "db_manager"):
            cleanup_tasks.append(app.state.db_manager.close())
        
        if cleanup_tasks:
            import asyncio
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)

        logger.info("小克智能体服务已关闭")
        
    except Exception as e:
        logger.error("服务关闭时出错", error=str(e))


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    
    app = FastAPI(
        title="小克智能体服务",
        description="索克生活健康管理平台的核心AI智能体，专注于中医辨证论治和个性化健康管理",
        version=settings.service.service_version,
        docs_url=settings.service.docs_url,
        redoc_url=settings.service.redoc_url,
        lifespan=lifespan,
    )
    
    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.cors_origins,
        allow_credentials=settings.security.cors_credentials,
        allow_methods=settings.security.cors_methods,
        allow_headers=settings.security.cors_headers,
    )
    
    # 添加 GZip 压缩
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # 添加受信任主机中间件
    if settings.service.environment == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # 在生产环境中应该配置具体的主机
        )
    
    # 添加自定义中间件
    app.add_middleware(LoggingMiddleware)
    
    if settings.service.rate_limit_enabled:
        app.add_middleware(RateLimitMiddleware)
    
    app.add_middleware(AuthMiddleware)
    
    # 注册路由
    app.include_router(api_router, prefix=settings.service.api_prefix)
    
    # 健康检查端点
    @app.get("/health")
    async def health_check():
        """基础健康检查"""
        return {
            "status": "healthy",
            "service": settings.service.service_name,
            "version": settings.service.service_version,
            "environment": settings.service.environment,
        }
    
    @app.get("/ready")
    async def readiness_check(request: Request):
        """就绪检查"""
        try:
            health_checker = getattr(request.app.state, "health_checker", None)
            if health_checker:
                health_status = await health_checker.check_all()
                if health_status["status"] == "healthy":
                    return health_status
                else:
                    raise HTTPException(status_code=503, detail=health_status)
            else:
                return {"status": "ready", "message": "Health checker not initialized"}
        except Exception as e:
            logger.error("就绪检查失败", error=str(e))
            raise HTTPException(status_code=503, detail={"status": "not ready", "error": str(e)})
    
    # Prometheus 指标端点
    if settings.monitoring.metrics_enabled:
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)
    
    # 全局异常处理器
    @app.exception_handler(XiaokeServiceError)
    async def xiaoke_exception_handler(request: Request, exc: XiaokeServiceError):
        """处理小克服务自定义异常"""
        request_logger.log_error(
            method=request.method,
            path=str(request.url.path),
            error=exc,
            request_id=getattr(request.state, "request_id", None),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """处理通用异常"""
        request_logger.log_error(
            method=request.method,
            path=str(request.url.path),
            error=exc,
            request_id=getattr(request.state, "request_id", None),
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Internal server error",
                    "details": {"type": type(exc).__name__} if settings.service.debug else {},
                }
            },
        )
    
    return app


def setup_signal_handlers():
    """设置信号处理器"""
    def signal_handler(signum, frame):
        logger.info(f"收到信号 {signum}，正在关闭服务...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main() -> None:
    """主函数"""
    setup_signal_handlers()
    
    app = create_app()
    
    # 启动服务器
    uvicorn.run(
        app,
        host=settings.service.host,
        port=settings.service.port,
        log_config=None,  # 使用自定义日志配置
        access_log=False,  # 禁用默认访问日志
    )


if __name__ == "__main__":
    main()