"""
main - 索克生活项目模块
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from integration_service.api.routes import health, integration

"""
integration-service API主文件
"""


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(

# 性能优化: 添加响应压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)
        title="integration-service",
        description="integration-service API服务",
        version="1.0.0"
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(health.router, prefix="/health", tags=["健康检查"])
    app.include_router(integration.router, prefix="/api/v1", tags=["integration-service"])
    
    return app
