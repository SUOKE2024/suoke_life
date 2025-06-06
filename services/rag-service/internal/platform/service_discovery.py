"""
service_discovery - 索克生活项目模块
"""

        import random
from ..observability.metrics import MetricsCollector
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger
from typing import Dict, List, Any, Optional, Callable
import aiohttp
import asyncio
import consul
import time
import uuid

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
服务发现和注册模块 - 实现服务注册、发现和健康检查
"""



class ServiceStatus(str, Enum):
    """服务状态"""
    HEALTHY = "healthy"         # 健康
    UNHEALTHY = "unhealthy"     # 不健康
    STARTING = "starting"       # 启动中
    STOPPING = "stopping"      # 停止中
    UNKNOWN = "unknown"         # 未知

class DiscoveryBackend(str, Enum):
    """服务发现后端"""
    CONSUL = "consul"           # Consul
    ETCD = "etcd"              # etcd
    KUBERNETES = "kubernetes"   # Kubernetes
    MEMORY = "memory"          # 内存（测试用）

@dataclass
class ServiceInstance:
    """服务实例"""
    id: str
    name: str
    host: str
    port: int
    status: ServiceStatus = ServiceStatus.HEALTHY
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    health_check_url: Optional[str] = None
    last_heartbeat: float = field(default_factory=time.time)
    registered_at: float = field(default_factory=time.time)
    version: str = "1.0.0"
    
    @property
    def address(self) -> str:
        """获取服务地址"""
        return f"{self.host}:{self.port}"
    
    @property
    def is_healthy(self) -> bool:
        """检查是否健康"""
        return self.status == ServiceStatus.HEALTHY
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "status": self.status.value,
            "metadata": self.metadata,
            "tags": self.tags,
            "health_check_url": self.health_check_url,
            "last_heartbeat": self.last_heartbeat,
            "registered_at": self.registered_at,
            "version": self.version,
            "address": self.address
        }

@dataclass
class HealthCheck:
    """健康检查配置"""
    url: str
    interval: int = 30          # 检查间隔（秒）
    timeout: int = 10           # 超时时间（秒）
    deregister_critical_after: int = 300  # 失败后注销时间（秒）
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    expected_status: int = 200

class ServiceRegistry:
    """服务注册表"""
    
    def __init__(self, backend: DiscoveryBackend = DiscoveryBackend.MEMORY):
        self.backend = backend
        self.services: Dict[str, Dict[str, ServiceInstance]] = {}
        self.watchers: List[Callable] = []
        self.consul_client = None
        
        if backend == DiscoveryBackend.CONSUL:
            self._init_consul()
    
    def _init_consul(self):
        """初始化Consul客户端"""
        try:
            self.consul_client = consul.Consul()
            logger.info("Consul客户端初始化成功")
        except Exception as e:
            logger.error(f"Consul客户端初始化失败: {e}")
            self.backend = DiscoveryBackend.MEMORY
    
    async def register_service(
        self,
        service: ServiceInstance,
        health_check: Optional[HealthCheck] = None
    ) -> bool:
        """注册服务"""
        try:
            if self.backend == DiscoveryBackend.CONSUL:
                return await self._register_consul(service, health_check)
            else:
                return await self._register_memory(service)
        except Exception as e:
            logger.error(f"服务注册失败: {e}")
            return False
    
    async def _register_consul(
        self,
        service: ServiceInstance,
        health_check: Optional[HealthCheck] = None
    ) -> bool:
        """在Consul中注册服务"""
        try:
            check = None
            if health_check:
                check = consul.Check.http(
                    health_check.url,
                    interval=f"{health_check.interval}s",
                    timeout=f"{health_check.timeout}s",
                    deregister=f"{health_check.deregister_critical_after}s"
                )
            
            self.consul_client.agent.service.register(
                name=service.name,
                service_id=service.id,
                address=service.host,
                port=service.port,
                tags=service.tags,
                meta=service.metadata,
                check=check
            )
            
            logger.info(f"服务已注册到Consul: {service.name} ({service.address})")
            return True
            
        except Exception as e:
            logger.error(f"Consul服务注册失败: {e}")
            return False
    
    async def _register_memory(self, service: ServiceInstance) -> bool:
        """在内存中注册服务"""
        if service.name not in self.services:
            self.services[service.name] = {}
        
        self.services[service.name][service.id] = service
        
        # 通知观察者
        await self._notify_watchers("register", service)
        
        logger.info(f"服务已注册到内存: {service.name} ({service.address})")
        return True
    
    async def deregister_service(self, service_id: str) -> bool:
        """注销服务"""
        try:
            if self.backend == DiscoveryBackend.CONSUL:
                return await self._deregister_consul(service_id)
            else:
                return await self._deregister_memory(service_id)
        except Exception as e:
            logger.error(f"服务注销失败: {e}")
            return False
    
    async def _deregister_consul(self, service_id: str) -> bool:
        """从Consul注销服务"""
        try:
            self.consul_client.agent.service.deregister(service_id)
            logger.info(f"服务已从Consul注销: {service_id}")
            return True
        except Exception as e:
            logger.error(f"Consul服务注销失败: {e}")
            return False
    
    async def _deregister_memory(self, service_id: str) -> bool:
        """从内存注销服务"""
        for service_name, instances in self.services.items():
            if service_id in instances:
                service = instances.pop(service_id)
                
                # 如果没有实例了，删除服务
                if not instances:
                    del self.services[service_name]
                
                # 通知观察者
                await self._notify_watchers("deregister", service)
                
                logger.info(f"服务已从内存注销: {service_id}")
                return True
        
        logger.warning(f"未找到要注销的服务: {service_id}")
        return False
    
    async def discover_services(self, service_name: str) -> List[ServiceInstance]:
        """发现服务"""
        try:
            if self.backend == DiscoveryBackend.CONSUL:
                return await self._discover_consul(service_name)
            else:
                return await self._discover_memory(service_name)
        except Exception as e:
            logger.error(f"服务发现失败: {e}")
            return []
    
    async def _discover_consul(self, service_name: str) -> List[ServiceInstance]:
        """从Consul发现服务"""
        try:
            _, services = self.consul_client.health.service(service_name, passing=True)
            
            instances = []
            for service_data in services:
                service = service_data['Service']
                health = service_data['Checks']
                
                # 判断健康状态
                status = ServiceStatus.HEALTHY
                for check in health:
                    if check['Status'] != 'passing':
                        status = ServiceStatus.UNHEALTHY
                        break
                
                instance = ServiceInstance(
                    id=service['ID'],
                    name=service['Service'],
                    host=service['Address'],
                    port=service['Port'],
                    status=status,
                    metadata=service.get('Meta', {}),
                    tags=service.get('Tags', [])
                )
                instances.append(instance)
            
            return instances
            
        except Exception as e:
            logger.error(f"Consul服务发现失败: {e}")
            return []
    
    async def _discover_memory(self, service_name: str) -> List[ServiceInstance]:
        """从内存发现服务"""
        if service_name in self.services:
            return list(self.services[service_name].values())
        return []
    
    async def get_healthy_instances(self, service_name: str) -> List[ServiceInstance]:
        """获取健康的服务实例"""
        instances = await self.discover_services(service_name)
        return [instance for instance in instances if instance.is_healthy]
    
    async def update_service_status(
        self,
        service_id: str,
        status: ServiceStatus,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """更新服务状态"""
        try:
            # 在内存中更新
            for service_name, instances in self.services.items():
                if service_id in instances:
                    instances[service_id].status = status
                    instances[service_id].last_heartbeat = time.time()
                    
                    if metadata:
                        instances[service_id].metadata.update(metadata)
                    
                    # 通知观察者
                    await self._notify_watchers("update", instances[service_id])
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"服务状态更新失败: {e}")
            return False
    
    def add_watcher(self, callback: Callable):
        """添加服务变化观察者"""
        self.watchers.append(callback)
    
    def remove_watcher(self, callback: Callable):
        """移除服务变化观察者"""
        if callback in self.watchers:
            self.watchers.remove(callback)
    
    async def _notify_watchers(self, event_type: str, service: ServiceInstance):
        """通知观察者"""
        for watcher in self.watchers:
            try:
                if asyncio.iscoroutinefunction(watcher):
                    await watcher(event_type, service)
                else:
                    watcher(event_type, service)
            except Exception as e:
                logger.error(f"观察者通知失败: {e}")
    
    async def get_all_services(self) -> Dict[str, List[ServiceInstance]]:
        """获取所有服务"""
        result = {}
        for service_name, instances in self.services.items():
            result[service_name] = list(instances.values())
        return result

class HealthChecker:
    """健康检查器"""
    
    def __init__(self, registry: ServiceRegistry, metrics_collector: MetricsCollector):
        self.registry = registry
        self.metrics_collector = metrics_collector
        self.running = False
        self.check_interval = 30
        self.timeout = 10
    
    async def start(self):
        """启动健康检查"""
        if self.running:
            return
        
        self.running = True
        asyncio.create_task(self._health_check_loop())
        logger.info("健康检查器已启动")
    
    async def stop(self):
        """停止健康检查"""
        self.running = False
        logger.info("健康检查器已停止")
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while self.running:
            try:
                await self._check_all_services()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"健康检查循环错误: {e}")
                await asyncio.sleep(5)
    
    async def _check_all_services(self):
        """检查所有服务"""
        all_services = await self.registry.get_all_services()
        
        for service_name, instances in all_services.items():
            for instance in instances:
                await self._check_service_instance(instance)
    
    async def _check_service_instance(self, instance: ServiceInstance):
        """检查单个服务实例"""
        if not instance.health_check_url:
            return
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(instance.health_check_url) as response:
                    if response.status == 200:
                        if instance.status != ServiceStatus.HEALTHY:
                            await self.registry.update_service_status(
                                instance.id,
                                ServiceStatus.HEALTHY
                            )
                            logger.info(f"服务恢复健康: {instance.name} ({instance.address})")
                    else:
                        if instance.status != ServiceStatus.UNHEALTHY:
                            await self.registry.update_service_status(
                                instance.id,
                                ServiceStatus.UNHEALTHY
                            )
                            logger.warning(f"服务不健康: {instance.name} ({instance.address})")
                    
                    # 记录指标
                    await self.metrics_collector.record_histogram(
                        "service_health_check_duration",
                        time.time(),
                        {"service": instance.name, "status": "success"}
                    )
                    
        except Exception as e:
            if instance.status != ServiceStatus.UNHEALTHY:
                await self.registry.update_service_status(
                    instance.id,
                    ServiceStatus.UNHEALTHY
                )
                logger.error(f"服务健康检查失败: {instance.name} ({instance.address}) - {e}")
            
            # 记录指标
            await self.metrics_collector.record_histogram(
                "service_health_check_duration",
                time.time(),
                {"service": instance.name, "status": "error"}
            )

class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, strategy: str = "round_robin"):
        self.strategy = strategy
        self.round_robin_counters: Dict[str, int] = {}
    
    async def select_instance(
        self,
        service_name: str,
        instances: List[ServiceInstance]
    ) -> Optional[ServiceInstance]:
        """选择服务实例"""
        healthy_instances = [inst for inst in instances if inst.is_healthy]
        
        if not healthy_instances:
            return None
        
        if self.strategy == "round_robin":
            return self._round_robin_select(service_name, healthy_instances)
        elif self.strategy == "random":
            return self._random_select(healthy_instances)
        elif self.strategy == "least_connections":
            return self._least_connections_select(healthy_instances)
        else:
            return healthy_instances[0]
    
    def _round_robin_select(
        self,
        service_name: str,
        instances: List[ServiceInstance]
    ) -> ServiceInstance:
        """轮询选择"""
        if service_name not in self.round_robin_counters:
            self.round_robin_counters[service_name] = 0
        
        index = self.round_robin_counters[service_name] % len(instances)
        self.round_robin_counters[service_name] += 1
        
        return instances[index]
    
    def _random_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """随机选择"""
        return random.choice(instances)
    
    def _least_connections_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """最少连接选择"""
        # 简化实现，实际应该跟踪连接数
        return min(instances, key=lambda x: x.metadata.get("connections", 0))

class ServiceDiscovery:
    """服务发现主类"""
    
    def __init__(
        self,
        backend: DiscoveryBackend = DiscoveryBackend.MEMORY,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        self.registry = ServiceRegistry(backend)
        self.health_checker = HealthChecker(self.registry, metrics_collector) if metrics_collector else None
        self.load_balancer = LoadBalancer()
        self.local_instance: Optional[ServiceInstance] = None
    
    async def start(self):
        """启动服务发现"""
        if self.health_checker:
            await self.health_checker.start()
        logger.info("服务发现已启动")
    
    async def stop(self):
        """停止服务发现"""
        if self.local_instance:
            await self.registry.deregister_service(self.local_instance.id)
        
        if self.health_checker:
            await self.health_checker.stop()
        
        logger.info("服务发现已停止")
    
    async def register_self(
        self,
        service_name: str,
        host: str,
        port: int,
        health_check_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """注册自身服务"""
        self.local_instance = ServiceInstance(
            id=f"{service_name}-{uuid.uuid4().hex[:8]}",
            name=service_name,
            host=host,
            port=port,
            health_check_url=health_check_url,
            metadata=metadata or {},
            tags=tags or []
        )
        
        health_check = None
        if health_check_url:
            health_check = HealthCheck(url=health_check_url)
        
        success = await self.registry.register_service(self.local_instance, health_check)
        
        if success:
            logger.info(f"自身服务注册成功: {service_name} ({host}:{port})")
        else:
            logger.error(f"自身服务注册失败: {service_name}")
        
        return success
    
    async def discover_service(self, service_name: str) -> Optional[ServiceInstance]:
        """发现并选择一个服务实例"""
        instances = await self.registry.discover_services(service_name)
        return await self.load_balancer.select_instance(service_name, instances)
    
    async def discover_all_instances(self, service_name: str) -> List[ServiceInstance]:
        """发现所有服务实例"""
        return await self.registry.discover_services(service_name)
    
    async def get_healthy_instances(self, service_name: str) -> List[ServiceInstance]:
        """获取健康的服务实例"""
        return await self.registry.get_healthy_instances(service_name)
    
    def add_service_watcher(self, callback: Callable):
        """添加服务变化观察者"""
        self.registry.add_watcher(callback)
    
    async def get_service_statistics(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        all_services = await self.registry.get_all_services()
        
        total_services = len(all_services)
        total_instances = sum(len(instances) for instances in all_services.values())
        healthy_instances = 0
        
        service_stats = {}
        for service_name, instances in all_services.items():
            healthy_count = sum(1 for inst in instances if inst.is_healthy)
            healthy_instances += healthy_count
            
            service_stats[service_name] = {
                "total_instances": len(instances),
                "healthy_instances": healthy_count,
                "instances": [inst.to_dict() for inst in instances]
            }
        
        return {
            "total_services": total_services,
            "total_instances": total_instances,
            "healthy_instances": healthy_instances,
            "unhealthy_instances": total_instances - healthy_instances,
            "services": service_stats
        }

# 全局服务发现实例
_service_discovery: Optional[ServiceDiscovery] = None

def initialize_service_discovery(
    backend: DiscoveryBackend = DiscoveryBackend.MEMORY,
    metrics_collector: Optional[MetricsCollector] = None
) -> ServiceDiscovery:
    """初始化服务发现"""
    global _service_discovery
    _service_discovery = ServiceDiscovery(backend, metrics_collector)
    return _service_discovery

def get_service_discovery() -> Optional[ServiceDiscovery]:
    """获取服务发现实例"""
    return _service_discovery 