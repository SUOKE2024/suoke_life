"""
算诊微服务主服务器

启动FastAPI应用程序
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from ..api.v1 import calculation_router, calendar_router, constitution_router
from ..core.config import get_settings
from ..middleware.logging import LoggingMiddleware
from ..middleware.metrics import MetricsMiddleware


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    settings = get_settings()
    
    app = FastAPI(
        title="算诊微服务",
        description="传统中医第五诊断方法 - 算诊服务",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
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
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(MetricsMiddleware)
    
    # 注册路由
    app.include_router(
        calculation_router,
        prefix="/api/v1/calculation",
        tags=["算诊计算"]
    )
    app.include_router(
        calendar_router,
        prefix="/api/v1/calendar",
        tags=["历法计算"]
    )
    app.include_router(
        constitution_router,
        prefix="/api/v1/constitution",
        tags=["体质分析"]
    )
    
    # 健康检查
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {"status": "healthy", "service": "calculation-service"}
    
    # 指标监控
    @app.get("/metrics")
    async def metrics():
        """指标监控"""
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        from fastapi import Response
        
        return Response(
            generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    
    return app


def main():
    """主函数"""
    settings = get_settings()
    
    uvicorn.run(
        "calculation_service.cmd.server:create_app",
        factory=True,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    main() 