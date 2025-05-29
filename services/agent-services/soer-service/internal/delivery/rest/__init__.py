from fastapi import FastAPI

from .emotional_routes import router as emotional_router
from .health_plan_routes import router as health_plan_router
from .health_routes import router as health_router


def init_rest_app():
    """初始化REST API应用"""
    app = FastAPI(
        title="索儿智能体服务API",
        description="索克生活APP LIFE频道的健康管理引擎服务API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # 注册路由
    app.include_router(health_router)
    app.include_router(health_plan_router)
    app.include_router(emotional_router)

    # 根路由
    @app.get("/")
    async def root():
        return {
            "service": "soer-service",
            "version": "1.0.0",
            "status": "running"
        }

    return app
