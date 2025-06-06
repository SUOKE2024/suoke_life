"""
api_gateway - 索克生活项目模块
"""

        import random
from ..config.settings import get_settings
from ..database.manager import get_cache_manager
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List, Optional, Callable
import asyncio
import hashlib
import httpx
import json
import jwt
import logging
import redis.asyncio as redis
import time

"""
API网关

提供统一的API入口、路由分发、负载均衡、认证授权、
限流、监控等功能，支持五诊服务的统一访问。
"""



logger = logging.getLogger(__name__)

@dataclass
class ServiceEndpoint:
    """服务端点配置"""
    name: str
    host: str
    port: int
    health_check_path: str = "/health"
    weight: int = 1
    max_connections: int = 100
    timeout: int = 30
    is_healthy: bool = True
    last_health_check: Optional[datetime] = None

@dataclass
class RouteConfig:
    """路由配置"""
    path: str
    service_name: str
    methods: List[str] = field(default_factory=lambda: ["GET", "POST"])
    auth_required: bool = True
    rate_limit: int = 100  # 每分钟请求数
    timeout: int = 30
    retry_count: int = 3
    circuit_breaker: bool = True

@dataclass
class RateLimitConfig:
    """限流配置"""
    requests_per_minute: int = 100
    requests_per_hour: int = 1000
    burst_size: int = 10
    window_size: int = 60  # 秒

class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
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
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
                return True
            return False
        elif self.state == "HALF_OPEN":
            return True
        return False
    
    def record_success(self):
        """记录成功"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """记录失败"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
    
    def _should_attempt_reset(self) -> bool:
        """是否应该尝试重置"""
        if self.last_failure_time is None:
            return True
        
        return (datetime.utcnow() - self.last_failure_time).seconds >= self.recovery_timeout

class RateLimiter:
    """限流器"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
    
    async def is_allowed(self, key: str, config: RateLimitConfig) -> bool:
        """检查是否允许请求"""
        try:
            current_time = int(time.time())
            window_start = current_time - config.window_size
            
            # 使用滑动窗口算法
            pipe = self.redis_client.pipeline()
            
            # 移除过期的请求记录
            pipe.zremrangebyscore(key, 0, window_start)
            
            # 获取当前窗口内的请求数
            pipe.zcard(key)
            
            # 添加当前请求
            pipe.zadd(key, {str(current_time): current_time})
            
            # 设置过期时间
            pipe.expire(key, config.window_size)
            
            results = await pipe.execute()
            current_requests = results[1]
            
            return current_requests < config.requests_per_minute
            
        except Exception as e:
            logger.error(f"限流检查失败: {e}")
            return True  # 失败时允许请求

class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self):
        self.services: Dict[str, List[ServiceEndpoint]] = {}
        self.current_index: Dict[str, int] = {}
    
    def add_service(self, service_name: str, endpoint: ServiceEndpoint):
        """添加服务端点"""
        if service_name not in self.services:
            self.services[service_name] = []
            self.current_index[service_name] = 0
        
        self.services[service_name].append(endpoint)
    
    def get_endpoint(self, service_name: str) -> Optional[ServiceEndpoint]:
        """获取服务端点（轮询算法）"""
        if service_name not in self.services:
            return None
        
        endpoints = [ep for ep in self.services[service_name] if ep.is_healthy]
        if not endpoints:
            return None
        
        # 轮询选择
        index = self.current_index[service_name] % len(endpoints)
        self.current_index[service_name] = (index + 1) % len(endpoints)
        
        return endpoints[index]
    
    def get_weighted_endpoint(self, service_name: str) -> Optional[ServiceEndpoint]:
        """获取服务端点（加权轮询算法）"""
        if service_name not in self.services:
            return None
        
        endpoints = [ep for ep in self.services[service_name] if ep.is_healthy]
        if not endpoints:
            return None
        
        # 计算总权重
        total_weight = sum(ep.weight for ep in endpoints)
        if total_weight == 0:
            return endpoints[0]
        
        # 加权选择
        weight_sum = 0
        random_weight = random.randint(1, total_weight)
        
        for endpoint in endpoints:
            weight_sum += endpoint.weight
            if random_weight <= weight_sum:
                return endpoint
        
        return endpoints[0]

class HealthChecker:
    """健康检查器"""
    
    def __init__(self, load_balancer: LoadBalancer):
        self.load_balancer = load_balancer
        self.check_interval = 30  # 秒
        self.timeout = 5
        self._running = False
    
    async def start(self):
        """启动健康检查"""
        self._running = True
        while self._running:
            await self._check_all_services()
            await asyncio.sleep(self.check_interval)
    
    def stop(self):
        """停止健康检查"""
        self._running = False
    
    async def _check_all_services(self):
        """检查所有服务健康状态"""
        for service_name, endpoints in self.load_balancer.services.items():
            for endpoint in endpoints:
                await self._check_endpoint_health(endpoint)
    
    async def _check_endpoint_health(self, endpoint: ServiceEndpoint):
        """检查单个端点健康状态"""
        try:
            url = f"http://{endpoint.host}:{endpoint.port}{endpoint.health_check_path}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    endpoint.is_healthy = True
                    logger.debug(f"服务健康: {endpoint.name}")
                else:
                    endpoint.is_healthy = False
                    logger.warning(f"服务不健康: {endpoint.name}, 状态码: {response.status_code}")
                
                endpoint.last_health_check = datetime.utcnow()
                
        except Exception as e:
            endpoint.is_healthy = False
            endpoint.last_health_check = datetime.utcnow()
            logger.error(f"健康检查失败: {endpoint.name}, 错误: {e}")

class AuthManager:
    """认证管理器"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.token_expiration = 3600  # 秒
    
    def create_token(self, user_data: Dict[str, Any]) -> str:
        """创建JWT令牌"""
        payload = {
            **user_data,
            "exp": datetime.utcnow() + timedelta(seconds=self.token_expiration),
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("令牌已过期")
            return None
        except jwt.InvalidTokenError:
            logger.warning("无效令牌")
            return None

class APIGateway:
    """API网关"""
    
    def __init__(self):
        self.settings = get_settings()
        self.app = FastAPI(
            title="五诊服务API网关",
            description="中医五诊服务统一API入口",
            version="1.0.0"
        )
        
        # 核心组件
        self.load_balancer = LoadBalancer()
        self.health_checker = HealthChecker(self.load_balancer)
        self.auth_manager = AuthManager(self.settings.security.secret_key)
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.rate_limiter = None
        
        # 路由配置
        self.routes: Dict[str, RouteConfig] = {}
        
        # HTTP客户端
        self.http_client = None
        
        # 初始化
        self._setup_middleware()
        self._setup_routes()
    
    async def initialize(self):
        """初始化网关"""
        # 初始化Redis连接
        cache_manager = await get_cache_manager()
        self.rate_limiter = RateLimiter(cache_manager.redis_client)
        
        # 初始化HTTP客户端
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )
        
        # 配置服务端点
        await self._configure_services()
        
        # 启动健康检查
        asyncio.create_task(self.health_checker.start())
        
        logger.info("API网关初始化完成")
    
    def _setup_middleware(self):
        """设置中间件"""
        # CORS中间件
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.settings.api.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Gzip压缩中间件
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # 自定义中间件
        @self.app.middleware("http")
        async def gateway_middleware(request: Request, call_next):
            start_time = time.time()
            
            # 请求ID
            request_id = hashlib.md5(
                f"{time.time()}{request.client.host}".encode()
            ).hexdigest()[:8]
            
            # 添加请求头
            request.state.request_id = request_id
            
            try:
                response = await call_next(request)
                
                # 添加响应头
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Gateway-Version"] = "1.0.0"
                
                # 记录访问日志
                process_time = time.time() - start_time
                logger.info(
                    f"请求处理完成: {request.method} {request.url.path} "
                    f"状态码: {response.status_code} 耗时: {process_time:.3f}s"
                )
                
                return response
                
            except Exception as e:
                logger.error(f"请求处理失败: {e}")
                raise
    
    def _setup_routes(self):
        """设置路由"""
        # 健康检查
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "services": {
                    name: [
                        {
                            "name": ep.name,
                            "healthy": ep.is_healthy,
                            "last_check": ep.last_health_check.isoformat() if ep.last_health_check else None
                        }
                        for ep in endpoints
                    ]
                    for name, endpoints in self.load_balancer.services.items()
                }
            }
        
        # 认证端点
        @self.app.post("/auth/login")
        async def login(credentials: Dict[str, str]):
            # 这里应该验证用户凭据
            # 简化实现，实际应该连接用户服务
            username = credentials.get("username")
            password = credentials.get("password")
            
            if username and password:
                token = self.auth_manager.create_token({
                    "username": username,
                    "role": "doctor"  # 实际应该从数据库获取
                })
                return {"access_token": token, "token_type": "bearer"}
            
            raise HTTPException(status_code=401, detail="认证失败")
        
        # 代理路由
        @self.app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
        async def proxy_request(
            service_name: str,
            path: str,
            request: Request,
            credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
        ):
            return await self._handle_proxy_request(service_name, path, request, credentials)
    
    async def _configure_services(self):
        """配置服务端点"""
        # 五诊服务配置
        services_config = {
            "look": [
                ServiceEndpoint("look-service-1", "localhost", 8001),
                ServiceEndpoint("look-service-2", "localhost", 8002)
            ],
            "listen": [
                ServiceEndpoint("listen-service-1", "localhost", 8003),
                ServiceEndpoint("listen-service-2", "localhost", 8004)
            ],
            "inquiry": [
                ServiceEndpoint("inquiry-service-1", "localhost", 8005),
                ServiceEndpoint("inquiry-service-2", "localhost", 8006)
            ],
            "palpation": [
                ServiceEndpoint("palpation-service-1", "localhost", 8007),
                ServiceEndpoint("palpation-service-2", "localhost", 8008)
            ],
            "calculation": [
                ServiceEndpoint("calculation-service-1", "localhost", 8009),
                ServiceEndpoint("calculation-service-2", "localhost", 8010)
            ]
        }
        
        # 添加服务端点
        for service_name, endpoints in services_config.items():
            for endpoint in endpoints:
                self.load_balancer.add_service(service_name, endpoint)
        
        # 配置路由
        route_configs = [
            RouteConfig("/look", "look", ["GET", "POST"], True, 50),
            RouteConfig("/listen", "listen", ["GET", "POST"], True, 50),
            RouteConfig("/inquiry", "inquiry", ["GET", "POST"], True, 100),
            RouteConfig("/palpation", "palpation", ["GET", "POST"], True, 30),
            RouteConfig("/calculation", "calculation", ["GET", "POST"], True, 80),
        ]
        
        for route_config in route_configs:
            self.routes[route_config.service_name] = route_config
            # 初始化熔断器
            self.circuit_breakers[route_config.service_name] = CircuitBreaker()
    
    async def _handle_proxy_request(
        self,
        service_name: str,
        path: str,
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials]
    ) -> Response:
        """处理代理请求"""
        # 获取路由配置
        route_config = self.routes.get(service_name)
        if not route_config:
            raise HTTPException(status_code=404, detail="服务不存在")
        
        # 认证检查
        if route_config.auth_required:
            if not credentials:
                raise HTTPException(status_code=401, detail="需要认证")
            
            user_data = self.auth_manager.verify_token(credentials.credentials)
            if not user_data:
                raise HTTPException(status_code=401, detail="认证失败")
            
            request.state.user = user_data
        
        # 限流检查
        client_ip = request.client.host
        rate_limit_key = f"rate_limit:{service_name}:{client_ip}"
        rate_limit_config = RateLimitConfig(requests_per_minute=route_config.rate_limit)
        
        if not await self.rate_limiter.is_allowed(rate_limit_key, rate_limit_config):
            raise HTTPException(status_code=429, detail="请求过于频繁")
        
        # 熔断器检查
        circuit_breaker = self.circuit_breakers[service_name]
        if not circuit_breaker.can_execute():
            raise HTTPException(status_code=503, detail="服务暂时不可用")
        
        # 获取服务端点
        endpoint = self.load_balancer.get_weighted_endpoint(service_name)
        if not endpoint:
            raise HTTPException(status_code=503, detail="服务不可用")
        
        # 构建目标URL
        target_url = f"http://{endpoint.host}:{endpoint.port}/{path}"
        
        # 准备请求数据
        headers = dict(request.headers)
        headers.pop("host", None)  # 移除原始host头
        
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
        
        # 发送请求
        try:
            async with self.http_client as client:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=body,
                    params=dict(request.query_params),
                    timeout=route_config.timeout
                )
                
                # 记录成功
                circuit_breaker.record_success()
                
                # 构建响应
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.headers.get("content-type")
                )
                
        except Exception as e:
            # 记录失败
            circuit_breaker.record_failure()
            logger.error(f"代理请求失败: {e}")
            raise HTTPException(status_code=502, detail="网关错误")
    
    async def shutdown(self):
        """关闭网关"""
        self.health_checker.stop()
        
        if self.http_client:
            await self.http_client.aclose()
        
        logger.info("API网关已关闭")

# 全局网关实例
_gateway = None

async def get_api_gateway() -> APIGateway:
    """获取API网关实例"""
    global _gateway
    if _gateway is None:
        _gateway = APIGateway()
        await _gateway.initialize()
    return _gateway

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    gateway = await get_api_gateway()
    yield
    # 关闭
    await gateway.shutdown()

def create_gateway_app() -> FastAPI:
    """创建网关应用"""
    gateway = APIGateway()
    gateway.app.router.lifespan_context = lifespan
    return gateway.app 