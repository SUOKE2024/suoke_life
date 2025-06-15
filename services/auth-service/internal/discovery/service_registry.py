"""
服务发现与注册中心

提供服务注册、发现和健康检查功能，支持负载均衡。
"""
import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import socket
import aiohttp

from internal.config.settings import get_settings
from internal.cache.redis_cache import get_redis_cache

logger = logging.getLogger(__name__)
settings = get_settings()


class ServiceStatus(Enum):
    """服务状态"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    STARTING = "starting"
    STOPPING = "stopping"


class LoadBalanceStrategy(Enum):
    """负载均衡策略"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    CONSISTENT_HASH = "consistent_hash"


@dataclass
class ServiceInstance:
    """服务实例"""
    id: str
    name: str
    host: str
    port: int
    version: str = "1.0.0"
    weight: int = 1
    status: ServiceStatus = ServiceStatus.UNKNOWN
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 健康检查配置
    health_check_url: Optional[str] = None
    health_check_interval: int = 30  # 秒
    health_check_timeout: int = 5    # 秒
    
    # 统计信息
    last_health_check: Optional[datetime] = None
    consecutive_failures: int = 0
    total_requests: int = 0
    active_connections: int = 0
    response_time_avg: float = 0.0
    
    # 注册信息
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def address(self) -> str:
        """获取服务地址"""
        return f"{self.host}:{self.port}"
    
    @property
    def is_healthy(self) -> bool:
        """检查服务是否健康"""
        return self.status == ServiceStatus.HEALTHY
    
    @property
    def load_score(self) -> float:
        """计算负载评分（越低越好）"""
        base_score = self.active_connections / max(self.weight, 1)
        
        # 考虑响应时间
        time_penalty = self.response_time_avg / 1000.0  # 转换为秒
        
        # 考虑失败次数
        failure_penalty = self.consecutive_failures * 0.1
        
        return base_score + time_penalty + failure_penalty


class ServiceRegistry:
    """服务注册中心"""
    
    def __init__(self):
        self.cache = get_redis_cache()
        self.services: Dict[str, Dict[str, ServiceInstance]] = {}
        self.load_balancers: Dict[str, 'LoadBalancer'] = {}
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
        self.is_running = False
        
        # Redis键前缀
        self.REGISTRY_PREFIX = "service_registry:"
        self.INSTANCE_PREFIX = "service_instance:"
        self.HEALTH_PREFIX = "service_health:"
        
    async def start(self):
        """启动服务注册中心"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # 启动健康检查任务
        asyncio.create_task(self._health_check_loop())
        
        # 启动清理任务
        asyncio.create_task(self._cleanup_loop())
        
        logger.info("服务注册中心已启动")
    
    async def stop(self):
        """停止服务注册中心"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # 取消所有健康检查任务
        for task in self.health_check_tasks.values():
            task.cancel()
        
        await asyncio.gather(*self.health_check_tasks.values(), return_exceptions=True)
        self.health_check_tasks.clear()
        
        logger.info("服务注册中心已停止")
    
    async def register_service(self, instance: ServiceInstance) -> bool:
        """注册服务实例"""
        try:
            service_name = instance.name
            instance_id = instance.id
            
            # 存储到内存
            if service_name not in self.services:
                self.services[service_name] = {}
            
            self.services[service_name][instance_id] = instance
            
            # 存储到Redis
            redis_key = f"{self.INSTANCE_PREFIX}{service_name}:{instance_id}"
            instance_data = {
                "id": instance.id,
                "name": instance.name,
                "host": instance.host,
                "port": instance.port,
                "version": instance.version,
                "weight": instance.weight,
                "status": instance.status.value,
                "metadata": instance.metadata,
                "health_check_url": instance.health_check_url,
                "health_check_interval": instance.health_check_interval,
                "health_check_timeout": instance.health_check_timeout,
                "registered_at": instance.registered_at.isoformat(),
                "last_heartbeat": instance.last_heartbeat.isoformat()
            }
            
            await self.cache.set(redis_key, instance_data, ttl=300)  # 5分钟TTL
            
            # 添加到服务列表
            service_list_key = f"{self.REGISTRY_PREFIX}{service_name}"
            service_instances = await self.cache.get(service_list_key, default=[])
            if instance_id not in service_instances:
                service_instances.append(instance_id)
                await self.cache.set(service_list_key, service_instances, ttl=300)
            
            # 启动健康检查
            if instance.health_check_url:
                await self._start_health_check(instance)
            
            logger.info(f"服务实例注册成功: {service_name}:{instance_id} ({instance.address})")
            return True
            
        except Exception as e:
            logger.error(f"服务注册失败: {str(e)}")
            return False
    
    async def deregister_service(self, service_name: str, instance_id: str) -> bool:
        """注销服务实例"""
        try:
            # 从内存移除
            if service_name in self.services:
                self.services[service_name].pop(instance_id, None)
                if not self.services[service_name]:
                    del self.services[service_name]
            
            # 从Redis移除
            redis_key = f"{self.INSTANCE_PREFIX}{service_name}:{instance_id}"
            await self.cache.delete(redis_key)
            
            # 从服务列表移除
            service_list_key = f"{self.REGISTRY_PREFIX}{service_name}"
            service_instances = await self.cache.get(service_list_key, default=[])
            if instance_id in service_instances:
                service_instances.remove(instance_id)
                await self.cache.set(service_list_key, service_instances, ttl=300)
            
            # 停止健康检查
            health_check_key = f"{service_name}:{instance_id}"
            if health_check_key in self.health_check_tasks:
                self.health_check_tasks[health_check_key].cancel()
                del self.health_check_tasks[health_check_key]
            
            logger.info(f"服务实例注销成功: {service_name}:{instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"服务注销失败: {str(e)}")
            return False
    
    async def discover_services(self, service_name: str) -> List[ServiceInstance]:
        """发现服务实例"""
        try:
            # 先从内存获取
            if service_name in self.services:
                instances = list(self.services[service_name].values())
                # 只返回健康的实例
                return [inst for inst in instances if inst.is_healthy]
            
            # 从Redis获取
            service_list_key = f"{self.REGISTRY_PREFIX}{service_name}"
            instance_ids = await self.cache.get(service_list_key, default=[])
            
            instances = []
            for instance_id in instance_ids:
                redis_key = f"{self.INSTANCE_PREFIX}{service_name}:{instance_id}"
                instance_data = await self.cache.get(redis_key)
                
                if instance_data:
                    instance = ServiceInstance(
                        id=instance_data["id"],
                        name=instance_data["name"],
                        host=instance_data["host"],
                        port=instance_data["port"],
                        version=instance_data.get("version", "1.0.0"),
                        weight=instance_data.get("weight", 1),
                        status=ServiceStatus(instance_data.get("status", "unknown")),
                        metadata=instance_data.get("metadata", {}),
                        health_check_url=instance_data.get("health_check_url"),
                        health_check_interval=instance_data.get("health_check_interval", 30),
                        health_check_timeout=instance_data.get("health_check_timeout", 5)
                    )
                    
                    if instance.is_healthy:
                        instances.append(instance)
            
            return instances
            
        except Exception as e:
            logger.error(f"服务发现失败: {str(e)}")
            return []
    
    async def heartbeat(self, service_name: str, instance_id: str) -> bool:
        """服务心跳"""
        try:
            # 更新内存中的心跳时间
            if service_name in self.services and instance_id in self.services[service_name]:
                self.services[service_name][instance_id].last_heartbeat = datetime.utcnow()
            
            # 更新Redis中的心跳时间
            redis_key = f"{self.INSTANCE_PREFIX}{service_name}:{instance_id}"
            instance_data = await self.cache.get(redis_key)
            
            if instance_data:
                instance_data["last_heartbeat"] = datetime.utcnow().isoformat()
                await self.cache.set(redis_key, instance_data, ttl=300)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"心跳更新失败: {str(e)}")
            return False
    
    async def get_load_balancer(self, service_name: str, strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN) -> 'LoadBalancer':
        """获取负载均衡器"""
        lb_key = f"{service_name}:{strategy.value}"
        
        if lb_key not in self.load_balancers:
            self.load_balancers[lb_key] = LoadBalancer(
                service_registry=self,
                service_name=service_name,
                strategy=strategy
            )
        
        return self.load_balancers[lb_key]
    
    async def _start_health_check(self, instance: ServiceInstance):
        """启动健康检查"""
        health_check_key = f"{instance.name}:{instance.id}"
        
        if health_check_key in self.health_check_tasks:
            self.health_check_tasks[health_check_key].cancel()
        
        self.health_check_tasks[health_check_key] = asyncio.create_task(
            self._health_check_worker(instance)
        )
    
    async def _health_check_worker(self, instance: ServiceInstance):
        """健康检查工作器"""
        while self.is_running:
            try:
                await asyncio.sleep(instance.health_check_interval)
                
                if not instance.health_check_url:
                    continue
                
                # 执行健康检查
                start_time = time.time()
                is_healthy = await self._perform_health_check(instance)
                response_time = (time.time() - start_time) * 1000  # 毫秒
                
                # 更新实例状态
                instance.last_health_check = datetime.utcnow()
                instance.response_time_avg = (instance.response_time_avg + response_time) / 2
                
                if is_healthy:
                    instance.status = ServiceStatus.HEALTHY
                    instance.consecutive_failures = 0
                else:
                    instance.consecutive_failures += 1
                    if instance.consecutive_failures >= 3:
                        instance.status = ServiceStatus.UNHEALTHY
                
                # 更新Redis中的健康状态
                health_key = f"{self.HEALTH_PREFIX}{instance.name}:{instance.id}"
                health_data = {
                    "status": instance.status.value,
                    "last_check": instance.last_health_check.isoformat(),
                    "consecutive_failures": instance.consecutive_failures,
                    "response_time_avg": instance.response_time_avg
                }
                await self.cache.set(health_key, health_data, ttl=120)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"健康检查失败 {instance.name}:{instance.id}: {str(e)}")
    
    async def _perform_health_check(self, instance: ServiceInstance) -> bool:
        """执行健康检查"""
        try:
            url = f"http://{instance.host}:{instance.port}{instance.health_check_url}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, 
                    timeout=aiohttp.ClientTimeout(total=instance.health_check_timeout)
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.debug(f"健康检查失败 {instance.address}: {str(e)}")
            return False
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while self.is_running:
            try:
                await asyncio.sleep(10)  # 每10秒检查一次
                
                # 检查所有服务实例的健康状态
                for service_name, instances in self.services.items():
                    for instance in instances.values():
                        if not instance.health_check_url:
                            continue
                        
                        # 如果健康检查任务不存在，重新启动
                        health_check_key = f"{instance.name}:{instance.id}"
                        if health_check_key not in self.health_check_tasks:
                            await self._start_health_check(instance)
                
            except Exception as e:
                logger.error(f"健康检查循环错误: {str(e)}")
    
    async def _cleanup_loop(self):
        """清理循环"""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # 每分钟清理一次
                
                current_time = datetime.utcnow()
                expired_instances = []
                
                # 检查过期的服务实例
                for service_name, instances in self.services.items():
                    for instance_id, instance in instances.items():
                        # 如果超过5分钟没有心跳，标记为过期
                        if (current_time - instance.last_heartbeat).total_seconds() > 300:
                            expired_instances.append((service_name, instance_id))
                
                # 清理过期实例
                for service_name, instance_id in expired_instances:
                    await self.deregister_service(service_name, instance_id)
                    logger.info(f"清理过期服务实例: {service_name}:{instance_id}")
                
            except Exception as e:
                logger.error(f"清理循环错误: {str(e)}")
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """获取注册中心统计信息"""
        total_services = len(self.services)
        total_instances = sum(len(instances) for instances in self.services.values())
        healthy_instances = sum(
            len([inst for inst in instances.values() if inst.is_healthy])
            for instances in self.services.values()
        )
        
        return {
            "total_services": total_services,
            "total_instances": total_instances,
            "healthy_instances": healthy_instances,
            "unhealthy_instances": total_instances - healthy_instances,
            "active_health_checks": len(self.health_check_tasks),
            "load_balancers": len(self.load_balancers),
            "is_running": self.is_running
        }


class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, service_registry: ServiceRegistry, service_name: str, strategy: LoadBalanceStrategy):
        self.service_registry = service_registry
        self.service_name = service_name
        self.strategy = strategy
        self.current_index = 0
        self.request_counts: Dict[str, int] = {}
    
    async def select_instance(self, request_context: Optional[Dict[str, Any]] = None) -> Optional[ServiceInstance]:
        """选择服务实例"""
        instances = await self.service_registry.discover_services(self.service_name)
        
        if not instances:
            return None
        
        if self.strategy == LoadBalanceStrategy.ROUND_ROBIN:
            return self._round_robin_select(instances)
        elif self.strategy == LoadBalanceStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(instances)
        elif self.strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return self._least_connections_select(instances)
        elif self.strategy == LoadBalanceStrategy.RANDOM:
            return self._random_select(instances)
        elif self.strategy == LoadBalanceStrategy.CONSISTENT_HASH:
            return self._consistent_hash_select(instances, request_context)
        else:
            return self._round_robin_select(instances)
    
    def _round_robin_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """轮询选择"""
        instance = instances[self.current_index % len(instances)]
        self.current_index += 1
        return instance
    
    def _weighted_round_robin_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """加权轮询选择"""
        # 构建加权列表
        weighted_instances = []
        for instance in instances:
            weighted_instances.extend([instance] * instance.weight)
        
        if not weighted_instances:
            return instances[0]
        
        instance = weighted_instances[self.current_index % len(weighted_instances)]
        self.current_index += 1
        return instance
    
    def _least_connections_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """最少连接选择"""
        return min(instances, key=lambda x: x.load_score)
    
    def _random_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """随机选择"""
        import random
        return random.choice(instances)
    
    def _consistent_hash_select(self, instances: List[ServiceInstance], request_context: Optional[Dict[str, Any]]) -> ServiceInstance:
        """一致性哈希选择"""
        if not request_context or 'hash_key' not in request_context:
            return self._round_robin_select(instances)
        
        hash_key = str(request_context['hash_key'])
        hash_value = hash(hash_key) % len(instances)
        return instances[hash_value]
    
    async def record_request(self, instance: ServiceInstance, success: bool, response_time: float):
        """记录请求结果"""
        instance.total_requests += 1
        
        if success:
            # 更新平均响应时间
            instance.response_time_avg = (
                (instance.response_time_avg * (instance.total_requests - 1) + response_time) 
                / instance.total_requests
            )
        else:
            # 增加失败计数
            instance.consecutive_failures += 1


# 全局服务注册中心实例
_service_registry: Optional[ServiceRegistry] = None


def get_service_registry() -> ServiceRegistry:
    """获取服务注册中心实例"""
    global _service_registry
    if _service_registry is None:
        _service_registry = ServiceRegistry()
    return _service_registry


async def init_service_registry() -> None:
    """初始化服务注册中心"""
    registry = get_service_registry()
    await registry.start()


async def shutdown_service_registry() -> None:
    """关闭服务注册中心"""
    global _service_registry
    if _service_registry:
        await _service_registry.stop()
        _service_registry = None


def get_local_ip() -> str:
    """获取本地IP地址"""
    try:
        # 连接到一个远程地址来获取本地IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1" 