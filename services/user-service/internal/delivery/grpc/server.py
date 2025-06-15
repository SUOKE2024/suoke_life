"""
gRPC服务器实现
提供用户服务的gRPC接口
"""
import asyncio
import logging
from concurrent import futures
from typing import Optional

import grpc
from grpc_reflection.v1alpha import reflection

from internal.delivery.grpc.user_server import UserServicer
from internal.service.user_service import UserService
from internal.repository.sqlite_user_repository import SQLiteUserRepository
from api.grpc import user_pb2_grpc

logger = logging.getLogger(__name__)

class GRPCServer:
    """gRPC服务器类"""
    
    def __init__(self, port: int = 50051):
        self.port = port
        self.server: Optional[grpc.aio.Server] = None
        self._shutdown_event = asyncio.Event()
    
    async def start(
        self, 
        user_repository: SQLiteUserRepository,
        user_service: UserService
    ):
        """启动gRPC服务器"""
        try:
            # 创建服务器
            self.server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
            
            # 注册服务
            user_servicer = UserServicer(user_service)
            user_pb2_grpc.add_UserServiceServicer_to_server(user_servicer, self.server)
            
            # 启用反射（用于调试）
            SERVICE_NAMES = (
                user_pb2_grpc.DESCRIPTOR.services_by_name['UserService'].full_name,
                reflection.SERVICE_NAME,
            )
            reflection.enable_server_reflection(SERVICE_NAMES, self.server)
            
            # 绑定端口
            listen_addr = f'[::]:{self.port}'
            self.server.add_insecure_port(listen_addr)
            
            # 启动服务器
            await self.server.start()
            logger.info(f"gRPC服务器启动成功，监听端口: {self.port}")
            
            # 等待关闭信号
            await self._shutdown_event.wait()
            
        except Exception as e:
            logger.error(f"gRPC服务器启动失败: {e}")
            raise
    
    async def stop(self, grace_period: float = 5.0):
        """停止gRPC服务器"""
        if self.server:
            logger.info("正在关闭gRPC服务器...")
            await self.server.stop(grace_period)
            logger.info("gRPC服务器已关闭")
        
        self._shutdown_event.set()
    
    def shutdown(self):
        """触发关闭"""
        self._shutdown_event.set()

async def start_grpc_server(
    user_repository: SQLiteUserRepository,
    user_service: UserService,
    port: int = 50051
) -> GRPCServer:
    """启动gRPC服务器的便捷函数"""
    server = GRPCServer(port)
    
    # 在后台任务中启动服务器
    task = asyncio.create_task(server.start(user_repository, user_service))
    
    # 等待一小段时间确保服务器启动
    await asyncio.sleep(0.1)
    
    return server

async def create_grpc_server_with_health_check(
    user_repository: SQLiteUserRepository,
    user_service: UserService,
    port: int = 50051
) -> GRPCServer:
    """创建带健康检查的gRPC服务器"""
    from grpc_health.v1 import health_pb2_grpc
    from grpc_health.v1.health import HealthServicer
    
    server = GRPCServer(port)
    
    # 添加健康检查服务
    health_servicer = HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server.server)
    
    # 设置服务健康状态
    health_servicer.set("user_service", health_pb2.HealthCheckResponse.SERVING)
    
    return server 