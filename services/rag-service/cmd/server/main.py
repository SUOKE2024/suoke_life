"""
main - 索克生活项目模块
"""

from config.settings import Settings
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from internal.container import Container
from internal.delivery.grpc_server import create_grpc_server
from internal.delivery.rest_handler import create_rest_handler
from internal.integration.api_gateway import APIGateway
from internal.observability.metrics import MetricsCollector
from internal.resilience.circuit_breaker import CircuitBreakerService
from internal.routing.intelligent_router import IntelligentRouter
from loguru import logger
from pathlib import Path
from typing import Optional
import asyncio
import os
import signal
import sys
import uvicorn

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RAG服务主入口
整合所有组件并启动服务
"""


# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))



class RAGService:
    """RAG服务主类"""
    
    def __init__(self):
        self.settings = Settings()
        self.container: Optional[Container] = None
        self.app: Optional[FastAPI] = None
        self.grpc_server = None
        self.metrics_collector: Optional[MetricsCollector] = None
        self.circuit_breaker: Optional[CircuitBreakerService] = None
        self.intelligent_router: Optional[IntelligentRouter] = None
        self.api_gateway: Optional[APIGateway] = None
        self.shutdown_event = asyncio.Event()
    
    async def initialize(self):
        """初始化服务"""
        try:
            logger.info("正在初始化RAG服务...")
            
            # 初始化依赖注入容器
            self.container = Container()
            await self.container.init_resources()
            
            # 获取核心组件
            self.metrics_collector = self.container.metrics_collector()
            self.circuit_breaker = self.container.circuit_breaker_service()
            
            # 初始化智能路由器
            self.intelligent_router = IntelligentRouter(self.metrics_collector)
            
            # 初始化API网关
            self.api_gateway = APIGateway(self.metrics_collector, self.circuit_breaker)
            await self.api_gateway.__aenter__()
            
            # 创建FastAPI应用
            self.app = await self._create_fastapi_app()
            
            # 创建gRPC服务器
            self.grpc_server = await create_grpc_server(self.container)
            
            logger.info("RAG服务初始化完成")
            
        except Exception as e:
            logger.error(f"RAG服务初始化失败: {e}")
            raise

    async def _create_fastapi_app(self) -> FastAPI:
        """创建FastAPI应用"""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            """应用生命周期管理"""
            # 启动时
            logger.info("FastAPI应用启动")
            yield
            # 关闭时
            logger.info("FastAPI应用关闭")
            await self.cleanup()
        
        app = FastAPI(
            title="索克生活 RAG服务",
            description="基于检索增强生成的智能健康管理服务",
            version="1.2.0",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json",
            lifespan=lifespan
        )
        
        # 添加中间件
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # 注册路由
        rest_handler = create_rest_handler(
            self.container,
            self.intelligent_router,
            self.api_gateway
        )
        app.include_router(rest_handler, prefix="/api/v1")
        
        # 健康检查端点
        @cache(expire=300)  # 5分钟缓存
@limiter.limit("100/minute")  # 每分钟100次请求
@app.get("/health")
        async def health_check():
            """健康检查"""
            try:
                # 检查核心组件状态
                container_status = "healthy" if self.container else "unhealthy"
                router_status = "healthy" if self.intelligent_router else "unhealthy"
                gateway_status = "healthy" if self.api_gateway else "unhealthy"
                
                # 检查数据库连接
                vector_db = self.container.vector_database()
                db_status = "healthy" if await vector_db.health_check() else "unhealthy"
                
                overall_status = "healthy" if all([
                    container_status == "healthy",
                    router_status == "healthy",
                    gateway_status == "healthy",
                    db_status == "healthy"
                ]) else "unhealthy"
                
                return {
                    "status": overall_status,
                    "components": {
                        "container": container_status,
                        "router": router_status,
                        "gateway": gateway_status,
                        "vector_database": db_status
                    },
                    "version": "1.2.0",
                    "timestamp": asyncio.get_event_loop().time()
                }
                
            except Exception as e:
                logger.error(f"健康检查失败: {e}")
                raise HTTPException(status_code=503, detail="服务不健康")
    @cache(expire=@limiter.limit("100/minute")  # 每分钟100次请求
300)  # 5分钟缓存
    
        # 指标端点
        @app.get("/metrics")
        async async def get_metrics(
            """获取Prometheus格式的指标"""
            try:
                if self.metrics_collector:
                    return await self.metrics_collector.export_prometheus_metrics()
                else:
                    return {"error": "指标收集器未初始化"}
            except Exception as e:
                logger.error(f"获取指标失败: {e}")
                raise HTTPException(status_code=@limiter.limit("100/minute")  # 每分钟100次请求
@cache(expire=300)  # 5分钟缓存
500, detail="获取指标失败")
        
        # 服务状态端点
        @app.get("/status")
        async async def get_service_status(
            """获取详细的服务状态"""
            try:
                status = {
                    "service": "rag-service",
                    "version": "1.2.0",
                    "environment": self.settings.environment,
                    "uptime": asyncio.get_event_loop().time(),
                }
                
                # 添加路由器统计
                if self.intelligent_router:
                    status["routing"] = await self.intelligent_router.get_routing_statistics()
                
                # 添加网关统计
                if self.api_gateway:
                    status["gateway"] = await self.api_gateway.get_gateway_statistics()
                
                # 添加容器统计
                if self.container:
                    status["container"] = {
                        "initialized": True,
                        "components_count": len(self.container._providers)
                    }
                
                return status
                
            except Exception as e:
                logger.error(f"获取服务状态失败: {e}")
                raise HTTPException(status_code=500, detail="获取服务状态失败")
        
        return app
    
    async def start_http_server(self):
        """启动HTTP服务器"""
        try:
            config = uvicorn.Config(
                app=self.app,
                host=self.settings.server.host,
                port=self.settings.server.port,
                log_level=self.settings.server.log_level.lower(),
                access_log=True,
                loop="asyncio"
            )
            
            server = uvicorn.Server(config)
            
            logger.info(
                f"启动HTTP服务器: http://{self.settings.server.host}:{self.settings.server.port}"
            )
            
            # 在后台任务中运行服务器
            server_task = asyncio.create_task(server.serve())
            
            # 等待关闭信号
            await self.shutdown_event.wait()
            
            # 优雅关闭
            logger.info("正在关闭HTTP服务器...")
            server.should_exit = True
            await server_task
            
        except Exception as e:
            logger.error(f"HTTP服务器启动失败: {e}")
            raise
    
    async def start_grpc_server(self):
        """启动gRPC服务器"""
        try:
            if self.grpc_server:
                grpc_port = self.settings.grpc.port
                await self.grpc_server.start(f"[::]:{grpc_port}")
                
                logger.info(f"启动gRPC服务器: 端口 {grpc_port}")
                
                # 等待关闭信号
                await self.shutdown_event.wait()
                
                # 优雅关闭
                logger.info("正在关闭gRPC服务器...")
                await self.grpc_server.stop(grace=30)
                
        except Exception as e:
            logger.error(f"gRPC服务器启动失败: {e}")
            raise
    
    async def run(self):
        """运行服务"""
        try:
            # 初始化服务
            await self.initialize()
            
            # 设置信号处理
            self._setup_signal_handlers()
            
            # 启动服务器
            tasks = []
            
            # HTTP服务器
            http_task = asyncio.create_task(self.start_http_server())
            tasks.append(http_task)
            
            # gRPC服务器
            if self.settings.grpc.enabled:
                grpc_task = asyncio.create_task(self.start_grpc_server())
                tasks.append(grpc_task)
            
            logger.info("RAG服务已启动，等待请求...")
            
            # 等待所有任务完成
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在关闭服务...")
        except Exception as e:
            logger.error(f"服务运行失败: {e}")
            raise
        finally:
            await self.cleanup()
    
    def _setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            logger.info(f"收到信号 {signum}，开始优雅关闭...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def shutdown(self):
        """关闭服务"""
        logger.info("正在关闭RAG服务...")
        self.shutdown_event.set()
    
    async def cleanup(self):
        """清理资源"""
        try:
            logger.info("正在清理资源...")
            
            # 关闭API网关
            if self.api_gateway:
                await self.api_gateway.__aexit__(None, None, None)
            
            # 关闭容器
            if self.container:
                await self.container.shutdown_resources()
            
            logger.info("资源清理完成")
        
        except Exception as e:
            logger.error(f"资源清理失败: {e}")


def setup_logging():
    """设置日志"""
    # 移除默认处理器
    logger.remove()
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level="INFO"
    )
    
    # 添加文件处理器
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "rag-service.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="DEBUG",
        rotation="100 MB",
        retention="30 days",
        compression="zip"
    )
    
    # 添加错误日志文件
    logger.add(
        log_dir / "rag-service-error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="50 MB",
        retention="30 days",
        compression="zip"
    )


def main():
    """主函数"""
    try:
        # 设置日志
        setup_logging()
        
        logger.info("启动索克生活 RAG服务...")
        logger.info(f"Python版本: {sys.version}")
        logger.info(f"工作目录: {os.getcwd()}")
        
        # 创建并运行服务
        service = RAGService()
        asyncio.run(service.run())
        
    except KeyboardInterrupt:
        logger.info("服务被用户中断")
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        sys.exit(1)
    finally:
        logger.info("RAG服务已停止")


if __name__ == "__main__":
    main()