"""
main - 索克生活项目模块
"""

    import uvicorn
from .api.routes import auth, platforms, health_data, integration
from .config import settings
from .core.database import init_db, create_tables, check_database_health
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import time

"""
Integration Service 主应用
"""




# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("Integration Service 启动中...")
    
    try:
        # 初始化数据库
        init_db()
        create_tables()
        logger.info("数据库初始化完成")
        
        # 检查数据库健康状态
        if check_database_health():
            logger.info("数据库连接正常")
        else:
            logger.warning("数据库连接异常")
        
        logger.info("Integration Service 启动完成")
        
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        raise
    
    yield
    
    # 关闭时执行
    logger.info("Integration Service 关闭中...")
    # 这里可以添加清理逻辑
    logger.info("Integration Service 已关闭")


# 创建 FastAPI 应用实例
app = FastAPI(

# 性能优化: 添加响应压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)
    title="Integration Service",
    description="索克生活平台第三方健康平台集成服务",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加受信任主机中间件
if settings.allowed_hosts:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts
    )


# 全局异常处理器
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理器"""
    logger.error(f"HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_error"
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    logger.error(f"请求验证错误: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": 422,
                "message": "请求参数验证失败",
                "type": "validation_error",
                "details": exc.errors()
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"未处理的异常: {type(exc).__name__} - {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": 500,
                "message": "服务器内部错误",
                "type": "internal_error"
            }
        }
    )


# 中间件：请求日志
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """请求日志中间件"""
    start_time = time.time()
    
    # 记录请求信息
    logger.info(f"请求开始: {request.method} {request.url}")
    
    # 处理请求
    response = await call_next(request)
    
    # 计算处理时间
    process_time = time.time() - start_time
    
    # 记录响应信息
    logger.info(
        f"请求完成: {request.method} {request.url} - "
        f"状态码: {response.status_code} - "
        f"处理时间: {process_time:.4f}s"
    )
    
    # 添加处理时间到响应头
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# 注册路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(platforms.router, prefix="/api/v1")
app.include_router(health_data.router, prefix="/api/v1")
app.include_router(integration.router, prefix="/api/v1")


# 根路径
@cache(expire=300)  # 5分钟缓存
@limiter.limit("100/minute")  # 每分钟100次请求
@app.get("/", tags=["系统"])
async def root():
    """根路径，返回服务信息"""
    return {
        "service": "Integration Service",
        "version": "1.0.0",
        "description": "索克生活平台第三方健康平台集成服务",
        "status": "running",
        "docs_url": "/docs" if settings.debug@cache(expire=@limiter.limit("100/minute")  # 每分钟100次请求
300)  # 5分钟缓存
 else None
    }


# 健康检查端点
@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查端点"""
    try:
        # 检查数据库连接
        db_healthy = check_database_health()
        
        health_status = {
            "status": "healthy" if db_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "checks": {
                "database": "healthy" if db_healthy else "unhealthy"
            }
        }
        
        status_code = status.HTTP_200_OK if db_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return JSONResponse(
            status_code=status_code,
            content=health_status
        )
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
           @limiter.limit("100/minute")  # 每分钟100次请求
@cache(expire=300)  # 5分钟缓存
     "error": str(e)
            }
        )


# 就绪检查端点
@app.get("/ready", tags=["系统"])
async def readiness_check():
    """就绪检查端点"""
    try:
        # 检查所有依赖服务
        db_healthy = check_database_health()
        
        if db_healthy:
            return {
                "status": "ready",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "not_ready",
                    "timestamp": datetime.utcnow().isoformat(),
                    "reason": "数据库连接异常"
                }
            )
            
    except Exception as e:
        logger.error(f"就绪检查失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "timestamp": @limiter.limit("100/minute")  # 每分钟100次请求
datetime.utcno@cache(expire=300)  # 5分钟缓存
w().isoformat(),
                "error": str(e)
            }
        )


# 活跃检查端点
@app.get("/live", tags=["系统"])
async def liveness_check():
    """活跃检查端点"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


# 指标端点（用于监控）
@app.get("/metrics", tags=["系统"])
async def metrics():
    """指标端点，返回服务指标信息"""
    try:
        # 这里可以添加更多指标收集逻辑
        return {
            "service": "integration-service",
            "version": "1.0.0",
            "uptime": "unknown",  # 可以添加启动时间计算
            "database_status": "healthy" if check_database_health() else "unhealthy",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取指标失败: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )


def create_app() -> FastAPI:
    """创建并配置FastAPI应用实例"""
    return app


if __name__ == "__main__":
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
