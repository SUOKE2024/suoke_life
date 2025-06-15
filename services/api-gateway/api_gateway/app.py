"""
简单的FastAPI应用工厂
"""

from fastapi import FastAPI


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title="索克生活API网关",
        description="索克生活项目的API网关服务",
        version="1.0.0"
    )
    
    @app.get("/")
    async def root():
        return {"message": "索克生活API网关"}
    
    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "api-gateway"}
    
    return app


# 创建应用实例
app = create_app() 