#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API网关和路由优化器
支持智能路由、版本管理、限流、认证和负载均衡
"""

import asyncio
import time
import json
import logging
import hashlib
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import re
from urllib.parse import urlparse, parse_qs
import aiohttp
from aiohttp import web, ClientSession
from aiohttp.web_middlewares import cors_handler
import jwt
from functools import wraps
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class RouteMethod(Enum):
    """路由方法"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class LoadBalanceStrategy(Enum):
    """负载均衡策略"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    IP_HASH = "ip_hash"
    RANDOM = "random"

@dataclass
class ServiceEndpoint:
    """服务端点"""
    id: str
    host: str
    port: int
    weight: int = 1
    health_check_url: str = "/health"
    max_connections: int = 100
    timeout: float = 30.0
    
    # 运行时状态
    active_connections: int = 0
    is_healthy: bool = True
    last_health_check: datetime = None
    response_time: float = 0.0
    
    def __post_init__(self):
        if self.last_health_check is None:
            self.last_health_check = datetime.now()
    
    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"
    
    @property
    def health_url(self) -> str:
        return f"{self.url}{self.health_check_url}"

@dataclass
class RouteConfig:
    """路由配置"""
    path: str
    methods: List[RouteMethod]
    service_name: str
    version: str = "v1"
    timeout: float = 30.0
    retries: int = 3
    
    # 认证配置
    auth_required: bool = False
    auth_scopes: List[str] = None
    
    # 限流配置
    rate_limit: Optional[int] = None  # 每分钟请求数
    burst_limit: Optional[int] = None  # 突发请求数
    
    # 缓存配置
    cache_enabled: bool = False
    cache_ttl: int = 300  # 秒
    
    # 转换配置
    request_transform: Optional[str] = None
    response_transform: Optional[str] = None
    
    def __post_init__(self):
        if self.auth_scopes is None:
            self.auth_scopes = []

@dataclass
class ServiceConfig:
    """服务配置"""
    name: str
    endpoints: List[ServiceEndpoint]
    load_balance_strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN
    health_check_interval: int = 30  # 秒
    circuit_breaker_enabled: bool = True
    circuit_breaker_threshold: int = 5  # 失败次数阈值
    circuit_breaker_timeout: int = 60  # 熔断超时时间（秒）

class RateLimiter:
    """限流器"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.prefix = "xiaoai:rate_limit:"
    
    async def is_allowed(self, key: str, limit: int, window: int = 60) -> bool:
        """检查是否允许请求"""
        current_time = int(time.time())
        window_start = current_time - window
        
        pipe = self.redis.pipeline()
        
        # 清理过期记录
        pipe.zremrangebyscore(f"{self.prefix}{key}", 0, window_start)
        
        # 获取当前窗口内的请求数
        pipe.zcard(f"{self.prefix}{key}")
        
        # 添加当前请求
        pipe.zadd(f"{self.prefix}{key}", {str(current_time): current_time})
        
        # 设置过期时间
        pipe.expire(f"{self.prefix}{key}", window)
        
        results = await pipe.execute()
        current_requests = results[1]
        
        return current_requests < limit

class AuthManager:
    """认证管理器"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_cache = {}
    
    def generate_token(self, user_id: str, scopes: List[str], 
                      expires_in: int = 3600) -> str:
        """生成JWT令牌"""
        payload = {
            'user_id': user_id,
            'scopes': scopes,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证JWT令牌"""
        try:
            # 检查缓存
            if token in self.token_cache:
                cached_payload, cached_time = self.token_cache[token]
                if time.time() - cached_time < 300:  # 5分钟缓存
                    return cached_payload
            
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 缓存结果
            self.token_cache[token] = (payload, time.time())
            
            return payload
        
        except jwt.ExpiredSignatureError:
            logger.warning("JWT令牌已过期")
            return None
        except jwt.InvalidTokenError:
            logger.warning("无效的JWT令牌")
            return None
    
    def check_scopes(self, token_scopes: List[str], required_scopes: List[str]) -> bool:
        """检查权限范围"""
        if not required_scopes:
            return True
        
        return any(scope in token_scopes for scope in required_scopes)

class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN):
        self.strategy = strategy
        self.round_robin_index = {}
    
    def select_endpoint(self, service_name: str, endpoints: List[ServiceEndpoint], 
                       client_ip: str = None) -> Optional[ServiceEndpoint]:
        """选择服务端点"""
        # 过滤健康的端点
        healthy_endpoints = [ep for ep in endpoints if ep.is_healthy]
        
        if not healthy_endpoints:
            return None
        
        if self.strategy == LoadBalanceStrategy.ROUND_ROBIN:
            return self._round_robin(service_name, healthy_endpoints)
        elif self.strategy == LoadBalanceStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin(service_name, healthy_endpoints)
        elif self.strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return self._least_connections(healthy_endpoints)
        elif self.strategy == LoadBalanceStrategy.IP_HASH:
            return self._ip_hash(healthy_endpoints, client_ip)
        elif self.strategy == LoadBalanceStrategy.RANDOM:
            return self._random(healthy_endpoints)
        else:
            return healthy_endpoints[0]
    
    def _round_robin(self, service_name: str, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """轮询算法"""
        if service_name not in self.round_robin_index:
            self.round_robin_index[service_name] = 0
        
        index = self.round_robin_index[service_name]
        endpoint = endpoints[index % len(endpoints)]
        self.round_robin_index[service_name] = (index + 1) % len(endpoints)
        
        return endpoint
    
    def _weighted_round_robin(self, service_name: str, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """加权轮询算法"""
        total_weight = sum(ep.weight for ep in endpoints)
        
        if service_name not in self.round_robin_index:
            self.round_robin_index[service_name] = 0
        
        index = self.round_robin_index[service_name] % total_weight
        current_weight = 0
        
        for endpoint in endpoints:
            current_weight += endpoint.weight
            if index < current_weight:
                self.round_robin_index[service_name] += 1
                return endpoint
        
        return endpoints[0]
    
    def _least_connections(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """最少连接算法"""
        return min(endpoints, key=lambda ep: ep.active_connections)
    
    def _ip_hash(self, endpoints: List[ServiceEndpoint], client_ip: str) -> ServiceEndpoint:
        """IP哈希算法"""
        if not client_ip:
            return endpoints[0]
        
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        return endpoints[hash_value % len(endpoints)]
    
    def _random(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """随机算法"""
        import random
        return random.choice(endpoints)

class HealthChecker:
    """健康检查器"""
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.running = False
        self.check_task = None
    
    async def start(self, services: Dict[str, ServiceConfig]):
        """启动健康检查"""
        self.running = True
        self.check_task = asyncio.create_task(self._health_check_loop(services))
        logger.info("健康检查器已启动")
    
    async def stop(self):
        """停止健康检查"""
        self.running = False
        if self.check_task:
            self.check_task.cancel()
            try:
                await self.check_task
            except asyncio.CancelledError:
                pass
        logger.info("健康检查器已停止")
    
    async def _health_check_loop(self, services: Dict[str, ServiceConfig]):
        """健康检查循环"""
        while self.running:
            try:
                await asyncio.sleep(self.check_interval)
                
                for service_config in services.values():
                    await self._check_service_health(service_config)
                
            except Exception as e:
                logger.error(f"健康检查错误: {e}")
    
    async def _check_service_health(self, service_config: ServiceConfig):
        """检查服务健康状态"""
        tasks = []
        for endpoint in service_config.endpoints:
            task = asyncio.create_task(self._check_endpoint_health(endpoint))
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_endpoint_health(self, endpoint: ServiceEndpoint):
        """检查端点健康状态"""
        try:
            start_time = time.time()
            
            async with ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(endpoint.health_url) as response:
                    if response.status == 200:
                        endpoint.is_healthy = True
                        endpoint.response_time = time.time() - start_time
                        endpoint.last_health_check = datetime.now()
                        logger.debug(f"端点 {endpoint.url} 健康检查通过")
                    else:
                        endpoint.is_healthy = False
                        logger.warning(f"端点 {endpoint.url} 健康检查失败，状态码: {response.status}")
        
        except Exception as e:
            endpoint.is_healthy = False
            endpoint.last_health_check = datetime.now()
            logger.warning(f"端点 {endpoint.url} 健康检查异常: {e}")

class RequestTransformer:
    """请求转换器"""
    
    def __init__(self):
        self.transformers = {}
    
    def register_transformer(self, name: str, transformer: Callable):
        """注册转换器"""
        self.transformers[name] = transformer
        logger.debug(f"注册请求转换器: {name}")
    
    async def transform_request(self, transform_name: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """转换请求"""
        if transform_name not in self.transformers:
            return request_data
        
        transformer = self.transformers[transform_name]
        
        if asyncio.iscoroutinefunction(transformer):
            return await transformer(request_data)
        else:
            return transformer(request_data)
    
    async def transform_response(self, transform_name: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """转换响应"""
        if transform_name not in self.transformers:
            return response_data
        
        transformer = self.transformers[transform_name]
        
        if asyncio.iscoroutinefunction(transformer):
            return await transformer(response_data)
        else:
            return transformer(response_data)

class APIGateway:
    """API网关"""
    
    def __init__(self, redis_url: str = None, secret_key: str = "xiaoai-secret"):
        self.routes = {}
        self.services = {}
        self.load_balancer = LoadBalancer()
        self.health_checker = HealthChecker()
        self.request_transformer = RequestTransformer()
        
        # 组件初始化
        self.redis_client = None
        self.rate_limiter = None
        self.auth_manager = AuthManager(secret_key)
        
        if redis_url:
            self.redis_client = redis.from_url(redis_url)
            self.rate_limiter = RateLimiter(self.redis_client)
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'avg_response_time': 0.0
        }
        
        logger.info("API网关初始化完成")
    
    async def initialize(self):
        """初始化网关"""
        if self.redis_client:
            await self.redis_client.ping()
        
        await self.health_checker.start(self.services)
        logger.info("API网关初始化完成")
    
    def register_service(self, service_config: ServiceConfig):
        """注册服务"""
        self.services[service_config.name] = service_config
        logger.info(f"服务 {service_config.name} 注册成功")
    
    def register_route(self, route_config: RouteConfig):
        """注册路由"""
        route_key = f"{route_config.path}:{route_config.version}"
        self.routes[route_key] = route_config
        logger.info(f"路由 {route_key} 注册成功")
    
    def register_transformer(self, name: str, transformer: Callable):
        """注册转换器"""
        self.request_transformer.register_transformer(name, transformer)
    
    async def create_app(self) -> web.Application:
        """创建Web应用"""
        app = web.Application(middlewares=[
            self._cors_middleware,
            self._auth_middleware,
            self._rate_limit_middleware,
            self._logging_middleware,
            self._error_middleware
        ])
        
        # 添加路由
        app.router.add_route('*', '/{path:.*}', self._handle_request)
        
        # 添加健康检查端点
        app.router.add_get('/gateway/health', self._health_endpoint)
        app.router.add_get('/gateway/stats', self._stats_endpoint)
        
        return app
    
    async def _cors_middleware(self, request: web.Request, handler):
        """CORS中间件"""
        response = await handler(request)
        
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response
    
    async def _auth_middleware(self, request: web.Request, handler):
        """认证中间件"""
        # 获取路由配置
        route_config = self._match_route(request)
        
        if route_config and route_config.auth_required:
            auth_header = request.headers.get('Authorization')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                return web.json_response(
                    {'error': '缺少认证令牌'}, 
                    status=401
                )
            
            token = auth_header[7:]  # 移除 'Bearer ' 前缀
            payload = self.auth_manager.verify_token(token)
            
            if not payload:
                return web.json_response(
                    {'error': '无效的认证令牌'}, 
                    status=401
                )
            
            # 检查权限范围
            if not self.auth_manager.check_scopes(
                payload.get('scopes', []), 
                route_config.auth_scopes
            ):
                return web.json_response(
                    {'error': '权限不足'}, 
                    status=403
                )
            
            # 将用户信息添加到请求中
            request['user'] = payload
        
        return await handler(request)
    
    async def _rate_limit_middleware(self, request: web.Request, handler):
        """限流中间件"""
        if not self.rate_limiter:
            return await handler(request)
        
        route_config = self._match_route(request)
        
        if route_config and route_config.rate_limit:
            client_ip = request.remote
            rate_key = f"{client_ip}:{route_config.path}"
            
            if not await self.rate_limiter.is_allowed(rate_key, route_config.rate_limit):
                return web.json_response(
                    {'error': '请求频率过高'}, 
                    status=429
                )
        
        return await handler(request)
    
    async def _logging_middleware(self, request: web.Request, handler):
        """日志中间件"""
        start_time = time.time()
        
        try:
            response = await handler(request)
            
            duration = time.time() - start_time
            
            logger.info(
                f"{request.method} {request.path} - "
                f"状态: {response.status}, 耗时: {duration:.3f}s"
            )
            
            # 更新统计
            self.stats['total_requests'] += 1
            if response.status < 400:
                self.stats['successful_requests'] += 1
            else:
                self.stats['failed_requests'] += 1
            
            # 更新平均响应时间
            total_requests = self.stats['total_requests']
            current_avg = self.stats['avg_response_time']
            self.stats['avg_response_time'] = (
                (current_avg * (total_requests - 1) + duration) / total_requests
            )
            
            return response
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{request.method} {request.path} - 错误: {e}, 耗时: {duration:.3f}s")
            
            self.stats['total_requests'] += 1
            self.stats['failed_requests'] += 1
            
            raise
    
    async def _error_middleware(self, request: web.Request, handler):
        """错误处理中间件"""
        try:
            return await handler(request)
        except web.HTTPException:
            raise
        except Exception as e:
            logger.error(f"请求处理错误: {e}")
            return web.json_response(
                {'error': '内部服务器错误'}, 
                status=500
            )
    
    def _match_route(self, request: web.Request) -> Optional[RouteConfig]:
        """匹配路由"""
        path = request.path
        method = RouteMethod(request.method)
        version = request.headers.get('API-Version', 'v1')
        
        # 精确匹配
        route_key = f"{path}:{version}"
        if route_key in self.routes:
            route_config = self.routes[route_key]
            if method in route_config.methods:
                return route_config
        
        # 模式匹配
        for route_key, route_config in self.routes.items():
            route_path, route_version = route_key.split(':', 1)
            
            if route_version == version and method in route_config.methods:
                # 简单的路径匹配（可以扩展为正则表达式）
                if self._path_matches(path, route_path):
                    return route_config
        
        return None
    
    def _path_matches(self, request_path: str, route_path: str) -> bool:
        """路径匹配"""
        # 简单的通配符匹配
        if '*' in route_path:
            pattern = route_path.replace('*', '.*')
            return re.match(f"^{pattern}$", request_path) is not None
        
        return request_path == route_path
    
    async def _handle_request(self, request: web.Request) -> web.Response:
        """处理请求"""
        route_config = self._match_route(request)
        
        if not route_config:
            return web.json_response(
                {'error': '路由未找到'}, 
                status=404
            )
        
        # 获取服务配置
        service_config = self.services.get(route_config.service_name)
        if not service_config:
            return web.json_response(
                {'error': '服务未找到'}, 
                status=503
            )
        
        # 选择服务端点
        endpoint = self.load_balancer.select_endpoint(
            route_config.service_name,
            service_config.endpoints,
            request.remote
        )
        
        if not endpoint:
            return web.json_response(
                {'error': '服务不可用'}, 
                status=503
            )
        
        # 转发请求
        return await self._forward_request(request, route_config, endpoint)
    
    async def _forward_request(self, request: web.Request, 
                              route_config: RouteConfig, 
                              endpoint: ServiceEndpoint) -> web.Response:
        """转发请求"""
        endpoint.active_connections += 1
        
        try:
            # 构建目标URL
            target_url = f"{endpoint.url}{request.path_qs}"
            
            # 准备请求数据
            headers = dict(request.headers)
            headers.pop('Host', None)  # 移除Host头
            
            # 读取请求体
            body = None
            if request.method in ['POST', 'PUT', 'PATCH']:
                body = await request.read()
            
            # 请求转换
            if route_config.request_transform:
                request_data = {
                    'headers': headers,
                    'body': body,
                    'params': dict(request.query)
                }
                
                transformed_data = await self.request_transformer.transform_request(
                    route_config.request_transform, 
                    request_data
                )
                
                headers = transformed_data.get('headers', headers)
                body = transformed_data.get('body', body)
            
            # 发送请求
            timeout = aiohttp.ClientTimeout(total=route_config.timeout)
            
            async with ClientSession(timeout=timeout) as session:
                async with session.request(
                    request.method,
                    target_url,
                    headers=headers,
                    data=body
                ) as response:
                    
                    response_body = await response.read()
                    response_headers = dict(response.headers)
                    
                    # 响应转换
                    if route_config.response_transform:
                        response_data = {
                            'headers': response_headers,
                            'body': response_body,
                            'status': response.status
                        }
                        
                        transformed_data = await self.request_transformer.transform_response(
                            route_config.response_transform,
                            response_data
                        )
                        
                        response_headers = transformed_data.get('headers', response_headers)
                        response_body = transformed_data.get('body', response_body)
                    
                    # 构建响应
                    web_response = web.Response(
                        body=response_body,
                        status=response.status,
                        headers=response_headers
                    )
                    
                    return web_response
        
        except asyncio.TimeoutError:
            logger.error(f"请求超时: {endpoint.url}")
            return web.json_response(
                {'error': '请求超时'}, 
                status=504
            )
        
        except Exception as e:
            logger.error(f"转发请求失败: {e}")
            return web.json_response(
                {'error': '服务错误'}, 
                status=502
            )
        
        finally:
            endpoint.active_connections -= 1
    
    async def _health_endpoint(self, request: web.Request) -> web.Response:
        """健康检查端点"""
        health_status = {
            'status': 'healthy',
            'services': {},
            'timestamp': datetime.now().isoformat()
        }
        
        for service_name, service_config in self.services.items():
            service_health = {
                'endpoints': []
            }
            
            for endpoint in service_config.endpoints:
                service_health['endpoints'].append({
                    'url': endpoint.url,
                    'healthy': endpoint.is_healthy,
                    'active_connections': endpoint.active_connections,
                    'response_time': endpoint.response_time,
                    'last_check': endpoint.last_health_check.isoformat()
                })
            
            health_status['services'][service_name] = service_health
        
        return web.json_response(health_status)
    
    async def _stats_endpoint(self, request: web.Request) -> web.Response:
        """统计信息端点"""
        return web.json_response(self.stats)
    
    async def close(self):
        """关闭网关"""
        await self.health_checker.stop()
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("API网关已关闭")

# 全局API网关实例
_api_gateway = None

async def get_api_gateway(redis_url: str = None, secret_key: str = "xiaoai-secret") -> APIGateway:
    """获取API网关实例"""
    global _api_gateway
    
    if _api_gateway is None:
        _api_gateway = APIGateway(redis_url, secret_key)
        await _api_gateway.initialize()
    
    return _api_gateway

# 装饰器
def route(path: str, methods: List[str] = None, **kwargs):
    """路由装饰器"""
    def decorator(func):
        route_methods = [RouteMethod(m.upper()) for m in (methods or ['GET'])]
        
        route_config = RouteConfig(
            path=path,
            methods=route_methods,
            service_name=kwargs.get('service_name', 'default'),
            **kwargs
        )
        
        func._route_config = route_config
        return func
    
    return decorator 