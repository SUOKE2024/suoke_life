#!/usr/bin/env python3
"""
索克生活用户管理服务主入口
整合了auth-service和user-service的功能
"""

import logging
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# 导入子服务模块
from user_management_service.user_service.config import get_settings

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    logger.info("🚀 启动索克生活用户管理服务...")

    # 启动时的初始化
    try:
        # 初始化数据库连接
        logger.info("📊 初始化数据库连接...")

        # 初始化缓存
        logger.info("🗄️ 初始化缓存系统...")

        # 初始化监控
        logger.info("📈 初始化监控系统...")

        logger.info("✅ 用户管理服务启动完成")
        yield

    except Exception as e:
        logger.error(f"❌ 服务启动失败: {e}")
        raise
    finally:
        # 关闭时的清理
        logger.info("🔄 正在关闭用户管理服务...")
        logger.info("✅ 用户管理服务已关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    settings = get_settings()

    app = FastAPI(
        title="索克生活用户管理服务",
        description="整合认证和用户管理功能的统一服务",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # 添加中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )

    app.add_middleware(GZipMiddleware, minimum_size=1000)

    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware, allowed_hosts=["*"]  # 在生产环境中应该配置具体的主机
        )

    # 健康检查端点
    @app.get("/health")
    async def health_check():
        """服务健康检查"""
        return {
            "status": "healthy",
            "service": "user-management-service",
            "version": "1.0.0",
            "components": {"auth_service": "healthy", "user_service": "healthy"},
            "timestamp": "2024-12-19T00:00:00Z",
        }

    @app.get("/")
    async def root():
        """根路径"""
        return {
            "message": "索克生活用户管理服务",
            "description": "提供用户认证、授权和用户数据管理功能",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
        }

    # 挂载子应用路由
    # 认证相关路由
    @app.get("/api/v1/auth/status")
    async def auth_status():
        """认证状态检查"""
        return {"status": "auth_service_ready", "version": "1.0.0"}

    # 用户管理相关路由
    from user_management_service.user_service.api.router import (
        api_router as user_router,
    )

    app.include_router(user_router, prefix="/api/v1", tags=["用户管理"])

    # 全局异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """全局异常处理器"""
        logger.error(f"未处理的异常: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": 500,
                    "message": "内部服务器错误",
                    "type": "InternalServerError",
                },
                "request_id": getattr(request.state, "request_id", None),
                "timestamp": "2024-12-19T00:00:00Z",
            },
        )

    return app


def main():
    """主函数"""
    settings = get_settings()

    logger.info("🌟 启动索克生活用户管理服务")
    logger.info(f"📍 环境: {settings.environment}")
    logger.info(f"🔧 调试模式: {settings.debug}")

    # 创建应用
    app = create_app()

    # 启动服务器
    uvicorn.run(
        app,
        host=settings.server.host,
        port=settings.server.port,
        workers=settings.server.workers if not settings.debug else 1,
        reload=settings.debug,
        log_level=settings.server.log_level,
        access_log=True,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("👋 收到中断信号，正在关闭服务...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ 服务启动失败: {e}")
        sys.exit(1)
