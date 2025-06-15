#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
服务间通信客户端 - 支持负载均衡、熔断和重试机制
"""

import asyncio
import logging
import time
import random
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

import aiohttp
import json
from urllib.parse import urljoin

from pkg.utils.cache import CacheManager
from pkg.utils.metrics import record_service_call, errors_total

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"      # 正常状态
    OPEN = "open"          # 熔断状态
    HALF_OPEN = "half_open"  # 半开状态

@dataclass
class ServiceEndpoint:
    """服务端点配置"""
    host: str
    port: int
    scheme: str = "http"
    weight: int = 1
    health_check_path: str = "/health"
    
    @property
    def base_url(self) -> str:
        return f"{self.scheme}://{self.host}:{self.port}"

@dataclass
class CircuitBreakerConfig:
    """熔断器配置"""
    failure_threshold: int = 5          # 失败阈值
    recovery_timeout: int = 60          # 恢复超时（秒）
    success_threshold: int = 3          # 半开状态成功阈值
    timeout: float = 30.0               # 请求超时
    
@dataclass
class RetryConfig:
    """重试配置"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True

@dataclass
class CircuitBreakerState:
    """熔断器状态"""
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    next_attempt_time: Optional[float] = None

class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, endpoints: List[ServiceEndpoint]):
        self.endpoints = endpoints
        self.current_index = 0
        self.weights = [ep.weight for ep in endpoints]
        self.total_weight = sum(self.weights)
    
    def get_endpoint(self, strategy: str = "round_robin") -> ServiceEndpoint:
        """获取端点"""
        if strategy == "round_robin":
            return self._round_robin()
        elif strategy == "weighted_round_robin":
            return self._weighted_round_robin()
        elif strategy == "random":
            return self._random()
        elif strategy == "weighted_random":
            return self._weighted_random()
        else:
            return self._round_robin()
    
    def _round_robin(self) -> ServiceEndpoint:
        """轮询"""
        endpoint = self.endpoints[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.endpoints)
        return endpoint
    
    def _weighted_round_robin(self) -> ServiceEndpoint:
        """加权轮询"""
        # 简化实现，实际应该使用更复杂的加权轮询算法
        return self._weighted_random()
    
    def _random(self) -> ServiceEndpoint:
        """随机"""
        return random.choice(self.endpoints)
    
    def _weighted_random(self) -> ServiceEndpoint:
        """加权随机"""
        if self.total_weight == 0:
            return random.choice(self.endpoints)
        
        r = random.uniform(0, self.total_weight)
        current_weight = 0
        
        for i, weight in enumerate(self.weights):
            current_weight += weight
            if r <= current_weight:
                return self.endpoints[i]
        
        return self.endpoints[-1]

class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState()
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """执行调用"""
        async with self._lock:
            # 检查熔断器状态
            if self.state.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state.state = CircuitState.HALF_OPEN
                    self.state.success_count = 0
                else:
                    raise Exception("Circuit breaker is OPEN")
        
        try:
            # 执行调用
            result = await func(*args, **kwargs)
            
            # 成功处理
            async with self._lock:
                await self._on_success()
            
            return result
            
        except Exception as e:
            # 失败处理
            async with self._lock:
                await self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """是否应该尝试重置"""
        if self.state.next_attempt_time is None:
            return True
        return time.time() >= self.state.next_attempt_time
    
    async def _on_success(self):
        """成功回调"""
        if self.state.state == CircuitState.HALF_OPEN:
            self.state.success_count += 1
            if self.state.success_count >= self.config.success_threshold:
                self.state.state = CircuitState.CLOSED
                self.state.failure_count = 0
                self.state.success_count = 0
        elif self.state.state == CircuitState.CLOSED:
            self.state.failure_count = 0
    
    async def _on_failure(self):
        """失败回调"""
        self.state.failure_count += 1
        self.state.last_failure_time = time.time()
        
        if self.state.failure_count >= self.config.failure_threshold:
            self.state.state = CircuitState.OPEN
            self.state.next_attempt_time = time.time() + self.config.recovery_timeout

class ServiceClient:
    """服务客户端"""
    
    def __init__(
        self,
        service_name: str,
        endpoints: List[ServiceEndpoint],
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
        retry_config: Optional[RetryConfig] = None,
        load_balance_strategy: str = "round_robin",
        cache_manager: Optional[CacheManager] = None
    ):
        self.service_name = service_name
        self.load_balancer = LoadBalancer(endpoints)
        self.circuit_breaker_config = circuit_breaker_config or CircuitBreakerConfig()
        self.retry_config = retry_config or RetryConfig()
        self.load_balance_strategy = load_balance_strategy
        self.cache_manager = cache_manager or CacheManager()
        
        # 为每个端点创建熔断器
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        for endpoint in endpoints:
            key = f"{endpoint.host}:{endpoint.port}"
            self.circuit_breakers[key] = CircuitBreaker(self.circuit_breaker_config)
        
        # HTTP会话
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.info(f"服务客户端初始化完成: {service_name}")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
    
    async def _ensure_session(self):
        """确保HTTP会话存在"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.circuit_breaker_config.timeout)
            connector = aiohttp.TCPConnector(
                limit=100,  # 连接池大小
                limit_per_host=20,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={"User-Agent": f"ServiceClient/{self.service_name}"}
            )
    
    async def close(self):
        """关闭客户端"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cache_ttl: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """GET请求"""
        return await self._request("GET", path, params=params, headers=headers, cache_ttl=cache_ttl, **kwargs)
    
    async def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """POST请求"""
        return await self._request("POST", path, data=data, json=json_data, headers=headers, **kwargs)
    
    async def put(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """PUT请求"""
        return await self._request("PUT", path, data=data, json=json_data, headers=headers, **kwargs)
    
    async def delete(
        self,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """DELETE请求"""
        return await self._request("DELETE", path, headers=headers, **kwargs)
    
    async def _request(
        self,
        method: str,
        path: str,
        cache_ttl: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """执行HTTP请求"""
        await self._ensure_session()
        
        # 检查缓存（仅对GET请求）
        if method == "GET" and cache_ttl:
            cache_key = self._get_cache_key(method, path, kwargs.get("params"))
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_result
        
        # 重试逻辑
        last_exception = None
        for attempt in range(self.retry_config.max_attempts):
            try:
                # 获取端点
                endpoint = self.load_balancer.get_endpoint(self.load_balance_strategy)
                endpoint_key = f"{endpoint.host}:{endpoint.port}"
                circuit_breaker = self.circuit_breakers[endpoint_key]
                
                # 通过熔断器执行请求
                result = await circuit_breaker.call(
                    self._execute_request,
                    endpoint,
                    method,
                    path,
                    **kwargs
                )
                
                # 缓存结果（仅对GET请求）
                if method == "GET" and cache_ttl:
                    cache_key = self._get_cache_key(method, path, kwargs.get("params"))
                    await self.cache_manager.set(cache_key, result, ttl=cache_ttl)
                
                # 记录成功指标
                record_service_call(
                    service=self.service_name,
                    endpoint=path,
                    method=method,
                    status="success",
                    duration=0  # 实际应该记录真实耗时
                )
                
                return result
                
            except Exception as e:
                last_exception = e
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{self.retry_config.max_attempts}): {str(e)}")
                
                # 记录失败指标
                record_service_call(
                    service=self.service_name,
                    endpoint=path,
                    method=method,
                    status="error",
                    duration=0
                )
                
                errors_total.labels(
                    component="service_client",
                    error_type=type(e).__name__,
                    severity="warning"
                ).inc()
                
                # 如果不是最后一次尝试，等待后重试
                if attempt < self.retry_config.max_attempts - 1:
                    delay = self._calculate_retry_delay(attempt)
                    await asyncio.sleep(delay)
        
        # 所有重试都失败了
        logger.error(f"所有重试都失败了: {str(last_exception)}")
        raise last_exception
    
    async def _execute_request(
        self,
        endpoint: ServiceEndpoint,
        method: str,
        path: str,
        **kwargs
    ) -> Dict[str, Any]:
        """执行单次HTTP请求"""
        url = urljoin(endpoint.base_url, path)
        
        logger.debug(f"执行请求: {method} {url}")
        
        async with self.session.request(method, url, **kwargs) as response:
            # 检查HTTP状态码
            if response.status >= 400:
                error_text = await response.text()
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=error_text
                )
            
            # 解析响应
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return await response.json()
            else:
                text = await response.text()
                return {"data": text}
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        """计算重试延迟"""
        delay = self.retry_config.base_delay * (
            self.retry_config.exponential_base ** attempt
        )
        delay = min(delay, self.retry_config.max_delay)
        
        if self.retry_config.jitter:
            delay *= (0.5 + random.random() * 0.5)  # 添加50%的抖动
        
        return delay
    
    def _get_cache_key(self, method: str, path: str, params: Optional[Dict[str, Any]]) -> str:
        """生成缓存键"""
        key_parts = [self.service_name, method, path]
        
        if params:
            # 对参数进行排序以确保一致性
            sorted_params = sorted(params.items())
            params_str = "&".join(f"{k}={v}" for k, v in sorted_params)
            key_parts.append(params_str)
        
        return ":".join(key_parts)
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        results = {}
        
        for endpoint in self.load_balancer.endpoints:
            endpoint_key = f"{endpoint.host}:{endpoint.port}"
            try:
                start_time = time.time()
                result = await self._execute_request(
                    endpoint,
                    "GET",
                    endpoint.health_check_path
                )
                duration = time.time() - start_time
                
                results[endpoint_key] = {
                    "status": "healthy",
                    "response_time": duration,
                    "details": result
                }
                
            except Exception as e:
                results[endpoint_key] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        return results
    
    async def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """获取熔断器状态"""
        status = {}
        
        for endpoint_key, circuit_breaker in self.circuit_breakers.items():
            status[endpoint_key] = {
                "state": circuit_breaker.state.state.value,
                "failure_count": circuit_breaker.state.failure_count,
                "success_count": circuit_breaker.state.success_count,
                "last_failure_time": circuit_breaker.state.last_failure_time,
                "next_attempt_time": circuit_breaker.state.next_attempt_time
            }
        
        return status

class ServiceRegistry:
    """服务注册中心"""
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.cache_manager = cache_manager or CacheManager()
        self.services: Dict[str, List[ServiceEndpoint]] = {}
        
    async def register_service(
        self,
        service_name: str,
        endpoints: List[ServiceEndpoint]
    ):
        """注册服务"""
        self.services[service_name] = endpoints
        
        # 缓存服务信息
        await self.cache_manager.set(
            f"service_registry:{service_name}",
            [
                {
                    "host": ep.host,
                    "port": ep.port,
                    "scheme": ep.scheme,
                    "weight": ep.weight,
                    "health_check_path": ep.health_check_path
                }
                for ep in endpoints
            ],
            ttl=3600
        )
        
        logger.info(f"服务已注册: {service_name} ({len(endpoints)} 个端点)")
    
    async def get_service_endpoints(self, service_name: str) -> List[ServiceEndpoint]:
        """获取服务端点"""
        # 先从内存获取
        if service_name in self.services:
            return self.services[service_name]
        
        # 从缓存获取
        cached_endpoints = await self.cache_manager.get(f"service_registry:{service_name}")
        if cached_endpoints:
            endpoints = [
                ServiceEndpoint(**ep_data) for ep_data in cached_endpoints
            ]
            self.services[service_name] = endpoints
            return endpoints
        
        raise ValueError(f"服务未找到: {service_name}")
    
    async def create_client(
        self,
        service_name: str,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
        retry_config: Optional[RetryConfig] = None,
        load_balance_strategy: str = "round_robin"
    ) -> ServiceClient:
        """创建服务客户端"""
        endpoints = await self.get_service_endpoints(service_name)
        
        return ServiceClient(
            service_name=service_name,
            endpoints=endpoints,
            circuit_breaker_config=circuit_breaker_config,
            retry_config=retry_config,
            load_balance_strategy=load_balance_strategy,
            cache_manager=self.cache_manager
        )

# 全局服务注册中心
_service_registry: Optional[ServiceRegistry] = None

def get_service_registry() -> ServiceRegistry:
    """获取全局服务注册中心"""
    global _service_registry
    if _service_registry is None:
        _service_registry = ServiceRegistry()
    return _service_registry

async def register_default_services():
    """注册默认服务"""
    registry = get_service_registry()
    
    # 注册索克生活平台的其他服务
    services_config = {
        "auth-service": [
            ServiceEndpoint("localhost", 8001, "http", 1),
            ServiceEndpoint("localhost", 8002, "http", 1),
        ],
        "user-service": [
            ServiceEndpoint("localhost", 8003, "http", 1),
        ],
        "health-data-service": [
            ServiceEndpoint("localhost", 8004, "http", 1),
        ],
        "rag-service": [
            ServiceEndpoint("localhost", 8005, "http", 1),
        ],
        "api-gateway": [
            ServiceEndpoint("localhost", 8000, "http", 1),
        ]
    }
    
    for service_name, endpoints in services_config.items():
        await registry.register_service(service_name, endpoints)
    
    logger.info("默认服务注册完成") 