"""
服务注册中心

管理五诊服务的注册、发现和健康检查
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum

import aiohttp
import grpc
from grpc import aio as aio_grpc

from ..config.settings import get_settings


logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """服务状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceEndpoint:
    """服务端点"""
    service_name: str
    service_type: str  # grpc, http, websocket
    host: str
    port: int
    path: str = ""
    protocol: str = "http"
    
    @property
    def url(self) -> str:
        """获取完整URL"""
        if self.service_type=="grpc":
            return f"{self.host}:{self.port}"
        else:
            return f"{self.protocol}://{self.host}:{self.port}{self.path}"
    
    @property
    def health_check_url(self) -> str:
        """健康检查URL"""
        if self.service_type=="grpc":
            return self.url
        else:
            return f"{self.protocol}://{self.host}:{self.port}/health"


@dataclass
class ServiceInfo:
    """服务信息"""
    service_name: str
    endpoints: List[ServiceEndpoint] = field(default_factory=list)
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_health_check: Optional[datetime] = None
    health_check_interval: int = 30  # 秒
    failure_count: int = 0
    max_failures: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_healthy(self) -> bool:
        """是否健康"""
        return self.status==ServiceStatus.HEALTHY
    
    @property
    def is_available(self) -> bool:
        """是否可用"""
        return self.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]
    
    @property
    def primary_endpoint(self) -> Optional[ServiceEndpoint]:
        """主要端点"""
        return self.endpoints[0] if self.endpoints else None


class ServiceRegistry:
    """服务注册中心"""
    
    def __init__(self):
        self.settings = get_settings()
        self.services: Dict[str, ServiceInfo] = {}
        self.service_clients: Dict[str, Any] = {}
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """初始化服务注册中心"""
        if self._initialized:
            return
            
        logger.info("初始化服务注册中心...")
        
        try:
            # 注册五诊服务
            await self._register_default_services()
            
            # 启动健康检查
            await self._start_health_checks()
            
            self._initialized = True
            logger.info("服务注册中心初始化完成")
            
        except Exception as e:
            logger.error(f"服务注册中心初始化失败: {e}")
            raise
    
    async def _register_default_services(self) -> None:
        """注册默认服务"""
        # 从配置文件读取服务信息
        services_config = self.settings.get("services", {})
        
        # 望诊服务
        look_service = ServiceInfo(
            service_name="look-service",
            endpoints=[
                ServiceEndpoint(
                    service_name="look-service",
                    service_type="grpc",
                    host=services_config.get("look_service", {}).get("host", "localhost"),
                    port=services_config.get("look_service", {}).get("port", 50051)
                ),
                ServiceEndpoint(
                    service_name="look-service",
                    service_type="http",
                    host=services_config.get("look_service", {}).get("host", "localhost"),
                    port=services_config.get("look_service", {}).get("http_port", 8001),
                    path="/api/v1/look"
                )
            ],
            metadata={"version": "1.0.0", "capabilities": ["face_analysis", "tongue_analysis"]}
        )
        await self.register_service(look_service)
        
        # 闻诊服务
        listen_service = ServiceInfo(
            service_name="listen-service",
            endpoints=[
                ServiceEndpoint(
                    service_name="listen-service",
                    service_type="grpc",
                    host=services_config.get("listen_service", {}).get("host", "localhost"),
                    port=services_config.get("listen_service", {}).get("port", 50052)
                ),
                ServiceEndpoint(
                    service_name="listen-service",
                    service_type="http",
                    host=services_config.get("listen_service", {}).get("host", "localhost"),
                    port=services_config.get("listen_service", {}).get("http_port", 8002),
                    path="/api/v1/listen"
                )
            ],
            metadata={"version": "1.0.0", "capabilities": ["voice_analysis", "breath_analysis"]}
        )
        await self.register_service(listen_service)
        
        # 问诊服务
        inquiry_service = ServiceInfo(
            service_name="inquiry-service",
            endpoints=[
                ServiceEndpoint(
                    service_name="inquiry-service",
                    service_type="grpc",
                    host=services_config.get("inquiry_service", {}).get("host", "localhost"),
                    port=services_config.get("inquiry_service", {}).get("port", 50053)
                ),
                ServiceEndpoint(
                    service_name="inquiry-service",
                    service_type="http",
                    host=services_config.get("inquiry_service", {}).get("host", "localhost"),
                    port=services_config.get("inquiry_service", {}).get("http_port", 8003),
                    path="/api/v1/inquiry"
                )
            ],
            metadata={"version": "1.0.0", "capabilities": ["symptom_analysis", "history_analysis"]}
        )
        await self.register_service(inquiry_service)
        
        # 切诊服务
        palpation_service = ServiceInfo(
            service_name="palpation-service",
            endpoints=[
                ServiceEndpoint(
                    service_name="palpation-service",
                    service_type="grpc",
                    host=services_config.get("palpation_service", {}).get("host", "localhost"),
                    port=services_config.get("palpation_service", {}).get("port", 50054)
                ),
                ServiceEndpoint(
                    service_name="palpation-service",
                    service_type="http",
                    host=services_config.get("palpation_service", {}).get("host", "localhost"),
                    port=services_config.get("palpation_service", {}).get("http_port", 8004),
                    path="/api/v1/palpation"
                )
            ],
            metadata={"version": "1.0.0", "capabilities": ["pulse_analysis", "pressure_analysis"]}
        )
        await self.register_service(palpation_service)
        
        # 算诊服务
        calculation_service = ServiceInfo(
            service_name="calculation-service",
            endpoints=[
                ServiceEndpoint(
                    service_name="calculation-service",
                    service_type="grpc",
                    host=services_config.get("calculation_service", {}).get("host", "localhost"),
                    port=services_config.get("calculation_service", {}).get("port", 50055)
                ),
                ServiceEndpoint(
                    service_name="calculation-service",
                    service_type="http",
                    host=services_config.get("calculation_service", {}).get("host", "localhost"),
                    port=services_config.get("calculation_service", {}).get("http_port", 8005),
                    path="/api/v1/calculation"
                )
            ],
            metadata={"version": "1.0.0", "capabilities": ["constitution_analysis", "risk_assessment"]}
        )
        await self.register_service(calculation_service)
    
    async def register_service(self, service_info: ServiceInfo) -> None:
        """注册服务"""
        self.services[service_info.service_name] = service_info
        logger.info(f"注册服务: {service_info.service_name}")
        
        # 立即进行健康检查
        await self._health_check_service(service_info.service_name)
    
    async def unregister_service(self, service_name: str) -> None:
        """注销服务"""
        if service_name in self.services:
            # 停止健康检查
            if service_name in self.health_check_tasks:
                self.health_check_tasks[service_name].cancel()
                del self.health_check_tasks[service_name]
            
            # 关闭客户端连接
            if service_name in self.service_clients:
                client = self.service_clients[service_name]
                if hasattr(client, 'close'):
                    await client.close()
                del self.service_clients[service_name]
            
            del self.services[service_name]
            logger.info(f"注销服务: {service_name}")
    
    async def get_service_info(self, service_name: str) -> Optional[ServiceInfo]:
        """获取服务信息"""
        return self.services.get(service_name)
    
    async def get_available_services(self) -> List[str]:
        """获取可用服务列表"""
        available = []
        for service_name, service_info in self.services.items():
            if service_info.is_available:
                available.append(service_name)
        return available
    
    async def get_service_client(self, service_name: str) -> Optional[Any]:
        """获取服务客户端"""
        if service_name not in self.services:
            logger.warning(f"服务未注册: {service_name}")
            return None
        
        service_info = self.services[service_name]
        if not service_info.is_available:
            logger.warning(f"服务不可用: {service_name}")
            return None
        
        # 如果客户端已存在，直接返回
        if service_name in self.service_clients:
            return self.service_clients[service_name]
        
        # 创建新的客户端
        client = await self._create_service_client(service_info)
        if client:
            self.service_clients[service_name] = client
        
        return client
    
    async def _create_service_client(self, service_info: ServiceInfo) -> Optional[Any]:
        """创建服务客户端"""
        primary_endpoint = service_info.primary_endpoint
        if not primary_endpoint:
            return None
        
        try:
            if primary_endpoint.service_type=="grpc":
                # 创建gRPC客户端
                channel = aio_grpc.insecure_channel(primary_endpoint.url)
                # 这里需要根据具体的gRPC服务定义创建stub
                # 暂时返回channel，实际使用时需要创建具体的stub
                return channel
            else:
                # 创建HTTP客户端
                session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=30),
                    connector=aiohttp.TCPConnector(limit=100)
                )
                return session
                
        except Exception as e:
            logger.error(f"创建服务客户端失败: {service_info.service_name}, 错误: {e}")
            return None
    
    async def _start_health_checks(self) -> None:
        """启动健康检查"""
        for service_name in self.services:
            task = asyncio.create_task(self._health_check_loop(service_name))
            self.health_check_tasks[service_name] = task
    
    async def _health_check_loop(self, service_name: str) -> None:
        """健康检查循环"""
        while service_name in self.services:
            try:
                await self._health_check_service(service_name)
                service_info = self.services[service_name]
                await asyncio.sleep(service_info.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"健康检查循环异常: {service_name}, 错误: {e}")
                await asyncio.sleep(30)  # 异常时等待30秒再重试
    
    async def _health_check_service(self, service_name: str) -> None:
        """检查单个服务健康状态"""
        if service_name not in self.services:
            return
        
        service_info = self.services[service_name]
        
        try:
            # 检查所有端点
            healthy_endpoints = 0
            total_endpoints = len(service_info.endpoints)
            
            for endpoint in service_info.endpoints:
                is_healthy = await self._check_endpoint_health(endpoint)
                if is_healthy:
                    healthy_endpoints+=1
            
            # 更新服务状态
            if healthy_endpoints==total_endpoints:
                service_info.status = ServiceStatus.HEALTHY
                service_info.failure_count = 0
            elif healthy_endpoints > 0:
                service_info.status = ServiceStatus.DEGRADED
                service_info.failure_count = 0
            else:
                service_info.failure_count+=1
                if service_info.failure_count>=service_info.max_failures:
                    service_info.status = ServiceStatus.UNHEALTHY
                else:
                    service_info.status = ServiceStatus.DEGRADED
            
            service_info.last_health_check = datetime.utcnow()
            
            logger.debug(f"健康检查完成: {service_name}, 状态: {service_info.status.value}")
            
        except Exception as e:
            service_info.status = ServiceStatus.UNKNOWN
            service_info.failure_count+=1
            logger.warning(f"健康检查失败: {service_name}, 错误: {e}")
    
    async def _check_endpoint_health(self, endpoint: ServiceEndpoint) -> bool:
        """检查端点健康状态"""
        try:
            if endpoint.service_type=="grpc":
                return await self._check_grpc_health(endpoint)
            else:
                return await self._check_http_health(endpoint)
        except Exception as e:
            logger.debug(f"端点健康检查失败: {endpoint.url}, 错误: {e}")
            return False
    
    async def _check_grpc_health(self, endpoint: ServiceEndpoint) -> bool:
        """检查gRPC端点健康状态"""
        try:
            channel = aio_grpc.insecure_channel(endpoint.url)
            
            # 使用gRPC健康检查协议
            # 这里需要导入grpc_health.v1.health_pb2_grpc
            # 暂时使用简单的连接测试
            
            # 尝试连接
            await channel.channel_ready()
            await channel.close()
            return True
            
        except Exception:
            return False
    
    async def _check_http_health(self, endpoint: ServiceEndpoint) -> bool:
        """检查HTTP端点健康状态"""
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=5)
            ) as session:
                async with session.get(endpoint.health_check_url) as response:
                    return response.status==200
        except Exception:
            return False
    
    async def health_check_all(self) -> Dict[str, ServiceStatus]:
        """检查所有服务健康状态"""
        results = {}
        tasks = []
        
        for service_name in self.services:
            task = asyncio.create_task(self._health_check_service(service_name))
            tasks.append((service_name, task))
        
        # 等待所有健康检查完成
        for service_name, task in tasks:
            try:
                await task
                results[service_name] = self.services[service_name].status
            except Exception as e:
                logger.warning(f"健康检查失败: {service_name}, 错误: {e}")
                results[service_name] = ServiceStatus.UNKNOWN
        
        return results
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """获取服务指标"""
        total_services = len(self.services)
        healthy_services = sum(1 for s in self.services.values() if s.status==ServiceStatus.HEALTHY)
        degraded_services = sum(1 for s in self.services.values() if s.status==ServiceStatus.DEGRADED)
        unhealthy_services = sum(1 for s in self.services.values() if s.status==ServiceStatus.UNHEALTHY)
        
        return {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "degraded_services": degraded_services,
            "unhealthy_services": unhealthy_services,
            "availability_rate": healthy_services / max(total_services, 1),
            "service_details": {
                name: {
                    "status": info.status.value,
                    "last_health_check": info.last_health_check.isoformat() if info.last_health_check else None,
                    "failure_count": info.failure_count,
                    "endpoints_count": len(info.endpoints)
                }
                for name, info in self.services.items()
            }
        }
    
    async def update_service_metadata(self, service_name: str, metadata: Dict[str, Any]) -> None:
        """更新服务元数据"""
        if service_name in self.services:
            self.services[service_name].metadata.update(metadata)
            logger.info(f"更新服务元数据: {service_name}")
    
    async def get_service_by_capability(self, capability: str) -> List[str]:
        """根据能力获取服务"""
        matching_services = []
        for service_name, service_info in self.services.items():
            capabilities = service_info.metadata.get("capabilities", [])
            if capability in capabilities and service_info.is_available:
                matching_services.append(service_name)
        return matching_services
    
    async def close(self) -> None:
        """关闭服务注册中心"""
        logger.info("关闭服务注册中心...")
        
        # 取消所有健康检查任务
        for task in self.health_check_tasks.values():
            task.cancel()
        
        # 等待任务完成
        if self.health_check_tasks:
            await asyncio.gather(*self.health_check_tasks.values(), return_exceptions=True)
        
        # 关闭所有客户端连接
        for client in self.service_clients.values():
            try:
                if hasattr(client, 'close'):
                    await client.close()
            except Exception as e:
                logger.warning(f"关闭客户端连接失败: {e}")
        
        self.services.clear()
        self.service_clients.clear()
        self.health_check_tasks.clear()
        
        logger.info("服务注册中心已关闭")