"""
索克生活触诊服务主程序
基于FastAPI的现代化微服务架构
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import asyncio
import logging
import signal
import sys
import uvicorn

from .config import get_settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用程序生命周期管理"""
    logger.info("启动索克生活触诊服务...")
    
    try:
        # 获取配置
        settings = get_settings()
        logger.info("配置加载完成")
        
        yield
        
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        raise
    finally:
        logger.info("索克生活触诊服务已关闭")

def create_app() -> FastAPI:
    """创建FastAPI应用程序"""
    settings = get_settings()
    
    app = FastAPI(
        title="索克生活触诊服务",
        description="基于AI的中医触诊智能分析微服务，融合传统中医智慧与现代传感技术",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan
    )
    
    # 添加中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # 健康检查端点
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {
            "status": "healthy",
            "service": "palpation-service",
            "version": "1.0.0",
            "timestamp": asyncio.get_event_loop().time()
        }
    
    @app.get("/ready")
    async def readiness_check():
        """就绪检查"""
        return {
            "status": "ready",
            "service": "palpation-service",
            "timestamp": asyncio.get_event_loop().time()
        }
    
    return app

# 创建应用程序实例
app = create_app()

def main() -> None:
    """主函数"""
    settings = get_settings()
    
    # 配置信号处理
    def signal_handler(signum, frame):
        logger.info(f"接收到信号 {signum}，正在关闭服务...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动服务器
    uvicorn.run(
        "palpation_service.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning",
        access_log=settings.debug,
        workers=1 if settings.debug else settings.workers
    )

if __name__ == "__main__":
    main()
