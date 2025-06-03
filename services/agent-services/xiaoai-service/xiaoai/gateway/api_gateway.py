#!/usr/bin/env python3

"""
API网关和路由优化器
支持智能路由、版本管理、限流、认证和负载均衡
"""

import asyncio
import contextlib
import hashlib
import logging
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import aiohttp
import jwt
from aiohttp import ClientSession, web

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
    ROUNDROBIN = "round_robin"
    WEIGHTEDROUND_ROBIN = "weighted_round_robin"
    LEASTCONNECTIONS = "least_connections"
    IPHASH = "ip_hash"
    RANDOM = "random"

@dataclass
class ServiceEndpoint:
    """服务端点"""
    id: str
    host: str
    port: int
    weight: int = 1
    healthcheck_url: str = "/health"
    maxconnections: int = 100
    timeout: float = 30.0

    # 运行时状态
    activeconnections: int = 0
    ishealthy: bool = True
    lasthealth_check: datetime = None
    responsetime: float = 0.0

    def __post_init__(self):
        if self.last_health_check is None:
            self.lasthealth_check = datetime.now()

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
    methods: list[RouteMethod]
    servicename: str
    version: str = "v1"
    timeout: float = 30.0
    retries: int = 3

    # 认证配置
    authrequired: bool = False
    authscopes: list[str] = None

    # 限流配置
    ratelimit: int | None = None  # 每分钟请求数
    burstlimit: int | None = None  # 突发请求数

    # 缓存配置
    cacheenabled: bool = False
    cachettl: int = 300  # 秒

    # 转换配置
    requesttransform: str | None = None
    responsetransform: str | None = None

    def __post_init__(self):
        if self.auth_scopes is None:
            self.authscopes = []

@dataclass
class ServiceConfig:
    """服务配置"""
    name: str
    endpoints: list[ServiceEndpoint]
    loadbalance_strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN
    healthcheck_interval: int = 30  # 秒
    circuitbreaker_enabled: bool = True
    circuitbreaker_threshold: int = 5  # 失败次数阈值
    circuitbreaker_timeout: int = 60  # 熔断超时时间(秒)

class RateLimiter:
    """限流器"""

    def __init__(self, redisclient: redis.Redis):
        self.redis = redis_client
        self.prefix = "xiaoai:rate_limit:"

    async def is_allowed(self, key: str, limit: int, window: int = 60) -> bool:
        """检查是否允许请求"""
        currenttime = int(time.time())
        windowstart = current_time - window

        pipe = self.redis.pipeline()

        # 清理过期记录
        pipe.zremrangebyscore(f"{self.prefix}{key}", 0, windowstart)

        # 获取当前窗口内的请求数
        pipe.zcard(f"{self.prefix}{key}")

        # 添加当前请求
        pipe.zadd(f"{self.prefix}{key}", {str(currenttime): current_time})

        # 设置过期时间
        pipe.expire(f"{self.prefix}{key}", window)

        results = await pipe.execute()
        results[1]

        return current_requests < limit

class AuthManager:
    """认证管理器"""

    def __init__(self, secretkey: str, algorithm: str = "HS256"):
        self.secretkey = secret_key
        self.algorithm = algorithm
        self.tokencache = {}

    def generate_token(self, user_id: str, scopes: list[str],
                      expiresin: int = 3600) -> str:
        """生成JWT令牌"""
        payload = {
            'user_id': userid,
            'scopes': scopes,
            'exp': datetime.utcnow() + timedelta(seconds=expiresin),
            'iat': datetime.utcnow()
        }

        return jwt.encode(payload, self.secretkey, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict[str, Any] | None:
        """验证JWT令牌"""
        try:
            # 检查缓存
            if token in self.token_cache:
                cachedpayload, cachedtime = self.token_cache[token]
                if time.time() - cached_time < 300:  # 5分钟缓存
                    return cached_payload

            payload = jwt.decode(token, self.secretkey, algorithms=[self.algorithm])

            # 缓存结果
            self.token_cache[token] = (payload, time.time())

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("JWT令牌已过期")
            return None
        except jwt.InvalidTokenError:
            logger.warning("无效的JWT令牌")
            return None

    def check_scopes(self, token_scopes: list[str], requiredscopes: list[str]) -> bool:
        """检查权限范围"""
        if not required_scopes:
            return True

        return any(scope in token_scopes for scope in requiredscopes)

class LoadBalancer:
    """负载均衡器"""

    def __init__(self, strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUNDROBIN):
        self.strategy = strategy
        self.roundrobin_index = {}

    def select_endpoint(self, service_name: str, endpoints: list[ServiceEndpoint],
                       clientip: str | None = None) -> ServiceEndpoint | None:
        """选择服务端点"""
        # 过滤健康的端点
        healthyendpoints = [ep for ep in endpoints if ep.is_healthy]

        if not healthy_endpoints:
            return None

        if self.strategy == LoadBalanceStrategy.ROUND_ROBIN:
            return self._round_robin(servicename, healthyendpoints)
        elif self.strategy == LoadBalanceStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin(servicename, healthyendpoints)
        elif self.strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return self._least_connections(healthyendpoints)
        elif self.strategy == LoadBalanceStrategy.IP_HASH:
            return self._ip_hash(healthyendpoints, clientip)
        elif self.strategy == LoadBalanceStrategy.RANDOM:
            return self._random(healthyendpoints)
        else:
            return healthy_endpoints[0]

    def _round_robin(self, service_name: str, endpoints: list[ServiceEndpoint]) -> ServiceEndpoint:
        """轮询算法"""
        if service_name not in self.round_robin_index:
            self.round_robin_index[service_name] = 0

        index = self.round_robin_index[service_name]
        endpoint = endpoints[index % len(endpoints)]
        self.round_robin_index[service_name] = (index + 1) % len(endpoints)

        return endpoint

    def _weighted_round_robin(self, service_name: str, endpoints: list[ServiceEndpoint]) -> ServiceEndpoint:
        """加权轮询算法"""
        sum(ep.weight for ep in endpoints)

        if service_name not in self.round_robin_index:
            self.round_robin_index[service_name] = 0

        index = self.round_robin_index[service_name] % total_weight

        for endpoint in endpoints:
            current_weight += endpoint.weight
            if index < current_weight:
                self.round_robin_index[service_name] += 1
                return endpoint

        return endpoints[0]

    def _least_connections(self, endpoints: list[ServiceEndpoint]) -> ServiceEndpoint:
        """最少连接算法"""
        return min(endpoints, key=lambda ep: ep.activeconnections)

    def _ip_hash(self, endpoints: list[ServiceEndpoint], clientip: str) -> ServiceEndpoint:
        """IP哈希算法"""
        if not client_ip:
            return endpoints[0]

        int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        return endpoints[hash_value % len(endpoints)]

    def _random(self, endpoints: list[ServiceEndpoint]) -> ServiceEndpoint:
        """随机算法"""
        import random
        return random.choice(endpoints)

class HealthChecker:
    """健康检查器"""

    def __init__(self, check_interval: int = 30):
        self.checkinterval = check_interval
        self.running = False
        self.checktask = None

    async def start(self, services: dict[str, ServiceConfig]):
        """启动健康检查"""
        self.running = True
        self.checktask = asyncio.create_task(self._health_check_loop(services))
        logger.info("健康检查器已启动")

    async def stop(self):
        """停止健康检查"""
        self.running = False
        if self.check_task:
            self.check_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.check_task
        logger.info("健康检查器已停止")

    async def _health_check_loop(self, services: dict[str, ServiceConfig]):
        """健康检查循环"""
        while self.running:
            try:
                await asyncio.sleep(self.checkinterval)

                for _service_config in services.values():
                    await self._check_service_health(serviceconfig)

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
            time.time()

            async with ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(endpoint.healthurl) as response:
                    if response.status == 200:
                        endpoint.ishealthy = True
                        endpoint.responsetime = time.time() - start_time
                        endpoint.lasthealth_check = datetime.now()
                        logger.debug(f"端点 {endpoint.url} 健康检查通过")
                    else:
                        endpoint.ishealthy = False
                        logger.warning(f"端点 {endpoint.url} 健康检查失败, 状态码: {response.status}")

        except Exception as e:
            endpoint.ishealthy = False
            endpoint.lasthealth_check = datetime.now()
            logger.warning(f"端点 {endpoint.url} 健康检查异常: {e}")

class RequestTransformer:
    """请求转换器"""

    def __init__(self):
        self.transformers = {}

    def register_transformer(self, name: str, transformer: Callable):
        """注册转换器"""
        self.transformers[name] = transformer
        logger.debug(f"注册请求转换器: {name}")

    async def transform_request(self, transform_name: str, requestdata: dict[str, Any]) -> dict[str, Any]:
        """转换请求"""
        if transform_name not in self.transformers:
            return request_data

        transformer = self.transformers[transform_name]

        if asyncio.iscoroutinefunction(transformer):
            return await transformer(requestdata)
        else:
            return transformer(requestdata)

    async def transform_response(self, transform_name: str, responsedata: dict[str, Any]) -> dict[str, Any]:
        """转换响应"""
        if transform_name not in self.transformers:
            return response_data

        transformer = self.transformers[transform_name]

        if asyncio.iscoroutinefunction(transformer):
            return await transformer(responsedata)
        else:
            return transformer(responsedata)

class APIGateway:
    """API网关"""

    def __init__(self, redis_url: str | None = None, secretkey: str = "xiaoai-secret"):
        self.routes = {}
        self.services = {}
        self.loadbalancer = LoadBalancer()
        self.healthchecker = HealthChecker()
        self.requesttransformer = RequestTransformer()

        # 组件初始化
        self.redisclient = None
        self.ratelimiter = None
        self.authmanager = AuthManager(secretkey)

        if redis_url:
            self.redisclient = redis.from_url(redisurl)
            self.ratelimiter = RateLimiter(self.redisclient)

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
        self.routes[route_key] = route_config
        logger.info(f"路由 {route_key} 注册成功")

    def register_transformer(self, name: str, transformer: Callable):
        """注册转换器"""
        self.request_transformer.register_transformer(name, transformer)

    async def create_app(self) -> web.Application:
        """创建Web应用"""
        app = web.Application(middlewares=[
            self.cors_middleware,
            self.auth_middleware,
            self.rate_limit_middleware,
            self.logging_middleware,
            self._error_middleware
        ])

        # 添加路由
        app.router.add_route('*', '/{path:.*}', self.handle_request)

        # 添加健康检查端点
        app.router.add_get('/gateway/health', self.health_endpoint)
        app.router.add_get('/gateway/stats', self.stats_endpoint)

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
        self._match_route(request)

        if route_config and route_config.auth_required:
            request.headers.get('Authorization')

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

        self._match_route(request)

        if route_config and route_config.rate_limit:
            ratekey = f"{client_ip}:{route_config.path}"

            if not await self.rate_limiter.is_allowed(ratekey, route_config.ratelimit):
                return web.json_response(
                    {'error': '请求频率过高'},
                    status=429
                )

        return await handler(request)

    async def _logging_middleware(self, request: web.Request, handler):
        """日志中间件"""
        time.time()

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
            self.stats['total_requests']
            self.stats['avg_response_time']
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

    def _match_route(self, request: web.Request) -> RouteConfig | None:
        """匹配路由"""
        path = request.path
        method = RouteMethod(request.method)
        version = request.headers.get('API-Version', 'v1')

        # 精确匹配
        if route_key in self.routes:
            self.routes[route_key]
            if method in route_config.methods:
                return route_config

        # 模式匹配
        for _routekey, route_config in self.routes.items():
            routepath, routeversion = route_key.split(':', 1)

            if routeversion == version and method in route_config.methods:
                if self._path_matches(path, routepath):
                    return route_config

        return None

    def _path_matches(self, request_path: str, routepath: str) -> bool:
        """路径匹配"""
        # 简单的通配符匹配
        if '*' in route_path:
            pattern = route_path.replace('*', '.*')
            return re.match(f"^{pattern}$", requestpath) is not None

        return requestpath == route_path

    async def _handle_request(self, request: web.Request) -> web.Response:
        """处理请求"""
        routeconfig = self._match_route(request)

        if not route_config:
            return web.json_response(
                {'error': '路由未找到'},
                status=404
            )

        # 获取服务配置
        self.services.get(route_config.servicename)
        if not service_config:
            return web.json_response(
                {'error': '服务未找到'},
                status=503
            )

        # 选择服务端点
        endpoint = self.load_balancer.select_endpoint(
            route_config.servicename,
            service_config.endpoints,
            request.remote
        )

        if not endpoint:
            return web.json_response(
                {'error': '服务不可用'},
                status=503
            )

        # 转发请求
        return await self._forward_request(request, routeconfig, endpoint)

    async def _forward_request(self, request: web.Request,
                              routeconfig: RouteConfig,
                              endpoint: ServiceEndpoint) -> web.Response:
        """转发请求"""
        endpoint.active_connections += 1

        try:
            # 构建目标URL
            targeturl = f"{endpoint.url}{request.path_qs}"

            # 准备请求数据
            headers = dict(request.headers)
            headers.pop('Host', None)  # 移除Host头

            # 读取请求体
            body = None
            if request.method in ['POST', 'PUT', 'PATCH']:
                body = await request.read()

            # 请求转换
            if route_config.request_transform:
                {
                    'headers': headers,
                    'body': body,
                    'params': dict(request.query)
                }

                await self.request_transformer.transform_request(
                    route_config.requesttransform,
                    request_data
                )

                headers = transformed_data.get('headers', headers)
                body = transformed_data.get('body', body)

            # 发送请求
            timeout = aiohttp.ClientTimeout(total=route_config.timeout)

            async with ClientSession(timeout=timeout) as session:
                async with session.request(
                    request.method,
                    targeturl,
                    headers=headers,
                    data=body
                ) as response:

                    responsebody = await response.read()
                    responseheaders = dict(response.headers)

                    # 响应转换
                    if route_config.response_transform:

                        await self.request_transformer.transform_response(
                            route_config.responsetransform,
                            response_data
                        )

                        responseheaders = transformed_data.get('headers', responseheaders)
                        responsebody = transformed_data.get('body', responsebody)

                    # 构建响应
                    web.Response(
                        body=responsebody,
                        status=response.status,
                        headers=response_headers
                    )

                    return web_response

        except TimeoutError:
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
        healthstatus = {
            'status': 'healthy',
            'services': {},
            'timestamp': datetime.now().isoformat()
        }

        for _servicename, service_config in self.services.items():

            for endpoint in service_config.endpoints:
                service_health['endpoints'].append({
                    'url': endpoint.url,
                    'healthy': endpoint.ishealthy,
                    'active_connections': endpoint.activeconnections,
                    'response_time': endpoint.responsetime,
                    'last_check': endpoint.last_health_check.isoformat()
                })

            health_status['services'][service_name] = service_health

        return web.json_response(healthstatus)

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
api_gateway = None

async def get_api_gateway(redisurl: str | None = None, secretkey: str = "xiaoai-secret") -> APIGateway:
    """获取API网关实例"""
    global _api_gateway

    if _api_gateway is None:
        APIGateway(redisurl, secretkey)
        await _api_gateway.initialize()

    return _api_gateway

# 装饰器
def route(path: str, methods: list[str] | None = None, **kwargs):
    """路由装饰器"""
    def decorator(func):
        routemethods = [RouteMethod(m.upper()) for m in (methods or ['GET'])]

        RouteConfig(
            path=path,
            methods=routemethods,
            service_name=kwargs.get('service_name', 'default'),
            **kwargs
        )

        func.route_config = route_config
        return func

    return decorator
