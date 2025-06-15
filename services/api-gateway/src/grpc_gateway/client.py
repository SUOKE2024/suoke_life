"""
gRPC客户端模块

提供gRPC客户端连接池和管理功能
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from contextlib import asynccontextmanager
import grpc
from grpc import aio
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class GrpcServiceConfig:
    """gRPC服务配置"""
    name: str
    host: str
    port: int
    secure: bool = False
    credentials: Optional[grpc.ChannelCredentials] = None
    options: Optional[List[tuple]] = None
    max_retries: int = 3
    timeout: float = 30.0
    keepalive_time: int = 30
    keepalive_timeout: int = 5


class GrpcClient:
    """gRPC客户端"""
    
    def __init__(self, config: GrpcServiceConfig):
        self.config = config
        self.channel: Optional[aio.Channel] = None
        self._stubs: Dict[str, Any] = {}
        self._connected = False
        
    async def connect(self) -> None:
        """建立连接"""
        if self._connected:
            return
            
        try:
            target = f"{self.config.host}:{self.config.port}"
            
            # 配置连接选项
            options = [
                ('grpc.keepalive_time_ms', self.config.keepalive_time * 1000),
                ('grpc.keepalive_timeout_ms', self.config.keepalive_timeout * 1000),
                ('grpc.keepalive_permit_without_calls', True),
                ('grpc.http2.max_pings_without_data', 0),
                ('grpc.http2.min_time_between_pings_ms', 10000),
                ('grpc.http2.min_ping_interval_without_data_ms', 300000),
            ]
            
            if self.config.options:
                options.extend(self.config.options)
            
            # 创建通道
            if self.config.secure and self.config.credentials:
                self.channel = aio.secure_channel(
                    target, 
                    self.config.credentials,
                    options=options
                )
            else:
                self.channel = aio.insecure_channel(target, options=options)
            
            # 等待连接就绪
            await self.channel.channel_ready()
            self._connected = True
            
            logger.info(
                "gRPC客户端连接成功",
                service=self.config.name,
                target=target,
                secure=self.config.secure
            )
            
        except Exception as e:
            logger.error(
                "gRPC客户端连接失败",
                service=self.config.name,
                error=str(e)
            )
            raise
    
    async def disconnect(self) -> None:
        """断开连接"""
        if self.channel and self._connected:
            await self.channel.close()
            self._connected = False
            self._stubs.clear()
            
            logger.info(
                "gRPC客户端连接已断开",
                service=self.config.name
            )
    
    def get_stub(self, stub_class: type) -> Any:
        """获取服务存根"""
        if not self._connected:
            raise RuntimeError(f"gRPC客户端未连接: {self.config.name}")
        
        stub_name = stub_class.__name__
        if stub_name not in self._stubs:
            self._stubs[stub_name] = stub_class(self.channel)
        
        return self._stubs[stub_name]
    
    async def call_unary(
        self,
        stub_method: Callable,
        request: Any,
        timeout: Optional[float] = None,
        metadata: Optional[List[tuple]] = None
    ) -> Any:
        """调用一元RPC"""
        if not self._connected:
            await self.connect()
        
        timeout = timeout or self.config.timeout
        
        for attempt in range(self.config.max_retries):
            try:
                response = await stub_method(
                    request,
                    timeout=timeout,
                    metadata=metadata
                )
                return response
                
            except grpc.RpcError as e:
                if attempt == self.config.max_retries - 1:
                    logger.error(
                        "gRPC调用失败",
                        service=self.config.name,
                        method=stub_method.__name__,
                        code=e.code(),
                        details=e.details(),
                        attempt=attempt + 1
                    )
                    raise
                
                # 可重试的错误
                if e.code() in [
                    grpc.StatusCode.UNAVAILABLE,
                    grpc.StatusCode.DEADLINE_EXCEEDED,
                    grpc.StatusCode.RESOURCE_EXHAUSTED
                ]:
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    raise
    
    @asynccontextmanager
    async def call_streaming(
        self,
        stub_method: Callable,
        request_iterator: Optional[Any] = None,
        timeout: Optional[float] = None,
        metadata: Optional[List[tuple]] = None
    ):
        """调用流式RPC"""
        if not self._connected:
            await self.connect()
        
        timeout = timeout or self.config.timeout
        
        try:
            if request_iterator:
                # 客户端流或双向流
                call = stub_method(
                    request_iterator,
                    timeout=timeout,
                    metadata=metadata
                )
            else:
                # 服务端流
                call = stub_method(
                    timeout=timeout,
                    metadata=metadata
                )
            
            yield call
            
        except grpc.RpcError as e:
            logger.error(
                "gRPC流式调用失败",
                service=self.config.name,
                method=stub_method.__name__,
                code=e.code(),
                details=e.details()
            )
            raise
    
    @property
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self._connected


class GrpcClientPool:
    """gRPC客户端连接池"""
    
    def __init__(self):
        self._clients: Dict[str, List[GrpcClient]] = {}
        self._configs: Dict[str, GrpcServiceConfig] = {}
        self._current_index: Dict[str, int] = {}
        self._lock = asyncio.Lock()
    
    async def add_service(
        self,
        config: GrpcServiceConfig,
        pool_size: int = 5
    ) -> None:
        """添加服务到连接池"""
        async with self._lock:
            if config.name in self._clients:
                logger.warning(
                    "gRPC服务已存在，将替换",
                    service=config.name
                )
                await self.remove_service(config.name)
            
            self._configs[config.name] = config
            self._clients[config.name] = []
            self._current_index[config.name] = 0
            
            # 创建连接池
            for i in range(pool_size):
                client = GrpcClient(config)
                await client.connect()
                self._clients[config.name].append(client)
            
            logger.info(
                "gRPC服务连接池创建成功",
                service=config.name,
                pool_size=pool_size
            )
    
    async def remove_service(self, service_name: str) -> None:
        """从连接池移除服务"""
        async with self._lock:
            if service_name in self._clients:
                clients = self._clients[service_name]
                for client in clients:
                    await client.disconnect()
                
                del self._clients[service_name]
                del self._configs[service_name]
                del self._current_index[service_name]
                
                logger.info(
                    "gRPC服务已从连接池移除",
                    service=service_name
                )
    
    def get_client(self, service_name: str) -> GrpcClient:
        """获取客户端（负载均衡）"""
        if service_name not in self._clients:
            raise ValueError(f"gRPC服务不存在: {service_name}")
        
        clients = self._clients[service_name]
        if not clients:
            raise RuntimeError(f"gRPC服务无可用连接: {service_name}")
        
        # 轮询负载均衡
        index = self._current_index[service_name]
        client = clients[index]
        self._current_index[service_name] = (index + 1) % len(clients)
        
        return client
    
    async def health_check(self) -> Dict[str, bool]:
        """健康检查"""
        results = {}
        
        for service_name, clients in self._clients.items():
            healthy_count = sum(1 for client in clients if client.is_connected)
            results[service_name] = healthy_count > 0
        
        return results
    
    async def close_all(self) -> None:
        """关闭所有连接"""
        async with self._lock:
            for service_name in list(self._clients.keys()):
                await self.remove_service(service_name)
        
        logger.info("所有gRPC连接已关闭")
    
    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取连接池统计信息"""
        stats = {}
        
        for service_name, clients in self._clients.items():
            config = self._configs[service_name]
            healthy_count = sum(1 for client in clients if client.is_connected)
            
            stats[service_name] = {
                "total_connections": len(clients),
                "healthy_connections": healthy_count,
                "target": f"{config.host}:{config.port}",
                "secure": config.secure,
                "health_ratio": healthy_count / len(clients) if clients else 0
            }
        
        return stats 