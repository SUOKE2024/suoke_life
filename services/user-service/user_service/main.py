"""
main - 索克生活项目模块
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from typing import AsyncGenerator
from user_service.api.router import api_router
from user_service.config import get_settings
from user_service.core.cache import init_cache, close_cache
from user_service.core.database import init_database, close_database
from user_service.core.exceptions import UserServiceException
from user_service.middleware.auth import AuthMiddleware
from user_service.middleware.logging import LoggingMiddleware
from user_service.middleware.rate_limit import RateLimitMiddleware
import logging
import uvicorn

"""
用户服务主应用
"""





# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    settings = get_settings()
    
    # 启动时初始化
    logger.info("正在启动用户服务...")
    
    try:
        # 初始化数据库
        await init_database()
        logger.info("数据库初始化完成")
        
        # 初始化缓存
        await init_cache()
        logger.info("缓存初始化完成")
        
        logger.info("用户服务启动完成")
        
        yield
        
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        raise
    finally:
        # 关闭时清理
        logger.info("正在关闭用户服务...")
        
        try:
            await close_cache()
            logger.info("缓存连接已关闭")
            
            await close_database()
            logger.info("数据库连接已关闭")
            
        except Exception as e:
            logger.error(f"服务关闭时出错: {e}")
        
        logger.info("用户服务已关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    settings = get_settings()
    
    # 创建应用实例
    app = FastAPI(

# 性能优化: 添加响应压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)
        title="索克生活用户服务",
        description="提供用户管理、设备管理、健康数据管理等功能",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan
    )
    
    # 添加中间件
    setup_middleware(app, settings)
    
    # 添加路由
    app.include_router(api_router, prefix="/api/v1")
    
    # 添加异常处理器
    setup_exception_handlers(app)
    
    return app


def setup_middleware(app: FastAPI, settings) -> None:
    """设置中间件"""
    
    # 信任主机中间件
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"] if settings.debug else ["suoke.life", "*.suoke.life"]
    )
    
    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else [
            "https://suoke.life",
            "https://app.suoke.life",
            "https://admin.suoke.life"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 自定义中间件
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthMiddleware)
    app.add_middleware(RateLimitMiddleware)


def setup_exception_handlers(app: FastAPI) -> None:
    """设置异常处理器"""
    
    @app.exception_handler(UserServiceException)
    async def user_service_exception_handler(request: Request, exc: UserServiceException):
        """用户服务异常处理器"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """值错误处理器"""
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "INVALID_VALUE",
                    "message": str(exc),
                    "details": None
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """通用异常处理器"""
        logger.error(f"未处理的异常: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "服务器内部错误",
                    "details": None
                }
            }
        )


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
        workers=1 if settings.debug else settings.server.workers
    )
