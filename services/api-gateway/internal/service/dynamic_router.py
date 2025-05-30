"""
API网关动态路由服务
支持服务发现、负载均衡和健康检查
"""
import asyncio
import logging
import time
import hashlib
import random
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import json
from urllib.parse import urljoin, urlparse

# 导入服务发现和配置中心
from ...common.service_registry.consul_client import get_consul_client, ServiceInstance
from ...common.config.config_center import get_config_center, ServiceConfig
from ...common.observability.tracing import get_tracing_manager, trace_function

logger = logging.getLogger(__name__)

class LoadBalanceStrategy(Enum):
    """负载均衡策略"""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"

class HealthStatus(Enum):
    """健康状态"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class RouteRule:
    """路由规则"""
    path_pattern: str
    service_name: str
    method: str = "*"
    headers: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, str] = field(default_factory=dict)
    weight: int = 100
    timeout: float = 30.0
    retry_count: int = 3
    circuit_breaker_enabled: bool = True
    rate_limit_enabled: bool = True
    auth_required: bool = True
    priority: int = 0

@dataclass
class ServiceEndpoint:
    """服务端点信息"""
    address: str
    port: int
    service_id: str
    weight: int = 1
    connections: int = 0
    last_used: float = 0
    health_status: str = "unknown"

class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """检查是否可以执行请求"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self):
        """记录成功"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """记录失败"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

class RateLimiter:
    """限流器"""
    
    def __init__(self, max_requests: int = 100, window_size: float = 60.0):
        self.max_requests = max_requests
        self.window_size = window_size
        self.requests = []
    
    def is_allowed(self) -> bool:
        """检查是否允许请求"""
        now = time.time()
        
        # 清理过期请求
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.window_size]
        
        # 检查是否超过限制
        if len(self.requests) >= self.max_requests:
            return False
        
        # 记录当前请求
        self.requests.append(now)
        return True

class ServiceNotAvailableError(Exception):
    """服务不可用异常"""
    pass

class DynamicRouter:
    """动态路由器"""
    
    def __init__(self, consul_client: ConsulServiceRegistry):
        self.consul = consul_client
        self.service_cache: Dict[str, List[ServiceEndpoint]] = {}
        self.load_balancer_state: Dict[str, int] = {}
        self.cache_ttl = 30  # 缓存30秒
        self.last_refresh: Dict[str, float] = {}
        self.health_check_interval = 10
        self._running = False
        
    async def start(self):
        """启动路由器"""
        self._running = True
        # 启动后台健康检查任务
        asyncio.create_task(self._health_check_loop())
        logger.info("Dynamic router started")
        
    async def stop(self):
        """停止路由器"""
        self._running = False
        logger.info("Dynamic router stopped")
        
    async def get_service_endpoint(
        self, 
        service_name: str, 
        strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN
    ) -> str:
        """获取服务端点（带负载均衡）"""
        
        # 检查缓存是否需要刷新
        await self._refresh_cache_if_needed(service_name)
        
        endpoints = self.service_cache.get(service_name, [])
        if not endpoints:
            raise ServiceNotAvailableError(f"Service {service_name} not available")
        
        # 过滤健康的端点
        healthy_endpoints = [ep for ep in endpoints if ep.health_status == "passing"]
        if not healthy_endpoints:
            # 如果没有健康的端点，使用所有端点作为降级策略
            healthy_endpoints = endpoints
            logger.warning(f"No healthy endpoints for {service_name}, using all endpoints")
        
        # 根据策略选择端点
        endpoint = self._select_endpoint(healthy_endpoints, strategy, service_name)
        
        # 更新连接计数和使用时间
        endpoint.connections += 1
        endpoint.last_used = time.time()
        
        return f"http://{endpoint.address}:{endpoint.port}"
    
    def _select_endpoint(
        self, 
        endpoints: List[ServiceEndpoint], 
        strategy: LoadBalanceStrategy,
        service_name: str
    ) -> ServiceEndpoint:
        """根据策略选择端点"""
        
        if strategy == LoadBalanceStrategy.ROUND_ROBIN:
            index = self.load_balancer_state.get(service_name, 0)
            endpoint = endpoints[index % len(endpoints)]
            self.load_balancer_state[service_name] = index + 1
            return endpoint
            
        elif strategy == LoadBalanceStrategy.RANDOM:
            return random.choice(endpoints)
            
        elif strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return min(endpoints, key=lambda ep: ep.connections)
            
        elif strategy == LoadBalanceStrategy.WEIGHTED_ROUND_ROBIN:
            # 基于权重的轮询
            total_weight = sum(ep.weight for ep in endpoints)
            if total_weight == 0:
                return endpoints[0]
                
            # 简化的加权轮询实现
            current_weight = self.load_balancer_state.get(f"{service_name}_weight", 0)
            for endpoint in endpoints:
                current_weight += endpoint.weight
                if current_weight >= total_weight:
                    self.load_balancer_state[f"{service_name}_weight"] = 0
                    return endpoint
            
            self.load_balancer_state[f"{service_name}_weight"] = current_weight
            return endpoints[0]
            
        else:
            return endpoints[0]
    
    async def _refresh_cache_if_needed(self, service_name: str):
        """如果需要则刷新缓存"""
        now = time.time()
        last_refresh = self.last_refresh.get(service_name, 0)
        
        if now - last_refresh > self.cache_ttl:
            await self._refresh_service_cache(service_name)
            self.last_refresh[service_name] = now
    
    async def _refresh_service_cache(self, service_name: str):
        """刷新服务缓存"""
        try:
            instances = self.consul.discover_service(service_name)
            endpoints = []
            
            for instance in instances:
                endpoint = ServiceEndpoint(
                    address=instance["address"],
                    port=instance["port"],
                    service_id=instance["service_id"],
                    weight=int(instance.get("meta", {}).get("weight", 1))
                )
                endpoints.append(endpoint)
            
            self.service_cache[service_name] = endpoints
            logger.debug(f"Refreshed cache for {service_name}: {len(endpoints)} endpoints")
            
        except Exception as e:
            logger.error(f"Failed to refresh cache for {service_name}: {e}")
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while self._running:
            try:
                await self._check_all_services_health()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(5)
    
    async def _check_all_services_health(self):
        """检查所有服务的健康状态"""
        for service_name, endpoints in self.service_cache.items():
        tasks = []
            for endpoint in endpoints:
                task = asyncio.create_task(
                    self._check_endpoint_health(endpoint)
                )
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_endpoint_health(self, endpoint: ServiceEndpoint):
        """检查单个端点的健康状态"""
        try:
            health_url = f"http://{endpoint.address}:{endpoint.port}/health"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(health_url) as response:
                if response.status == 200:
                        endpoint.health_status = "passing"
                else:
                        endpoint.health_status = "warning"
            
        except Exception as e:
            endpoint.health_status = "critical"
            logger.debug(f"Health check failed for {endpoint.service_id}: {e}")
    
    async def route_request(
        self, 
        service_name: str, 
        path: str, 
        method: str = "GET",
        headers: Optional[Dict] = None,
        data: Optional[bytes] = None,
        params: Optional[Dict] = None
    ) -> aiohttp.ClientResponse:
        """路由请求到服务"""
        
        endpoint_url = await self.get_service_endpoint(service_name)
        full_url = f"{endpoint_url}{path}"
        
        # 添加追踪头
        if headers is None:
            headers = {}
        headers.update({
            "X-Request-ID": f"req_{int(time.time() * 1000)}",
            "X-Forwarded-For": "api-gateway",
            "X-Service-Name": service_name
        })
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                        method=method,
                url=full_url,
                        headers=headers,
                data=data,
                params=params,
                timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                return response
    
    def get_service_stats(self, service_name: str) -> Dict:
        """获取服务统计信息"""
        endpoints = self.service_cache.get(service_name, [])
        
        total_endpoints = len(endpoints)
        healthy_endpoints = len([ep for ep in endpoints if ep.health_status == "passing"])
        total_connections = sum(ep.connections for ep in endpoints)
        
        return {
            "service_name": service_name,
            "total_endpoints": total_endpoints,
            "healthy_endpoints": healthy_endpoints,
            "total_connections": total_connections,
            "endpoints": [
                {
                    "service_id": ep.service_id,
                    "address": f"{ep.address}:{ep.port}",
                    "health_status": ep.health_status,
                    "connections": ep.connections,
                    "weight": ep.weight,
                    "last_used": ep.last_used
                }
                for ep in endpoints
            ]
        }
    
    def reset_connections(self, service_name: Optional[str] = None):
        """重置连接计数"""
        if service_name:
            endpoints = self.service_cache.get(service_name, [])
            for endpoint in endpoints:
                endpoint.connections = 0
        else:
            for endpoints in self.service_cache.values():
                for endpoint in endpoints:
                    endpoint.connections = 0
        
        logger.info(f"Reset connections for {service_name or 'all services'}")

# 全局路由器实例
_router_instance = None

def get_router(consul_client: ConsulServiceRegistry) -> DynamicRouter:
    """获取路由器单例"""
    global _router_instance
    if _router_instance is None:
        _router_instance = DynamicRouter(consul_client)
    return _router_instance

# 使用示例
    async def main():
    """示例用法"""
    from ...common.service_registry.consul_client import ConsulServiceRegistry
    
    # 创建Consul客户端和路由器
    consul_client = ConsulServiceRegistry()
    router = DynamicRouter(consul_client)
    
    await router.start()
    
    try:
        # 获取服务端点
        endpoint = await router.get_service_endpoint(
            "xiaoai-service", 
            LoadBalanceStrategy.ROUND_ROBIN
        )
        print(f"Selected endpoint: {endpoint}")
        
        # 路由请求
        response = await router.route_request(
            service_name="xiaoai-service",
            path="/api/v1/diagnose",
            method="POST",
            headers={"Content-Type": "application/json"},
            data=b'{"symptoms": ["headache", "fever"]}'
        )
        
        print(f"Response status: {response.status}")
        
        # 获取服务统计
        stats = router.get_service_stats("xiaoai-service")
        print(f"Service stats: {stats}")
        
    except ServiceNotAvailableError as e:
        print(f"Service error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        await router.stop()

if __name__ == "__main__":
    asyncio.run(main()) 