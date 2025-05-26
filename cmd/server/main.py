"""
Integration Service Main Application
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent))

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from internal.delivery.api import router as api_router
from internal.service.config import get_settings
from internal.service.database import init_database, close_database
from internal.service.redis_client import init_redis, close_redis
from internal.service.logging_config import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    settings = get_settings()
    setup_logging(settings.logging.level)
    
    logger = logging.getLogger(__name__)
    logger.info("正在启动Integration Service...")
    
    try:
        # 初始化数据库
        await init_database()
        logger.info("数据库连接已建立")
        
        # 初始化Redis
        await init_redis()
        logger.info("Redis连接已建立")
        
        logger.info("Integration Service启动完成")
        
        yield
        
    except Exception as e:
        logger.error(f"启动失败: {str(e)}")
        raise
    finally:
        # 关闭时清理资源
        logger.info("正在关闭Integration Service...")
        await close_redis()
        await close_database()
        logger.info("Integration Service已关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app.name,
        description=settings.app.description,
        version=settings.app.version,
        debug=settings.app.debug,
        lifespan=lifespan
    )
    
    # 添加中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应该限制具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # 生产环境应该限制具体主机
    )
    
    # 添加全局异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger = logging.getLogger(__name__)
        logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "服务器内部错误",
                "error": str(exc) if settings.app.debug else "Internal Server Error"
            }
        )
    
    # 注册路由
    app.include_router(api_router, prefix="/api/v1")
    
    # 健康检查端点
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": settings.app.name,
            "version": settings.app.version
        }
    
    # 根路径
    @app.get("/")
    async def root():
        return {
            "service": settings.app.name,
            "version": settings.app.version,
            "description": settings.app.description,
            "docs": "/docs",
            "health": "/health"
        }
    
    return app


def main():
    """主函数"""
    settings = get_settings()
    
    # 配置日志
    setup_logging(settings.app.log_level)
    
    # 创建应用
    app = create_app()
    
    # 启动服务器
    uvicorn.run(
        app,
        host=settings.app.host,
        port=settings.app.port,
        log_level=settings.app.log_level.lower(),
        reload=settings.app.debug
    )


if __name__ == "__main__":
    main() 