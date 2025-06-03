#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版API网关服务
集成断路器、限流、缓存、智能路由等优化组件
"""

import asyncio
import logging
import time
import hashlib
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import aiohttp

# 导入通用组件
from services.common.governance.circuit_breaker import (
    CircuitBreaker, CircuitBreakerConfig, get_circuit_breaker
)
from services.common.governance.rate_limiter import (
    RateLimitConfig, get_rate_limiter, rate_limit
)
from services.common.observability.tracing import (
    get_tracer, trace, SpanKind
)

logger = logging.getLogger(__name__)

class RouteType(Enum):
    """路由类型"""
    REST = "rest"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    GRAPHQL = "graphql"

class LoadBalanceStrategy(Enum):
    """负载均衡策略"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"
    IP_HASH = "ip_hash"
    RANDOM = "random"

@dataclass
class ServiceEndpoint:
    """服务端点"""
    service_name: str
    host: str
    port: int
    weight: int = 1
    health_check_url: str = "/health"
    protocol: str = "http"
    
@dataclass
class RouteConfig:
    """路由配置"""
    path_pattern: str
    service_name: str
    route_type: RouteType
    methods: List[str]
    timeout: float = 30.0
    retry_count: int = 3
    cache_ttl: int = 0  # 0表示不缓存
    rate_limit: Optional[int] = None  # 每分钟请求数限制
    auth_required: bool = True
    
@dataclass
class GatewayRequest:
    """网关请求"""
    request_id: str
    method: str
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    body: Optional[Any]
    client_ip: str
    user_id: Optional[str] = None
    
@dataclass
class GatewayResponse:
    """网关响应"""
    status_code: int
    headers: Dict[str, str]
    body: Any
    processing_time: float
    cache_hit: bool = False
    
class EnhancedGatewayService:
    """增强版API网关服务"""
    
    def __init__(self):
        self.service_name = "api-gateway"
        self.tracer = get_tracer(self.service_name)
        
        # 服务注册表
        self.service_registry: Dict[str, List[ServiceEndpoint]] = {}
        
        # 路由表
        self.route_table: List[RouteConfig] = []
        
        # 负载均衡器
        self.load_balancers: Dict[str, Any] = {}
        
        # 初始化断路器配置
        self._init_circuit_breakers()
        
        # 初始化限流器配置
        self._init_rate_limiters()
        
        # 缓存
        self.response_cache = {}
        self.cache_ttl = 300  # 默认5分钟缓存
        
        # HTTP会话池
        self.http_sessions: Dict[str, aiohttp.ClientSession] = {}
        
        # WebSocket连接池
        self.websocket_connections = {}
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'average_response_time': 0.0,
            'active_connections': 0,
            'circuit_breaker_trips': 0
        }
        
        # 初始化路由和服务
        self._init_routes()
        self._init_services()
        
        logger.info("增强版API网关服务初始化完成")
    
    def _init_circuit_breakers(self):
        """初始化断路器配置"""
        self.circuit_breaker_configs = {
            'default': CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60.0,
                timeout=30.0
            ),
            'auth_service': CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30.0,
                timeout=10.0
            ),
            'health_service': CircuitBreakerConfig(
                failure_threshold=10,
                recovery_timeout=120.0,
                timeout=60.0
            )
        }
    
    def _init_rate_limiters(self):
        """初始化限流器配置"""
        self.rate_limit_configs = {
            'global': RateLimitConfig(rate=1000.0, burst=2000),
            'per_user': RateLimitConfig(rate=100.0, burst=200),
            'per_ip': RateLimitConfig(rate=200.0, burst=400),
            'auth_endpoints': RateLimitConfig(rate=10.0, burst=20),
            'health_endpoints': RateLimitConfig(rate=500.0, burst=1000)
        }
    
    def _init_routes(self):
        """初始化路由配置"""
        # 认证服务路由
        self.route_table.extend([
            RouteConfig(
                path_pattern="/api/v1/auth/login",
                service_name="auth-service",
                route_type=RouteType.REST,
                methods=["POST"],
                timeout=10.0,
                retry_count=1,
                cache_ttl=0,
                rate_limit=10,
                auth_required=False
            ),
            RouteConfig(
                path_pattern="/api/v1/auth/logout",
                service_name="auth-service",
                route_type=RouteType.REST,
                methods=["POST"],
                timeout=5.0,
                retry_count=1,
                cache_ttl=0,
                auth_required=True
            ),
        ])
        
        # 健康数据服务路由
        self.route_table.extend([
            RouteConfig(
                path_pattern="/api/v1/health/data",
                service_name="health-data-service",
                route_type=RouteType.REST,
                methods=["GET", "POST"],
                timeout=30.0,
                retry_count=3,
                cache_ttl=60,
                rate_limit=100,
                auth_required=True
            ),
        ])
        
        # 智能体服务路由
        self.route_table.extend([
            RouteConfig(
                path_pattern="/api/v1/agents/xiaoai/*",
                service_name="xiaoai-service",
                route_type=RouteType.REST,
                methods=["GET", "POST"],
                timeout=60.0,
                retry_count=2,
                cache_ttl=300,
                auth_required=True
            ),
            RouteConfig(
                path_pattern="/api/v1/agents/xiaoke/*",
                service_name="xiaoke-service",
                route_type=RouteType.REST,
                methods=["GET", "POST"],
                timeout=45.0,
                retry_count=2,
                cache_ttl=600,
                auth_required=True
            ),
        ])
    
    def _init_services(self):
        """初始化服务注册表"""
        # 认证服务
        self.service_registry["auth-service"] = [
            ServiceEndpoint("auth-service", "auth-service-1", 8080, weight=1),
            ServiceEndpoint("auth-service", "auth-service-2", 8080, weight=1),
        ]
        
        # 健康数据服务
        self.service_registry["health-data-service"] = [
            ServiceEndpoint("health-data-service", "health-service-1", 8081, weight=2),
            ServiceEndpoint("health-data-service", "health-service-2", 8081, weight=1),
        ]
        
        # 智能体服务
        self.service_registry["xiaoai-service"] = [
            ServiceEndpoint("xiaoai-service", "xiaoai-service", 8000, weight=1),
        ]
        self.service_registry["xiaoke-service"] = [
            ServiceEndpoint("xiaoke-service", "xiaoke-service", 8001, weight=1),
        ]
    
    @trace(service_name="api-gateway", kind=SpanKind.SERVER)
    async def handle_request(self, request: GatewayRequest) -> GatewayResponse:
        """
        处理网关请求
        
        Args:
            request: 网关请求
            
        Returns:
            GatewayResponse: 网关响应
        """
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        try:
            # 1. 路由匹配
            route = await self._match_route(request)
            if not route:
                return GatewayResponse(
                    status_code=404,
                    headers={"Content-Type": "application/json"},
                    body={"error": "Route not found"},
                    processing_time=time.time() - start_time
                )
            
            # 2. 认证检查
            if route.auth_required and not request.user_id:
                auth_result = await self._authenticate(request)
                if not auth_result['authenticated']:
                    return GatewayResponse(
                        status_code=401,
                        headers={"Content-Type": "application/json"},
                        body={"error": "Unauthorized"},
                        processing_time=time.time() - start_time
                    )
                request.user_id = auth_result['user_id']
            
            # 3. 限流检查
            if not await self._check_rate_limit(request, route):
                return GatewayResponse(
                    status_code=429,
                    headers={"Content-Type": "application/json"},
                    body={"error": "Rate limit exceeded"},
                    processing_time=time.time() - start_time
                )
            
            # 4. 缓存检查
            if route.cache_ttl > 0 and request.method == "GET":
                cached_response = await self._get_cached_response(request, route)
                if cached_response:
                    self.stats['cache_hits'] += 1
                    cached_response.cache_hit = True
                    return cached_response
            
            self.stats['cache_misses'] += 1
            
            # 5. 负载均衡选择后端
            endpoint = await self._select_endpoint(route.service_name)
            if not endpoint:
                return GatewayResponse(
                    status_code=503,
                    headers={"Content-Type": "application/json"},
                    body={"error": "Service unavailable"},
                    processing_time=time.time() - start_time
                )
            
            # 6. 转发请求
            response = await self._forward_request(request, route, endpoint)
            
            # 7. 缓存响应
            if route.cache_ttl > 0 and request.method == "GET" and response.status_code == 200:
                await self._cache_response(request, route, response)
            
            # 更新统计
            self.stats['successful_requests'] += 1
            self._update_average_response_time(response.processing_time)
            
            return response
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"网关请求处理失败: {e}")
            return GatewayResponse(
                status_code=500,
                headers={"Content-Type": "application/json"},
                body={"error": "Internal server error"},
                processing_time=time.time() - start_time
            )
    
    async def _match_route(self, request: GatewayRequest) -> Optional[RouteConfig]:
        """匹配路由"""
        for route in self.route_table:
            if self._path_matches(request.path, route.path_pattern):
                if request.method in route.methods:
                    return route
        return None
    
    def _path_matches(self, path: str, pattern: str) -> bool:
        """路径匹配"""
        if pattern.endswith("/*"):
            prefix = pattern[:-2]
            return path.startswith(prefix)
        return path == pattern
    
    async def _authenticate(self, request: GatewayRequest) -> Dict[str, Any]:
        """认证请求"""
        # 使用断路器保护认证服务
        breaker = await get_circuit_breaker(
            f"{self.service_name}_auth_service",
            self.circuit_breaker_configs['auth_service']
        )
        
        try:
            async with breaker.protect():
                # 模拟认证调用
                auth_token = request.headers.get('Authorization', '').replace('Bearer ', '')
                if auth_token:
                    # 验证JWT token
                    await asyncio.sleep(0.01)  # 模拟验证延迟
                    return {
                        'authenticated': True,
                        'user_id': f"user_{hash(auth_token) % 10000}"
                    }
                return {'authenticated': False}
        except Exception as e:
            logger.error(f"认证失败: {e}")
            return {'authenticated': False}
    
    async def _check_rate_limit(self, request: GatewayRequest, route: RouteConfig) -> bool:
        """检查限流"""
        # 全局限流
        global_limiter = await get_rate_limiter(
            f"{self.service_name}_global",
            config=self.rate_limit_configs['global']
        )
        if not await global_limiter.try_acquire():
            return False
        
        # 用户级限流
        if request.user_id:
            user_limiter = await get_rate_limiter(
                f"{self.service_name}_user_{request.user_id}",
                config=self.rate_limit_configs['per_user']
            )
            if not await user_limiter.try_acquire():
                return False
        
        # IP级限流
        ip_limiter = await get_rate_limiter(
            f"{self.service_name}_ip_{request.client_ip}",
            config=self.rate_limit_configs['per_ip']
        )
        if not await ip_limiter.try_acquire():
            return False
        
        # 路由级限流
        if route.rate_limit:
            route_limiter = await get_rate_limiter(
                f"{self.service_name}_route_{route.path_pattern}",
                config=RateLimitConfig(rate=route.rate_limit/60.0, burst=route.rate_limit)
            )
            if not await route_limiter.try_acquire():
                return False
        
        return True
    
    async def _get_cached_response(self, request: GatewayRequest, route: RouteConfig) -> Optional[GatewayResponse]:
        """获取缓存的响应"""
        cache_key = self._generate_cache_key(request, route)
        
        if cache_key in self.response_cache:
            cached_data = self.response_cache[cache_key]
            if time.time() - cached_data['timestamp'] < route.cache_ttl:
                return cached_data['response']
            else:
                del self.response_cache[cache_key]
        
        return None
    
    async def _select_endpoint(self, service_name: str) -> Optional[ServiceEndpoint]:
        """选择服务端点（负载均衡）"""
        endpoints = self.service_registry.get(service_name, [])
        if not endpoints:
            return None
        
        # 简单的轮询负载均衡
        if service_name not in self.load_balancers:
            self.load_balancers[service_name] = {'index': 0}
        
        lb = self.load_balancers[service_name]
        endpoint = endpoints[lb['index'] % len(endpoints)]
        lb['index'] += 1
        
        # 健康检查
        if not await self._is_endpoint_healthy(endpoint):
            # 尝试下一个端点
            for _ in range(len(endpoints)):
                lb['index'] += 1
                endpoint = endpoints[lb['index'] % len(endpoints)]
                if await self._is_endpoint_healthy(endpoint):
                    break
            else:
                return None
        
        return endpoint
    
    async def _is_endpoint_healthy(self, endpoint: ServiceEndpoint) -> bool:
        """检查端点健康状态"""
        # 简化的健康检查
        return True  # 实际应该进行真实的健康检查
    
    @trace(operation_name="forward_request")
    async def _forward_request(self, request: GatewayRequest, route: RouteConfig, endpoint: ServiceEndpoint) -> GatewayResponse:
        """转发请求到后端服务"""
        # 使用断路器保护后端服务
        breaker_config = self.circuit_breaker_configs.get(route.service_name, self.circuit_breaker_configs['default'])
        breaker = await get_circuit_breaker(
            f"{self.service_name}_{route.service_name}",
            breaker_config
        )
        
        try:
            async with breaker.protect():
                # 获取或创建HTTP会话
                session = await self._get_http_session(route.service_name)
                
                # 构建后端URL
                backend_url = f"{endpoint.protocol}://{endpoint.host}:{endpoint.port}{request.path}"
                
                # 准备请求头
                headers = dict(request.headers)
                headers['X-Forwarded-For'] = request.client_ip
                headers['X-Request-ID'] = request.request_id
                if request.user_id:
                    headers['X-User-ID'] = request.user_id
                
                # 发送请求
                start_time = time.time()
                
                async with session.request(
                    method=request.method,
                    url=backend_url,
                    headers=headers,
                    params=request.query_params,
                    json=request.body if request.body else None,
                    timeout=aiohttp.ClientTimeout(total=route.timeout)
                ) as response:
                    # 读取响应
                    response_body = await response.json() if response.content_type == 'application/json' else await response.text()
                    
                    return GatewayResponse(
                        status_code=response.status,
                        headers=dict(response.headers),
                        body=response_body,
                        processing_time=time.time() - start_time
                    )
                    
        except asyncio.TimeoutError:
            logger.error(f"请求超时: {route.service_name}")
            return GatewayResponse(
                status_code=504,
                headers={"Content-Type": "application/json"},
                body={"error": "Gateway timeout"},
                processing_time=route.timeout
            )
        except Exception as e:
            logger.error(f"转发请求失败: {e}")
            self.stats['circuit_breaker_trips'] += 1
            return GatewayResponse(
                status_code=502,
                headers={"Content-Type": "application/json"},
                body={"error": "Bad gateway"},
                processing_time=time.time() - start_time
            )
    
    async def _get_http_session(self, service_name: str) -> aiohttp.ClientSession:
        """获取HTTP会话"""
        if service_name not in self.http_sessions:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=30,
                ttl_dns_cache=300
            )
            self.http_sessions[service_name] = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=60)
            )
        return self.http_sessions[service_name]
    
    async def _cache_response(self, request: GatewayRequest, route: RouteConfig, response: GatewayResponse):
        """缓存响应"""
        cache_key = self._generate_cache_key(request, route)
        self.response_cache[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }
        
        # 简单的缓存清理策略
        if len(self.response_cache) > 10000:
            # 删除最老的缓存项
            oldest_key = min(
                self.response_cache.keys(),
                key=lambda k: self.response_cache[k]['timestamp']
            )
            del self.response_cache[oldest_key]
    
    def _generate_cache_key(self, request: GatewayRequest, route: RouteConfig) -> str:
        """生成缓存键"""
        # 基于路径、查询参数和用户ID生成缓存键
        key_parts = [
            request.method,
            request.path,
            json.dumps(request.query_params, sort_keys=True),
            request.user_id or 'anonymous'
        ]
        key_string = '|'.join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _update_average_response_time(self, response_time: float):
        """更新平均响应时间"""
        total_requests = self.stats['successful_requests']
        if total_requests == 1:
            self.stats['average_response_time'] = response_time
        else:
            current_avg = self.stats['average_response_time']
            self.stats['average_response_time'] = (
                (current_avg * (total_requests - 1) + response_time) / total_requests
            )
    
    async def handle_websocket(self, request: GatewayRequest, ws_handler: Callable):
        """处理WebSocket连接"""
        # WebSocket连接的特殊处理
        self.stats['active_connections'] += 1
        try:
            # 路由匹配
            route = await self._match_route(request)
            if not route or route.route_type != RouteType.WEBSOCKET:
                await ws_handler.close(code=404, reason="Route not found")
                return
            
            # 选择后端
            endpoint = await self._select_endpoint(route.service_name)
            if not endpoint:
                await ws_handler.close(code=503, reason="Service unavailable")
                return
            
            # 建立到后端的WebSocket连接
            backend_url = f"ws://{endpoint.host}:{endpoint.port}{request.path}"
            
            # 双向代理WebSocket消息
            # 这里需要实现WebSocket消息的双向转发逻辑
            
        finally:
            self.stats['active_connections'] -= 1
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取服务健康状态"""
        return {
            'service': self.service_name,
            'status': 'healthy',
            'stats': self.stats,
            'cache_size': len(self.response_cache),
            'active_sessions': len(self.http_sessions),
            'registered_services': list(self.service_registry.keys()),
            'route_count': len(self.route_table),
            'uptime': time.time()
        }
    
    async def cleanup(self):
        """清理资源"""
        # 关闭所有HTTP会话
        for session in self.http_sessions.values():
            await session.close()
        
        # 清理缓存
        self.response_cache.clear()
        
        # 关闭WebSocket连接
        for conn in self.websocket_connections.values():
            await conn.close()
        
        logger.info("API网关服务清理完成")

# 全局服务实例
_gateway_service = None

async def get_gateway_service() -> EnhancedGatewayService:
    """获取网关服务实例"""
    global _gateway_service
    if _gateway_service is None:
        _gateway_service = EnhancedGatewayService()
    return _gateway_service 