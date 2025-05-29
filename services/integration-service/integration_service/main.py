"""
Integration Service 主应用模块
"""

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = structlog.get_logger()


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""

    app = FastAPI(
        title="索克生活集成服务",
        description="第三方健康平台数据集成服务",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 添加 CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境中应该限制具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        """根路径健康检查"""
        return {"message": "Integration Service is running", "status": "healthy"}

    @app.get("/health")
    async def health_check():
        """健康检查端点"""
        return {"status": "healthy", "service": "integration-service"}

    logger.info("Integration Service application created successfully")
    return app


def main():
    """主函数"""
    print("Hello from integration-service!")


if __name__ == "__main__":
    main()
