"""
API网关动态路由服务
支持基于服务发现的动态路由、负载均衡、熔断器、限流等功能
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
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    CONSISTENT_HASH = "consistent_hash"

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
    """服务端点"""
    instance: ServiceInstance
    health_status: HealthStatus = HealthStatus.UNKNOWN
    last_health_check: datetime = field(default_factory=datetime.now)
    connection_count: int = 0
    response_time_avg: float = 0.0
    error_count: int = 0
    success_count: int = 0

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

class DynamicRouter:
    """动态路由器"""
    
    def __init__(self):
        self.consul_client = get_consul_client()
        self.config_center = get_config_center()
        self.tracing = get_tracing_manager()
        
        # 路由规则
        self.route_rules: List[RouteRule] = []
        self.service_endpoints: Dict[str, List[ServiceEndpoint]] = {}
        
        # 负载均衡状态
        self.lb_counters: Dict[str, int] = {}
        self.consistent_hash_ring: Dict[str, List[str]] = {}
        
        # 熔断器和限流器
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.rate_limiters: Dict[str, RateLimiter] = {}
        
        # HTTP客户端
        self.http_session = None
        
        # 配置
        self.config = ServiceConfig("api-gateway", self.config_center)
        
        # 初始化
        self._initialize()
    
    def _initialize(self):
        """初始化路由器"""
        # 加载路由规则
        self._load_route_rules()
        
        # 启动服务发现监听
        self._start_service_discovery()
        
        # 启动健康检查
        asyncio.create_task(self._health_check_loop())
        
        # 启动配置监听
        self._start_config_watching()
        
        logger.info("Dynamic router initialized")
    
    def _load_route_rules(self):
        """加载路由规则"""
        try:
            rules_config = self.config.get("route_rules", [])
            
            self.route_rules = []
            for rule_data in rules_config:
                rule = RouteRule(**rule_data)
                self.route_rules.append(rule)
            
            # 按优先级排序
            self.route_rules.sort(key=lambda r: r.priority, reverse=True)
            
            logger.info(f"Loaded {len(self.route_rules)} route rules")
            
        except Exception as e:
            logger.error(f"Failed to load route rules: {e}")
    
    def _start_service_discovery(self):
        """启动服务发现"""
        # 获取所有服务
        services = self.consul_client.get_all_services()
        
        for service_name, instances in services.items():
            self.service_endpoints[service_name] = [
                ServiceEndpoint(instance=instance)
                for instance in instances
            ]
            
            # 监听服务变化
            self.consul_client.watch_service(
                service_name, 
                lambda instances, svc=service_name: self._on_service_change(svc, instances)
            )
        
        logger.info(f"Started service discovery for {len(services)} services")
    
    def _on_service_change(self, service_name: str, instances: List[ServiceInstance]):
        """服务变化回调"""
        self.service_endpoints[service_name] = [
            ServiceEndpoint(instance=instance)
            for instance in instances
        ]
        
        # 重建一致性哈希环
        self._rebuild_consistent_hash_ring(service_name)
        
        logger.info(f"Service {service_name} updated: {len(instances)} instances")
    
    def _start_config_watching(self):
        """启动配置监听"""
        def on_route_rules_change(key, value):
            logger.info("Route rules configuration changed, reloading...")
            self._load_route_rules()
        
        self.config.watch("route_rules", on_route_rules_change)
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(30)  # 每30秒检查一次
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(5)
    
    async def _perform_health_checks(self):
        """执行健康检查"""
        if not self.http_session:
            self.http_session = aiohttp.ClientSession()
        
        tasks = []
        for service_name, endpoints in self.service_endpoints.items():
            for endpoint in endpoints:
                task = self._check_endpoint_health(endpoint)
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_endpoint_health(self, endpoint: ServiceEndpoint):
        """检查端点健康状态"""
        try:
            health_url = f"http://{endpoint.instance.address}:{endpoint.instance.port}/health"
            
            async with self.http_session.get(health_url, timeout=5) as response:
                if response.status == 200:
                    endpoint.health_status = HealthStatus.HEALTHY
                else:
                    endpoint.health_status = HealthStatus.UNHEALTHY
                    
        except Exception:
            endpoint.health_status = HealthStatus.UNHEALTHY
        
        endpoint.last_health_check = datetime.now()
    
    def _rebuild_consistent_hash_ring(self, service_name: str):
        """重建一致性哈希环"""
        if service_name not in self.service_endpoints:
            return
        
        ring = []
        for endpoint in self.service_endpoints[service_name]:
            if endpoint.health_status == HealthStatus.HEALTHY:
                # 为每个端点创建多个虚拟节点
                for i in range(100):
                    virtual_node = f"{endpoint.instance.address}:{endpoint.instance.port}#{i}"
                    hash_value = hashlib.md5(virtual_node.encode()).hexdigest()
                    ring.append(hash_value)
        
        ring.sort()
        self.consistent_hash_ring[service_name] = ring
    
    @trace_function("route_request")
    async def route_request(self, path: str, method: str, headers: Dict[str, str], 
                           query_params: Dict[str, str], body: bytes = None) -> Dict[str, Any]:
        """路由请求"""
        # 查找匹配的路由规则
        route_rule = self._find_matching_route(path, method, headers, query_params)
        
        if not route_rule:
            return {
                "status": 404,
                "error": "No matching route found",
                "path": path
            }
        
        # 获取服务端点
        endpoint = await self._select_endpoint(route_rule.service_name, headers, query_params)
        
        if not endpoint:
            return {
                "status": 503,
                "error": "No healthy service instances available",
                "service": route_rule.service_name
            }
        
        # 检查熔断器
        circuit_breaker = self._get_circuit_breaker(route_rule.service_name)
        if route_rule.circuit_breaker_enabled and not circuit_breaker.can_execute():
            return {
                "status": 503,
                "error": "Circuit breaker is open",
                "service": route_rule.service_name
            }
        
        # 检查限流
        rate_limiter = self._get_rate_limiter(route_rule.service_name)
        if route_rule.rate_limit_enabled and not rate_limiter.is_allowed():
            return {
                "status": 429,
                "error": "Rate limit exceeded",
                "service": route_rule.service_name
            }
        
        # 执行请求
        try:
            result = await self._execute_request(
                endpoint, path, method, headers, query_params, body, route_rule
            )
            
            # 记录成功
            circuit_breaker.record_success()
            endpoint.success_count += 1
            
            return result
            
        except Exception as e:
            # 记录失败
            circuit_breaker.record_failure()
            endpoint.error_count += 1
            
            logger.error(f"Request failed: {e}")
            return {
                "status": 500,
                "error": str(e),
                "service": route_rule.service_name
            }
    
    def _find_matching_route(self, path: str, method: str, 
                           headers: Dict[str, str], query_params: Dict[str, str]) -> Optional[RouteRule]:
        """查找匹配的路由规则"""
        for rule in self.route_rules:
            if self._match_route_rule(rule, path, method, headers, query_params):
                return rule
        return None
    
    def _match_route_rule(self, rule: RouteRule, path: str, method: str,
                         headers: Dict[str, str], query_params: Dict[str, str]) -> bool:
        """检查路由规则是否匹配"""
        # 检查路径
        if not self._match_path_pattern(rule.path_pattern, path):
            return False
        
        # 检查方法
        if rule.method != "*" and rule.method.upper() != method.upper():
            return False
        
        # 检查头部
        for key, value in rule.headers.items():
            if headers.get(key) != value:
                return False
        
        # 检查查询参数
        for key, value in rule.query_params.items():
            if query_params.get(key) != value:
                return False
        
        return True
    
    def _match_path_pattern(self, pattern: str, path: str) -> bool:
        """匹配路径模式"""
        import re
        
        # 简单的通配符支持
        pattern = pattern.replace("*", ".*")
        pattern = f"^{pattern}$"
        
        return bool(re.match(pattern, path))
    
    async def _select_endpoint(self, service_name: str, headers: Dict[str, str], 
                             query_params: Dict[str, str]) -> Optional[ServiceEndpoint]:
        """选择服务端点"""
        if service_name not in self.service_endpoints:
            return None
        
        endpoints = [ep for ep in self.service_endpoints[service_name] 
                    if ep.health_status == HealthStatus.HEALTHY]
        
        if not endpoints:
            return None
        
        # 获取负载均衡策略
        lb_strategy = self.config.get(f"services/{service_name}/load_balance_strategy", 
                                     LoadBalanceStrategy.ROUND_ROBIN.value)
        
        if lb_strategy == LoadBalanceStrategy.ROUND_ROBIN.value:
            return self._round_robin_select(service_name, endpoints)
        elif lb_strategy == LoadBalanceStrategy.RANDOM.value:
            return random.choice(endpoints)
        elif lb_strategy == LoadBalanceStrategy.LEAST_CONNECTIONS.value:
            return min(endpoints, key=lambda ep: ep.connection_count)
        elif lb_strategy == LoadBalanceStrategy.CONSISTENT_HASH.value:
            return self._consistent_hash_select(service_name, endpoints, headers, query_params)
        else:
            return self._round_robin_select(service_name, endpoints)
    
    def _round_robin_select(self, service_name: str, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """轮询选择"""
        if service_name not in self.lb_counters:
            self.lb_counters[service_name] = 0
        
        index = self.lb_counters[service_name] % len(endpoints)
        self.lb_counters[service_name] += 1
        
        return endpoints[index]
    
    def _consistent_hash_select(self, service_name: str, endpoints: List[ServiceEndpoint],
                               headers: Dict[str, str], query_params: Dict[str, str]) -> ServiceEndpoint:
        """一致性哈希选择"""
        # 构建哈希键
        hash_key = headers.get("X-User-ID") or query_params.get("user_id") or "default"
        hash_value = hashlib.md5(hash_key.encode()).hexdigest()
        
        # 在哈希环中查找
        ring = self.consistent_hash_ring.get(service_name, [])
        if not ring:
            return random.choice(endpoints)
        
        # 找到第一个大于等于hash_value的节点
        for node_hash in ring:
            if node_hash >= hash_value:
                # 提取实际的端点地址
                node_addr = node_hash.split('#')[0]
                for endpoint in endpoints:
                    if f"{endpoint.instance.address}:{endpoint.instance.port}" == node_addr:
                        return endpoint
        
        # 如果没找到，返回第一个
        return endpoints[0]
    
    async def _execute_request(self, endpoint: ServiceEndpoint, path: str, method: str,
                              headers: Dict[str, str], query_params: Dict[str, str],
                              body: bytes, route_rule: RouteRule) -> Dict[str, Any]:
        """执行请求"""
        if not self.http_session:
            self.http_session = aiohttp.ClientSession()
        
        # 构建目标URL
        target_url = f"http://{endpoint.instance.address}:{endpoint.instance.port}{path}"
        
        # 添加追踪头
        if self.tracing:
            headers = self.tracing.inject_context(headers.copy())
        
        # 增加连接计数
        endpoint.connection_count += 1
        
        try:
            start_time = time.time()
            
            # 执行请求（带重试）
            for attempt in range(route_rule.retry_count + 1):
                try:
                    async with self.http_session.request(
                        method=method,
                        url=target_url,
                        headers=headers,
                        params=query_params,
                        data=body,
                        timeout=aiohttp.ClientTimeout(total=route_rule.timeout)
                    ) as response:
                        response_body = await response.read()
                        
                        # 更新响应时间
                        response_time = time.time() - start_time
                        endpoint.response_time_avg = (
                            endpoint.response_time_avg * 0.9 + response_time * 0.1
                        )
                        
                        return {
                            "status": response.status,
                            "headers": dict(response.headers),
                            "body": response_body,
                            "response_time": response_time
                        }
                        
                except asyncio.TimeoutError:
                    if attempt < route_rule.retry_count:
                        await asyncio.sleep(0.1 * (attempt + 1))  # 指数退避
                        continue
                    raise
                except Exception as e:
                    if attempt < route_rule.retry_count:
                        await asyncio.sleep(0.1 * (attempt + 1))
                        continue
                    raise
        
        finally:
            # 减少连接计数
            endpoint.connection_count -= 1
    
    def _get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """获取熔断器"""
        if service_name not in self.circuit_breakers:
            failure_threshold = self.config.get(
                f"services/{service_name}/circuit_breaker/failure_threshold", 5
            )
            recovery_timeout = self.config.get(
                f"services/{service_name}/circuit_breaker/recovery_timeout", 60.0
            )
            
            self.circuit_breakers[service_name] = CircuitBreaker(
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout
            )
        
        return self.circuit_breakers[service_name]
    
    def _get_rate_limiter(self, service_name: str) -> RateLimiter:
        """获取限流器"""
        if service_name not in self.rate_limiters:
            max_requests = self.config.get(
                f"services/{service_name}/rate_limit/max_requests", 100
            )
            window_size = self.config.get(
                f"services/{service_name}/rate_limit/window_size", 60.0
            )
            
            self.rate_limiters[service_name] = RateLimiter(
                max_requests=max_requests,
                window_size=window_size
            )
        
        return self.rate_limiters[service_name]
    
    def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        stats = {
            "services": {},
            "total_endpoints": 0,
            "healthy_endpoints": 0
        }
        
        for service_name, endpoints in self.service_endpoints.items():
            healthy_count = sum(1 for ep in endpoints 
                              if ep.health_status == HealthStatus.HEALTHY)
            
            service_stats = {
                "total_instances": len(endpoints),
                "healthy_instances": healthy_count,
                "circuit_breaker_state": "UNKNOWN",
                "avg_response_time": 0.0,
                "success_rate": 0.0
            }
            
            if service_name in self.circuit_breakers:
                service_stats["circuit_breaker_state"] = self.circuit_breakers[service_name].state
            
            if endpoints:
                total_success = sum(ep.success_count for ep in endpoints)
                total_error = sum(ep.error_count for ep in endpoints)
                total_requests = total_success + total_error
                
                if total_requests > 0:
                    service_stats["success_rate"] = total_success / total_requests
                
                service_stats["avg_response_time"] = sum(ep.response_time_avg for ep in endpoints) / len(endpoints)
            
            stats["services"][service_name] = service_stats
            stats["total_endpoints"] += len(endpoints)
            stats["healthy_endpoints"] += healthy_count
        
        return stats
    
    async def shutdown(self):
        """关闭路由器"""
        if self.http_session:
            await self.http_session.close()
        
        logger.info("Dynamic router shutdown")

# 全局路由器实例
_dynamic_router = None

def get_dynamic_router() -> DynamicRouter:
    """获取动态路由器单例"""
    global _dynamic_router
    if _dynamic_router is None:
        _dynamic_router = DynamicRouter()
    return _dynamic_router

# 使用示例
if __name__ == "__main__":
    async def main():
        router = get_dynamic_router()
        
        # 模拟请求
        result = await router.route_request(
            path="/api/v1/diagnosis",
            method="POST",
            headers={"Content-Type": "application/json", "X-User-ID": "user123"},
            query_params={},
            body=b'{"symptoms": ["头痛", "乏力"]}'
        )
        
        print(f"Route result: {result}")
        
        # 获取统计信息
        stats = router.get_service_stats()
        print(f"Service stats: {json.dumps(stats, indent=2)}")
        
        await router.shutdown()
    
    asyncio.run(main()) 