"""
gRPC客户端管理器

提供高效的gRPC客户端连接管理，支持连接池、重试机制和负载均衡。
"""
import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import grpc
from grpc import aio
import random

from internal.config.settings import get_settings
from internal.discovery.service_registry import get_service_registry, LoadBalanceStrategy
from internal.cache.redis_cache import get_redis_cache

logger = logging.getLogger(__name__)
settings = get_settings()


class ConnectionState(Enum):
    """连接状态"""
    IDLE = "idle"
    CONNECTING = "connecting"
    READY = "ready"
    TRANSIENT_FAILURE = "transient_failure"
    SHUTDOWN = "shutdown"


@dataclass
class GrpcClientConfig:
    """gRPC客户端配置"""
    service_name: str
    stub_class: Type
    max_connections: int = 5
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: float = 30.0
    keepalive_time: int = 30
    keepalive_timeout: int = 5
    keepalive_permit_without_calls: bool = True
    max_receive_message_length: int = 4 * 1024 * 1024  # 4MB
    max_send_message_length: int = 4 * 1024 * 1024     # 4MB
    compression: Optional[grpc.Compression] = None
    load_balance_strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN


@dataclass
class ConnectionMetrics:
    """连接指标"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    last_used: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def avg_response_time(self) -> float:
        """平均响应时间"""
        if self.successful_requests == 0:
            return 0.0
        return self.total_response_time / self.successful_requests


class GrpcConnection:
    """gRPC连接"""
    
    def __init__(self, target: str, config: GrpcClientConfig):
        self.target = target
        self.config = config
        self.channel: Optional[aio.Channel] = None
        self.stub: Optional[Any] = None
        self.state = ConnectionState.IDLE
        self.metrics = ConnectionMetrics()
        self._lock = asyncio.Lock()
    
    async def connect(self) -> bool:
        """建立连接"""
        async with self._lock:
            if self.state == ConnectionState.READY:
                return True
            
            try:
                self.state = ConnectionState.CONNECTING
                
                # 配置gRPC选项
                options = [
                    ('grpc.keepalive_time_ms', self.config.keepalive_time * 1000),
                    ('grpc.keepalive_timeout_ms', self.config.keepalive_timeout * 1000),
                    ('grpc.keepalive_permit_without_calls', self.config.keepalive_permit_without_calls),
                    ('grpc.http2.max_pings_without_data', 0),
                    ('grpc.http2.min_time_between_pings_ms', 10000),
                    ('grpc.http2.min_ping_interval_without_data_ms', 300000),
                    ('grpc.max_receive_message_length', self.config.max_receive_message_length),
                    ('grpc.max_send_message_length', self.config.max_send_message_length),
                ]
                
                # 创建通道
                self.channel = aio.insecure_channel(
                    self.target,
                    options=options,
                    compression=self.config.compression
                )
                
                # 等待连接就绪
                await asyncio.wait_for(
                    self.channel.channel_ready(),
                    timeout=self.config.timeout
                )
                
                # 创建存根
                self.stub = self.config.stub_class(self.channel)
                
                self.state = ConnectionState.READY
                logger.debug(f"gRPC连接建立成功: {self.target}")
                return True
                
            except Exception as e:
                self.state = ConnectionState.TRANSIENT_FAILURE
                logger.error(f"gRPC连接失败 {self.target}: {str(e)}")
                return False
    
    async def close(self):
        """关闭连接"""
        async with self._lock:
            if self.channel:
                await self.channel.close()
                self.channel = None
                self.stub = None
                self.state = ConnectionState.SHUTDOWN
                logger.debug(f"gRPC连接已关闭: {self.target}")
    
    async def call(self, method_name: str, request: Any, **kwargs) -> Any:
        """调用gRPC方法"""
        if self.state != ConnectionState.READY:
            if not await self.connect():
                raise grpc.RpcError("连接不可用")
        
        start_time = time.time()
        
        try:
            # 获取方法
            method = getattr(self.stub, method_name)
            
            # 设置超时
            timeout = kwargs.pop('timeout', self.config.timeout)
            
            # 调用方法
            response = await method(request, timeout=timeout, **kwargs)
            
            # 记录成功指标
            response_time = time.time() - start_time
            self.metrics.total_requests += 1
            self.metrics.successful_requests += 1
            self.metrics.total_response_time += response_time
            self.metrics.last_used = datetime.utcnow()
            
            return response
            
        except Exception as e:
            # 记录失败指标
            self.metrics.total_requests += 1
            self.metrics.failed_requests += 1
            self.metrics.last_used = datetime.utcnow()
            
            # 如果是连接错误，标记连接状态
            if isinstance(e, grpc.RpcError):
                if e.code() in [grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED]:
                    self.state = ConnectionState.TRANSIENT_FAILURE
            
            raise
    
    @property
    def is_healthy(self) -> bool:
        """检查连接是否健康"""
        return self.state == ConnectionState.READY
    
    @property
    def is_idle(self) -> bool:
        """检查连接是否空闲"""
        if not self.is_healthy:
            return False
        
        # 如果超过5分钟没有使用，认为是空闲的
        idle_time = datetime.utcnow() - self.metrics.last_used
        return idle_time.total_seconds() > 300


class GrpcConnectionPool:
    """gRPC连接池"""
    
    def __init__(self, config: GrpcClientConfig):
        self.config = config
        self.connections: List[GrpcConnection] = []
        self.current_index = 0
        self._lock = asyncio.Lock()
        self.service_registry = get_service_registry()
        self.cache = get_redis_cache()
    
    async def get_connection(self) -> GrpcConnection:
        """获取连接"""
        async with self._lock:
            # 尝试获取健康的连接
            healthy_connections = [conn for conn in self.connections if conn.is_healthy]
            
            if healthy_connections:
                # 使用负载均衡策略选择连接
                return self._select_connection(healthy_connections)
            
            # 如果没有健康连接，尝试创建新连接
            if len(self.connections) < self.config.max_connections:
                target = await self._get_service_target()
                if target:
                    connection = GrpcConnection(target, self.config)
                    if await connection.connect():
                        self.connections.append(connection)
                        return connection
            
            # 尝试重连现有连接
            for connection in self.connections:
                if await connection.connect():
                    return connection
            
            raise grpc.RpcError("无可用连接")
    
    def _select_connection(self, connections: List[GrpcConnection]) -> GrpcConnection:
        """选择连接"""
        if self.config.load_balance_strategy == LoadBalanceStrategy.ROUND_ROBIN:
            connection = connections[self.current_index % len(connections)]
            self.current_index += 1
            return connection
        elif self.config.load_balance_strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return min(connections, key=lambda c: c.metrics.total_requests)
        elif self.config.load_balance_strategy == LoadBalanceStrategy.RANDOM:
            return random.choice(connections)
        else:
            return connections[0]
    
    async def _get_service_target(self) -> Optional[str]:
        """获取服务目标地址"""
        try:
            # 从服务注册中心获取实例
            load_balancer = await self.service_registry.get_load_balancer(
                self.config.service_name,
                self.config.load_balance_strategy
            )
            
            instance = await load_balancer.select_instance()
            if instance:
                return f"{instance.host}:{instance.port}"
            
            return None
            
        except Exception as e:
            logger.error(f"获取服务目标失败: {str(e)}")
            return None
    
    async def close_all(self):
        """关闭所有连接"""
        async with self._lock:
            for connection in self.connections:
                await connection.close()
            self.connections.clear()
    
    async def cleanup_idle_connections(self):
        """清理空闲连接"""
        async with self._lock:
            active_connections = []
            for connection in self.connections:
                if connection.is_idle:
                    await connection.close()
                    logger.debug(f"清理空闲连接: {connection.target}")
                else:
                    active_connections.append(connection)
            
            self.connections = active_connections
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """获取连接池统计"""
        total_connections = len(self.connections)
        healthy_connections = len([c for c in self.connections if c.is_healthy])
        idle_connections = len([c for c in self.connections if c.is_idle])
        
        total_requests = sum(c.metrics.total_requests for c in self.connections)
        successful_requests = sum(c.metrics.successful_requests for c in self.connections)
        
        return {
            "service_name": self.config.service_name,
            "total_connections": total_connections,
            "healthy_connections": healthy_connections,
            "idle_connections": idle_connections,
            "max_connections": self.config.max_connections,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
            "connections": [
                {
                    "target": conn.target,
                    "state": conn.state.value,
                    "metrics": {
                        "total_requests": conn.metrics.total_requests,
                        "success_rate": conn.metrics.success_rate,
                        "avg_response_time": conn.metrics.avg_response_time,
                        "last_used": conn.metrics.last_used.isoformat()
                    }
                }
                for conn in self.connections
            ]
        }


class GrpcClientManager:
    """gRPC客户端管理器"""
    
    def __init__(self):
        self.pools: Dict[str, GrpcConnectionPool] = {}
        self.configs: Dict[str, GrpcClientConfig] = {}
        self.is_running = False
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """启动客户端管理器"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # 启动清理任务
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("gRPC客户端管理器已启动")
    
    async def stop(self):
        """停止客户端管理器"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # 停止清理任务
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # 关闭所有连接池
        for pool in self.pools.values():
            await pool.close_all()
        
        self.pools.clear()
        logger.info("gRPC客户端管理器已停止")
    
    def register_service(self, config: GrpcClientConfig):
        """注册服务配置"""
        self.configs[config.service_name] = config
        logger.info(f"注册gRPC服务配置: {config.service_name}")
    
    async def get_client(self, service_name: str) -> Any:
        """获取gRPC客户端"""
        if service_name not in self.configs:
            raise ValueError(f"未注册的服务: {service_name}")
        
        if service_name not in self.pools:
            config = self.configs[service_name]
            self.pools[service_name] = GrpcConnectionPool(config)
        
        pool = self.pools[service_name]
        connection = await pool.get_connection()
        
        return GrpcClientWrapper(connection, pool)
    
    async def call_with_retry(
        self,
        service_name: str,
        method_name: str,
        request: Any,
        max_retries: Optional[int] = None,
        **kwargs
    ) -> Any:
        """带重试的gRPC调用"""
        config = self.configs.get(service_name)
        if not config:
            raise ValueError(f"未注册的服务: {service_name}")
        
        max_retries = max_retries or config.max_retries
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                client = await self.get_client(service_name)
                return await client.call(method_name, request, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                if attempt < max_retries:
                    # 计算重试延迟（指数退避）
                    delay = config.retry_delay * (2 ** attempt)
                    logger.warning(f"gRPC调用失败，{delay}秒后重试 (第{attempt + 1}次): {str(e)}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"gRPC调用最终失败: {str(e)}")
        
        raise last_exception
    
    async def _cleanup_loop(self):
        """清理循环"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # 每5分钟清理一次
                
                for pool in self.pools.values():
                    await pool.cleanup_idle_connections()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"连接池清理失败: {str(e)}")
    
    def get_manager_stats(self) -> Dict[str, Any]:
        """获取管理器统计"""
        return {
            "is_running": self.is_running,
            "registered_services": len(self.configs),
            "active_pools": len(self.pools),
            "pools": {
                name: pool.get_pool_stats()
                for name, pool in self.pools.items()
            }
        }


class GrpcClientWrapper:
    """gRPC客户端包装器"""
    
    def __init__(self, connection: GrpcConnection, pool: GrpcConnectionPool):
        self.connection = connection
        self.pool = pool
    
    async def call(self, method_name: str, request: Any, **kwargs) -> Any:
        """调用gRPC方法"""
        return await self.connection.call(method_name, request, **kwargs)
    
    @property
    def stub(self) -> Any:
        """获取gRPC存根"""
        return self.connection.stub


# 全局gRPC客户端管理器实例
_grpc_client_manager: Optional[GrpcClientManager] = None


def get_grpc_client_manager() -> GrpcClientManager:
    """获取gRPC客户端管理器实例"""
    global _grpc_client_manager
    if _grpc_client_manager is None:
        _grpc_client_manager = GrpcClientManager()
    return _grpc_client_manager


async def init_grpc_client_manager() -> None:
    """初始化gRPC客户端管理器"""
    manager = get_grpc_client_manager()
    await manager.start()


async def shutdown_grpc_client_manager() -> None:
    """关闭gRPC客户端管理器"""
    global _grpc_client_manager
    if _grpc_client_manager:
        await _grpc_client_manager.stop()
        _grpc_client_manager = None 