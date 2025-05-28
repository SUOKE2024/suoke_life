"""
gRPC 服务器

提供 gRPC 接口的网关服务。
"""

import asyncio
import signal
from typing import Optional

import grpc
from grpc import aio

from ..core.config import Settings
from ..core.logging import get_logger
from .gateway_service import GatewayService

logger = get_logger(__name__)


class GRPCServer:
    """gRPC 服务器"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.server: Optional[aio.Server] = None
        self.gateway_service: Optional[GatewayService] = None
        
    async def start(self) -> None:
        """启动 gRPC 服务器"""
        if not self.settings.grpc.enabled:
            logger.info("gRPC server is disabled")
            return
        
        try:
            # 创建服务器
            self.server = aio.server()
            
            # 创建网关服务
            self.gateway_service = GatewayService(self.settings)
            
            # 注册服务（这里需要根据实际的 protobuf 定义来实现）
            # add_GatewayServiceServicer_to_server(self.gateway_service, self.server)
            
            # 配置监听地址
            listen_addr = f"{self.settings.grpc.host}:{self.settings.grpc.port}"
            
            # 添加不安全端口（生产环境应该使用 TLS）
            self.server.add_insecure_port(listen_addr)
            
            # 启动服务器
            await self.server.start()
            
            logger.info(
                "gRPC server started",
                host=self.settings.grpc.host,
                port=self.settings.grpc.port,
            )
            
        except Exception as e:
            logger.error("Failed to start gRPC server", error=str(e))
            raise
    
    async def stop(self) -> None:
        """停止 gRPC 服务器"""
        if self.server:
            logger.info("Stopping gRPC server...")
            
            # 停止接受新连接
            self.server.stop(grace=30)
            
            # 等待服务器完全停止
            await self.server.wait_for_termination()
            
            logger.info("gRPC server stopped")
    
    async def wait_for_termination(self) -> None:
        """等待服务器终止"""
        if self.server:
            await self.server.wait_for_termination()


async def run_grpc_server(settings: Settings) -> None:
    """运行 gRPC 服务器"""
    server = GRPCServer(settings)
    
    # 设置信号处理
    def signal_handler():
        logger.info("Received shutdown signal")
        asyncio.create_task(server.stop())
    
    # 注册信号处理器
    for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, lambda s, f: signal_handler())
    
    try:
        await server.start()
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        await server.stop() 