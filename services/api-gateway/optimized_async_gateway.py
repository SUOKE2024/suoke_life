"""
optimized_async_gateway - 索克生活项目模块
"""

import asyncio
import hashlib
import json
import logging
import ssl
import time
import uuid
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

import aiohttp
import aioredis
import asyncpg
import certifi
import jwt
import psutil
from aiohttp import ClientSession, ClientTimeout, web
from aiohttp_cors import ResourceOptions
from aiohttp_cors import setup as cors_setup

#! / usr / bin / env python3
"""
索克生活 - 优化后的异步API网关
实现高并发I / O处理、智能负载均衡和性能监控
"""


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ServiceEndpoint:
    """服务端点配置"""

    name: str
    url: str
    health_check_path: str = " / health"
    timeout: float = 30.0
    max_retries: int = 3
    weight: int = 1
    is_healthy: bool = True
    last_health_check: datetime = None
    response_times: deque = None

    def __post_init__(self) -> None:
        """TODO: 添加文档字符串"""
        if self.response_times is None:
            self.response_times = deque(maxlen=100)
        if self.last_health_check is None:
            self.last_health_check = datetime.now()


@dataclass
class RequestMetrics:
    """请求指标"""

    request_id: str
    method: str
    path: str
    service: str
    start_time: datetime
    end_time: Optional[datetime] = None
    response_time: float = 0.0
    status_code: int = 0
    error_message: Optional[str] = None
    user_id: Optional[str] = None


class CircuitBreaker:
    """熔断器"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        """TODO: 添加文档字符串"""
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func: Callable) -> Callable:
        """装饰器：熔断器调用"""

        @wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                else:
                    raise Exception("Circuit breaker is OPEN")

            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise e

        return wrapper

    def _should_attempt_reset(self) -> bool:
        """是否应该尝试重置"""
        return (
            self.last_failure_time
            and datetime.now() - self.last_failure_time
            > timedelta(seconds=self.recovery_timeout)
        )

    def _on_success(self) -> None:
        """成功时的处理"""
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self) -> None:
        """失败时的处理"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class LoadBalancer:
    """智能负载均衡器"""

    def __init__(self, strategy: str = "weighted_round_robin"):
        """TODO: 添加文档字符串"""
        self.strategy = strategy
        self.services: Dict[str, List[ServiceEndpoint]] = defaultdict(list)
        self.current_index: Dict[str, int] = defaultdict(int)
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

    def add_service(self, service_name: str, endpoint: ServiceEndpoint):
        """添加服务端点"""
        self.services[service_name].append(endpoint)
        breaker_key = f"{service_name}:{endpoint.url}"
        self.circuit_breakers[breaker_key] = CircuitBreaker()
        logger.info(f"添加服务端点: {service_name} -> {endpoint.url}")

    def get_endpoint(self, service_name: str) -> Optional[ServiceEndpoint]:
        """获取服务端点"""
        endpoints = self.services.get(service_name, [])
        if not endpoints:
            return None

        healthy_endpoints = [ep for ep in endpoints if ep.is_healthy]
        if not healthy_endpoints:
            return None

        if self.strategy == "round_robin":
            return self._round_robin_select(service_name, healthy_endpoints)
        elif self.strategy == "weighted_round_robin":
            return self._weighted_round_robin_select(service_name, healthy_endpoints)
        elif self.strategy == "least_response_time":
            return self._least_response_time_select(healthy_endpoints)
        else:
            return healthy_endpoints[0]

    def _round_robin_select(
        self, service_name: str, endpoints: List[ServiceEndpoint]
    ) -> ServiceEndpoint:
        """轮询选择"""
        index = self.current_index[service_name] % len(endpoints)
        self.current_index[service_name] += 1
        return endpoints[index]

    def _weighted_round_robin_select(
        self, service_name: str, endpoints: List[ServiceEndpoint]
    ) -> ServiceEndpoint:
        """加权轮询选择"""
        total_weight = sum(ep.weight for ep in endpoints)
        if total_weight == 0:
            return endpoints[0]

        # 简化的加权轮询实现
        current = self.current_index[service_name] % total_weight
        cumulative_weight = 0

        for endpoint in endpoints:
            cumulative_weight += endpoint.weight
            if current < cumulative_weight:
                self.current_index[service_name] += 1
                return endpoint

        return endpoints[0]

    def _least_response_time_select(
        self, endpoints: List[ServiceEndpoint]
    ) -> ServiceEndpoint:
        """最少响应时间选择"""

        def avg_response_time(endpoint: ServiceEndpoint) -> float:
            """TODO: 添加文档字符串"""
            if not endpoint.response_times:
                return 0.0
            return sum(endpoint.response_times) / len(endpoint.response_times)

        return min(endpoints, key=avg_response_time)

    def record_response_time(
        self, service_name: str, endpoint_url: str, response_time: float
    ):
        """记录响应时间"""
        for endpoint in self.services[service_name]:
            if endpoint.url == endpoint_url:
                endpoint.response_times.append(response_time)
                break

    def mark_unhealthy(self, service_name: str, endpoint_url: str):
        """标记端点为不健康"""
        for endpoint in self.services[service_name]:
            if endpoint.url == endpoint_url:
                endpoint.is_healthy = False
                logger.warning(f"标记端点为不健康: {service_name} -> {endpoint_url}")
                break

    def mark_healthy(self, service_name: str, endpoint_url: str):
        """标记端点为健康"""
        for endpoint in self.services[service_name]:
            if endpoint.url == endpoint_url:
                endpoint.is_healthy = True
                logger.info(f"标记端点为健康: {service_name} -> {endpoint_url}")
                break


class RateLimiter:
    """速率限制器"""

    def __init__(self, redis_client: aioredis.Redis):
        """TODO: 添加文档字符串"""
        self.redis = redis_client

    async def is_allowed(self, key: str, limit: int, window: int = 60) -> bool:
        """检查是否允许请求"""
        current_time = int(time.time())
        window_start = current_time - window

        # 使用Redis的滑动窗口算法
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {str(uuid.uuid4()): current_time})
        pipe.expire(key, window)

        results = await pipe.execute()
        current_requests = results[1]

        return current_requests < limit


class CacheManager:
    """缓存管理器"""

    def __init__(self, redis_client: aioredis.Redis):
        """TODO: 添加文档字符串"""
        self.redis = redis_client

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"缓存获取失败: {key}, 错误: {e}")
        return None

    async def set(self, key: str, value: Any, ttl: int = 300):
        """设置缓存"""
        try:
            await self.redis.setex(key, ttl, json.dumps(value, default=str))
        except Exception as e:
            logger.error(f"缓存设置失败: {key}, 错误: {e}")

    async def delete(self, key: str):
        """删除缓存"""
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"缓存删除失败: {key}, 错误: {e}")

    def generate_cache_key(self, method: str, path: str, params: Dict = None) -> str:
        """生成缓存键"""
        key_parts = [method, path]
        if params:
            sorted_params = sorted(params.items())
            params_str = "&".join(f"{k} = {v}" for k, v in sorted_params)
            key_parts.append(params_str)

        key_string = "|".join(key_parts)
        return f"api_cache:{hashlib.md5(key_string.encode()).hexdigest()}"


class MetricsCollector:
    """指标收集器"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.metrics: List[RequestMetrics] = []
        self.metrics_lock = asyncio.Lock()
        self.max_metrics = 10000  # 保持最近10000个请求的指标

    async def record_request(self, metrics: RequestMetrics):
        """记录请求指标"""
        async with self.metrics_lock:
            self.metrics.append(metrics)
            if len(self.metrics) > self.max_metrics:
                self.metrics.pop(0)

    async def get_metrics_summary(self, time_window: int = 300) -> Dict[str, Any]:
        """获取指标摘要"""
        async with self.metrics_lock:
            now = datetime.now()
            recent_metrics = [
                m
                for m in self.metrics
                if m.start_time > now - timedelta(seconds=time_window)
            ]

            if not recent_metrics:
                return {}

            total_requests = len(recent_metrics)
            successful_requests = len(
                [m for m in recent_metrics if 200 <= m.status_code < 400]
            )
            failed_requests = total_requests - successful_requests

            response_times = [
                m.response_time for m in recent_metrics if m.response_time > 0
            ]
            avg_response_time = (
                sum(response_times) / len(response_times) if response_times else 0
            )

            # 按服务统计
            service_stats = defaultdict(
                lambda: {"count": 0, "errors": 0, "total_time": 0}
            )
            for metric in recent_metrics:
                service_stats[metric.service]["count"] += 1
                if metric.status_code >= 400:
                    service_stats[metric.service]["errors"] += 1
                service_stats[metric.service]["total_time"] += metric.response_time

            return {
                "time_window": time_window,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": (
                    successful_requests / total_requests if total_requests > 0 else 0
                ),
                "average_response_time": avg_response_time,
                "requests_per_second": total_requests / time_window,
                "service_stats": dict(service_stats),
            }


class OptimizedAsyncGateway:
    """优化后的异步API网关"""

    def __init__(
        self,
        redis_url: str = "redis: / /localhost:6379",
        database_url: Optional[str] = None,
        jwt_secret: str = "your - secret - key",
    ):
        self.redis_url = redis_url
        self.database_url = database_url
        self.jwt_secret = jwt_secret

        # 核心组件
        self.load_balancer = LoadBalancer()
        self.redis_client: Optional[aioredis.Redis] = None
        self.rate_limiter: Optional[RateLimiter] = None
        self.cache_manager: Optional[CacheManager] = None
        self.metrics_collector = MetricsCollector()

        # HTTP客户端会话
        self.client_session: Optional[ClientSession] = None

        # 数据库连接池
        self.db_pool: Optional[asyncpg.Pool] = None

        # 应用实例
        self.app: Optional[web.Application] = None

        logger.info("异步API网关初始化完成")

    async def initialize(self) -> None:
        """异步初始化"""
        # 初始化Redis连接
        self.redis_client = await aioredis.from_url(self.redis_url)
        self.rate_limiter = RateLimiter(self.redis_client)
        self.cache_manager = CacheManager(self.redis_client)

        # 初始化HTTP客户端
        timeout = ClientTimeout(total=30, connect=10)
        connector = aiohttp.TCPConnector(
            limit=100,  # 总连接池大小
            limit_per_host=20,  # 每个主机的连接数
            ssl=ssl.create_default_context(cafile=certifi.where()),
        )
        self.client_session = ClientSession(timeout=timeout, connector=connector)

        # 初始化数据库连接池
        if self.database_url:
            self.db_pool = await asyncpg.create_pool(
                self.database_url, min_size=5, max_size=20
            )

        # 初始化Web应用
        self._setup_web_app()

        # 注册服务端点
        await self._register_service_endpoints()

        # 启动健康检查
        asyncio.create_task(self._health_check_loop())

        logger.info("异步API网关初始化完成")

    def _setup_web_app(self) -> None:
        """设置Web应用"""
        self.app = web.Application(
            middlewares=[
                self._auth_middleware,
                self._rate_limit_middleware,
                self._cache_middleware,
                self._metrics_middleware,
                self._error_handling_middleware,
            ]
        )

        # 设置CORS
        cors = cors_setup(
            self.app,
            defaults={
                " * ": ResourceOptions(
                    allow_credentials=True,
                    expose_headers=" * ",
                    allow_headers=" * ",
                    allow_methods=" * ",
                )
            },
        )

        # 注册路由
        self.app.router.add_route(
            " * ", " / api / {service} / {path:. * }", self._proxy_handler
        )
        self.app.router.add_get(" / health", self._health_handler)
        self.app.router.add_get(" / metrics", self._metrics_handler)

        # 添加CORS到所有路由
        for route in list(self.app.router.routes()):
            cors.add(route)

    async def _register_service_endpoints(self) -> None:
        """注册服务端点"""
        # 注册四个智能体服务
        services = [
            ("xiaoai", "http: / /xiaoai - service:8001"),
            ("xiaoke", "http: / /xiaoke - service:8002"),
            ("laoke", "http: / /laoke - service:8003"),
            ("soer", "http: / /soer - service:8004"),
            ("auth", "http: / /auth - service:8005"),
            ("user", "http: / /user - service:8006"),
            ("health - data", "http: / /health - data - service:8007"),
            ("medical - resource", "http: / /medical - resource - service:8008"),
        ]

        for service_name, url in services:
            endpoint = ServiceEndpoint(
                name=f"{service_name} - primary", url=url, weight=1
            )
            self.load_balancer.add_service(service_name, endpoint)

    @web.middleware
    async def _auth_middleware(
        self, request: web.Request, handler: Callable
    ) -> web.Response:
        """认证中间件"""
        # 跳过健康检查和指标端点
        if request.path in [" / health", " / metrics"]:
            return await handler(request)

        # 检查JWT令牌
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
                request["user"] = payload
            except jwt.InvalidTokenError:
                return web.json_response({"error": "Invalid token"}, status=401)
        else:
            # 对于某些公开端点，可以跳过认证
            if not request.path.startswith(" / api / auth / "):
                return web.json_response(
                    {"error": "Authentication required"}, status=401
                )

        return await handler(request)

    @web.middleware
    async def _rate_limit_middleware(
        self, request: web.Request, handler: Callable
    ) -> web.Response:
        """速率限制中间件"""
        # 获取客户端标识
        client_id = request.remote
        if "user" in request and "user_id" in request["user"]:
            client_id = request["user"]["user_id"]

        # 检查速率限制
        rate_limit_key = f"rate_limit:{client_id}"
        if not await self.rate_limiter.is_allowed(rate_limit_key, limit=100, window=60):
            return web.json_response({"error": "Rate limit exceeded"}, status=429)

        return await handler(request)

    @web.middleware
    async def _cache_middleware(
        self, request: web.Request, handler: Callable
    ) -> web.Response:
        """缓存中间件"""
        # 只缓存GET请求
        if request.method != "GET":
            return await handler(request)

        # 生成缓存键
        cache_key = self.cache_manager.generate_cache_key(
            request.method, request.path_qs, dict(request.query)
        )

        # 尝试从缓存获取
        cached_response = await self.cache_manager.get(cache_key)
        if cached_response:
            return web.json_response(cached_response)

        # 执行请求
        response = await handler(request)

        # 缓存成功响应
        if response.status == 200 and response.content_type == "application / json":
            try:
                response_data = json.loads(response.text)
                await self.cache_manager.set(cache_key, response_data, ttl=300)
            except:
                pass  # 忽略缓存错误

        return response

    @web.middleware
    async def _metrics_middleware(
        self, request: web.Request, handler: Callable
    ) -> web.Response:
        """指标收集中间件"""
        start_time = datetime.now()
        request_id = str(uuid.uuid4())

        # 提取服务名称
        service_name = "unknown"
        if request.path.startswith("/api/"):
            path_parts = request.path.split("/")
            if len(path_parts) >= 3:
                service_name = path_parts[2]

        try:
            response = await handler(request)

            # 记录成功指标
            metrics = RequestMetrics(
                request_id=request_id,
                method=request.method,
                path=request.path,
                service=service_name,
                start_time=start_time,
                end_time=datetime.now(),
                response_time=(datetime.now() - start_time).total_seconds(),
                status_code=response.status,
                user_id=request.get("user", {}).get("user_id"),
            )

            await self.metrics_collector.record_request(metrics)
            return response

        except Exception as e:
            # 记录错误指标
            metrics = RequestMetrics(
                request_id=request_id,
                method=request.method,
                path=request.path,
                service=service_name,
                start_time=start_time,
                end_time=datetime.now(),
                response_time=(datetime.now() - start_time).total_seconds(),
                status_code=500,
                error_message=str(e),
                user_id=request.get("user", {}).get("user_id"),
            )

            await self.metrics_collector.record_request(metrics)
            raise

    @web.middleware
    async def _error_handling_middleware(
        self, request: web.Request, handler: Callable
    ) -> web.Response:
        """错误处理中间件"""
        try:
            return await handler(request)
        except web.HTTPException:
            raise
        except Exception as e:
            logger.error(f"请求处理错误: {request.path}, 错误: {e}")
            return web.json_response(
                {"error": "Internal server error", "message": str(e)}, status=500
            )

    async def _proxy_handler(self, request: web.Request) -> web.Response:
        """代理处理器"""
        # 解析路径
        service_name = request.match_info["service"]
        path = request.match_info["path"]

        # 获取服务端点
        endpoint = self.load_balancer.get_endpoint(service_name)
        if not endpoint:
            return web.json_response(
                {"error": f"Service {service_name} not available"}, status=503
            )

        # 构建目标URL
        target_url = f"{endpoint.url} / {path}"
        if request.query_string:
            target_url += f"?{request.query_string}"

        # 准备请求数据
        headers = dict(request.headers)
        headers.pop("Host", None)  # 移除Host头

        data = None
        if request.method in ["POST", "PUT", "PATCH"]:
            data = await request.read()

        start_time = time.time()

        try:
            # 发送请求
            async with self.client_session.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=data,
                timeout=ClientTimeout(total=endpoint.timeout),
            ) as response:
                response_time = time.time() - start_time

                # 记录响应时间
                self.load_balancer.record_response_time(
                    service_name, endpoint.url, response_time
                )

                # 读取响应
                response_data = await response.read()

                # 构建响应
                return web.Response(
                    body=response_data,
                    status=response.status,
                    headers=response.headers,
                    content_type=response.content_type,
                )

        except asyncio.TimeoutError:
            self.load_balancer.mark_unhealthy(service_name, endpoint.url)
            return web.json_response({"error": "Service timeout"}, status=504)
        except Exception as e:
            self.load_balancer.mark_unhealthy(service_name, endpoint.url)
            logger.error(f"代理请求失败: {target_url}, 错误: {e}")
            return web.json_response({"error": "Service unavailable"}, status=503)

    async def _health_handler(self, request: web.Request) -> web.Response:
        """健康检查处理器"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {},
        }

        # 检查各服务健康状态
        for service_name, endpoints in self.load_balancer.services.items():
            healthy_count = sum(1 for ep in endpoints if ep.is_healthy)
            total_count = len(endpoints)

            health_status["services"][service_name] = {
                "healthy_endpoints": healthy_count,
                "total_endpoints": total_count,
                "status": "healthy" if healthy_count > 0 else "unhealthy",
            }

        return web.json_response(health_status)

    async def _metrics_handler(self, request: web.Request) -> web.Response:
        """指标处理器"""
        metrics = await self.metrics_collector.get_metrics_summary()

        # 添加系统指标
        metrics["system"] = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage(" / ").percent,
        }

        return web.json_response(metrics)

    async def _health_check_loop(self) -> None:
        """健康检查循环"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(30)  # 每30秒检查一次
            except Exception as e:
                logger.error(f"健康检查失败: {e}")
                await asyncio.sleep(10)

    async def _perform_health_checks(self) -> None:
        """执行健康检查"""
        tasks = []

        for service_name, endpoints in self.load_balancer.services.items():
            for endpoint in endpoints:
                task = asyncio.create_task(
                    self._check_endpoint_health(service_name, endpoint)
                )
                tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_endpoint_health(
        self, service_name: str, endpoint: ServiceEndpoint
    ):
        """检查端点健康状态"""
        health_url = f"{endpoint.url}{endpoint.health_check_path}"

        try:
            async with self.client_session.get(
                health_url, timeout=ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    if not endpoint.is_healthy:
                        self.load_balancer.mark_healthy(service_name, endpoint.url)
                else:
                    self.load_balancer.mark_unhealthy(service_name, endpoint.url)

        except Exception:
            self.load_balancer.mark_unhealthy(service_name, endpoint.url)

        endpoint.last_health_check = datetime.now()

    async def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """启动服务器"""
        await self.initialize()

        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(runner, host, port)
        await site.start()

        logger.info(f"异步API网关启动成功: http: / /{host}:{port}")

        # 保持运行
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("正在关闭服务器...")
        finally:
            await self.shutdown()

    async def shutdown(self) -> None:
        """关闭网关"""
        logger.info("正在关闭异步API网关...")

        if self.client_session:
            await self.client_session.close()

        if self.redis_client:
            await self.redis_client.close()

        if self.db_pool:
            await self.db_pool.close()

        logger.info("异步API网关已关闭")


# 使用示例
async def main() -> None:
    """主函数"""
    gateway = OptimizedAsyncGateway(
        redis_url="redis: / /localhost:6379",
        database_url=None,  # 如果有数据库，提供连接字符串
        jwt_secret="your - secret - key",
    )

    await gateway.start_server(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    asyncio.run(main())
