"""
服务器启动模块

提供 gRPC 和 HTTP 服务器的启动功能。
"""

import asyncio
import signal
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

import grpc
import uvicorn
from grpc_reflection.v1alpha import reflection
from loguru import logger

from inquiry_service.api.grpc.server import create_grpc_server
from inquiry_service.api.http.app import create_fastapi_app
from inquiry_service.core.config import get_settings
from inquiry_service.core.logging import setup_logging


class ServiceManager:
    """服务管理器"""
    
    def __init__(self) -> None:
        self.settings = get_settings()
        self.grpc_server: Optional[grpc.aio.Server] = None
        self.http_server: Optional[uvicorn.Server] = None
        self._shutdown_event = asyncio.Event()
    
    async def start_grpc_server(self) -> None:
        """启动 gRPC 服务器"""
        try:
            self.grpc_server = await create_grpc_server(self.settings)
            
            listen_addr = f"{self.settings.grpc.host}:{self.settings.grpc.port}"
            self.grpc_server.add_insecure_port(listen_addr)
            
            logger.info(f"Starting gRPC server on {listen_addr}")
            await self.grpc_server.start()
            logger.info("gRPC server started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start gRPC server: {e}")
            raise
    
    async def start_http_server(self) -> None:
        """启动 HTTP 服务器"""
        try:
            app = create_fastapi_app(self.settings)
            
            config = uvicorn.Config(
                app=app,
                host=self.settings.grpc.host,
                port=self.settings.monitoring.metrics_port,
                log_level=self.settings.logging.level.lower(),
                access_log=True,
                loop="asyncio",
            )
            
            self.http_server = uvicorn.Server(config)
            
            logger.info(f"Starting HTTP server on {self.settings.grpc.host}:{self.settings.monitoring.metrics_port}")
            await self.http_server.serve()
            
        except Exception as e:
            logger.error(f"Failed to start HTTP server: {e}")
            raise
    
    async def shutdown(self) -> None:
        """关闭服务"""
        logger.info("Shutting down services...")
        
        # 关闭 gRPC 服务器
        if self.grpc_server:
            logger.info("Stopping gRPC server...")
            await self.grpc_server.stop(grace=30)
            logger.info("gRPC server stopped")
        
        # 关闭 HTTP 服务器
        if self.http_server:
            logger.info("Stopping HTTP server...")
            self.http_server.should_exit = True
            logger.info("HTTP server stopped")
        
        self._shutdown_event.set()
        logger.info("All services stopped")
    
    def setup_signal_handlers(self) -> None:
        """设置信号处理器"""
        def signal_handler(signum: int, frame) -> None:
            logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run(self) -> None:
        """运行服务"""
        self.setup_signal_handlers()
        
        try:
            # 并发启动服务
            tasks = []
            
            # 启动 gRPC 服务器
            tasks.append(asyncio.create_task(self.start_grpc_server()))
            
            # 如果启用监控，启动 HTTP 服务器
            if self.settings.monitoring.enable_metrics:
                tasks.append(asyncio.create_task(self.start_http_server()))
            
            # 等待所有服务启动
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # 等待关闭信号
            if self.grpc_server:
                await self.grpc_server.wait_for_termination()
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Service error: {e}")
            raise
        finally:
            await self.shutdown()


async def main() -> None:
    """主函数"""
    # 设置日志
    setup_logging()
    
    # 获取配置
    settings = get_settings()
    
    logger.info(f"Starting Inquiry Service v{settings.version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # 创建并运行服务管理器
    service_manager = ServiceManager()
    await service_manager.run()


def cli_main() -> None:
    """CLI 入口点"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Service failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main() 