"""
Integration Service Main Application
"""

import asyncio
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import logging

# 导入内部模块
from ...internal.service.database import init_database, close_database
from ...internal.service.redis_client import init_redis, close_redis
from ...internal.service.logging_config import setup_logging
from ...internal.service.config import get_settings

# 导入API路由
from ...api.rest.integration import router as integration_router
from ...api.rest.auth import router as auth_router
from ...api.rest.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    settings = get_settings()
    setup_logging(settings.app.log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("正在启动 Integration Service...")
    
    try:
        # 初始化数据库
        await init_database()
        logger.info("数据库初始化完成")
        
        # 初始化Redis
        await init_redis()
        logger.info("Redis初始化完成")
        
        logger.info("Integration Service 启动完成")
        
        yield
        
    except Exception as e:
        logger.error(f"服务启动失败: {str(e)}")
        raise
    finally:
        # 关闭时清理
        logger.info("正在关闭 Integration Service...")
        
        try:
            await close_redis()
            logger.info("Redis连接已关闭")
            
            await close_database()
            logger.info("数据库连接已关闭")
            
        except Exception as e:
            logger.error(f"服务关闭时出错: {str(e)}")
        
        logger.info("Integration Service 已关闭")


# 创建FastAPI应用
def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    
    settings = get_settings()
    
    app = FastAPI(
        title="Integration Service",
        description="第三方平台集成服务 - 索克生活健康管理平台",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # 添加中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.app.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # 添加全局异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger = logging.getLogger(__name__)
        logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "内部服务器错误",
                "message": "服务暂时不可用，请稍后重试"
            }
        )
    
    # 注册路由
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(integration_router, prefix="/api/v1")
    
    # 根路径
    @app.get("/", summary="服务信息")
    async def root():
        return {
            "service": "integration-service",
            "version": "1.0.0",
            "description": "第三方平台集成服务",
            "docs": "/docs",
            "health": "/api/v1/health"
        }
    
    return app


# 创建应用实例
app = create_app()


def main():
    """主函数"""
    settings = get_settings()
    
    # 配置日志
    setup_logging(settings.app.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info(f"启动 Integration Service")
    logger.info(f"Host: {settings.app.host}")
    logger.info(f"Port: {settings.app.port}")
    logger.info(f"Debug: {settings.app.debug}")
    logger.info(f"Log Level: {settings.app.log_level}")
    
    # 启动服务
    uvicorn.run(
        "main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug,
        log_level=settings.app.log_level.lower(),
        access_log=True
    )


if __name__ == "__main__":
    main() 