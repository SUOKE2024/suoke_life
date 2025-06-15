#!/usr/bin/env python3
"""
索克生活无障碍服务 - API网关

提供统一的API入口、路由、认证、限流、监控等功能。
"""

import asyncio
import hashlib
import json
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

try:
    import jwt

    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    jwt = None

import re

logger = logging.getLogger(__name__)


class HTTPMethod(Enum):
    """HTTP方法"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class AuthType(Enum):
    """认证类型"""

    NONE = "none"
    api_key = os.getenv("API_KEY", "")
    JWT = "jwt"
    OAUTH2 = "oauth2"
    BASIC = "basic"


class RateLimitType(Enum):
    """限流类型"""

    PER_SECOND = "per_second"
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"


@dataclass
class APIRequest:
    """API请求"""

    request_id: str
    method: HTTPMethod
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, Any]
    body: Any = None
    client_ip: str = ""
    user_agent: str = ""
    timestamp: float = field(default_factory=time.time)
    auth_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIResponse:
    """API响应"""

    request_id: str
    status_code: int
    headers: Dict[str, str]
    body: Any = None
    processing_time: float = 0.0
    error: Optional[str] = None
    cached: bool = False


@dataclass
class RouteConfig:
    """路由配置"""

    path_pattern: str
    methods: List[HTTPMethod]
    handler: Callable
    auth_required: bool = True
    auth_type: AuthType = AuthType.JWT
    rate_limit: Optional[Dict[str, Any]] = None
    cache_ttl: int = 0
    timeout: float = 30.0
    middleware: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RateLimitRule:
    """限流规则"""

    limit_type: RateLimitType
    max_requests: int
    window_size: int  # 时间窗口大小（秒）
    key_generator: Callable[[APIRequest], str] = None


class RateLimiter:
    """限流器"""

    def __init__(self, rules: List[RateLimitRule]):
        self.rules = rules
        self.request_counts: Dict[str, deque] = defaultdict(deque)
        self.lock = threading.Lock()

    def is_allowed(self, request: APIRequest) -> Tuple[bool, Dict[str, Any]]:
        """检查请求是否被允许"""
        current_time = time.time()

        with self.lock:
            for rule in self.rules:
                # 生成限流键
                if rule.key_generator:
                    key = rule.key_generator(request)
                else:
                    key = f"{request.client_ip}:{rule.limit_type.value}"

                # 获取请求记录
                requests = self.request_counts[key]

                # 清理过期记录
                while requests and current_time - requests[0] > rule.window_size:
                    requests.popleft()

                # 检查是否超过限制
                if len(requests) >= rule.max_requests:
                    return False, {
                        "rule": rule.limit_type.value,
                        "limit": rule.max_requests,
                        "window": rule.window_size,
                        "current": len(requests),
                        "reset_time": (
                            requests[0] + rule.window_size if requests else current_time
                        ),
                    }

                # 记录本次请求
                requests.append(current_time)

        return True, {}

    def get_stats(self) -> Dict[str, Any]:
        """获取限流统计"""
        with self.lock:
            return {
                "active_keys": len(self.request_counts),
                "total_requests": sum(
                    len(requests) for requests in self.request_counts.values()
                ),
                "rules_count": len(self.rules),
            }


class AuthenticationManager:
    """认证管理器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.jwt_secret = config.get("jwt_secret", "default_secret")
        self.jwt_algorithm = config.get("jwt_algorithm", "HS256")
        self.api_keys: Dict[str, Dict[str, Any]] = config.get("api_keys", {})

        # 认证缓存
        self.auth_cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
        self.cache_ttl = config.get("auth_cache_ttl", 300)  # 5分钟

    async def authenticate(
        self, request: APIRequest, auth_type: AuthType
    ) -> Tuple[bool, Dict[str, Any]]:
        """认证请求"""
        try:
            if auth_type == AuthType.NONE:
                return True, {}

            elif auth_type == AuthType.API_KEY:
                return await self._authenticate_api_key(request)

            elif auth_type == AuthType.JWT:
                return await self._authenticate_jwt(request)

            elif auth_type == AuthType.BASIC:
                return await self._authenticate_basic(request)

            else:
                return False, {"error": f"不支持的认证类型: {auth_type.value}"}

        except Exception as e:
            logger.error(f"认证失败: {e}")
            return False, {"error": str(e)}

    async def _authenticate_api_key(
        self, request: APIRequest
    ) -> Tuple[bool, Dict[str, Any]]:
        """API Key认证"""
        api_key = request.headers.get("X-API-Key") or request.query_params.get(
            "api_key"
        )

        if not api_key:
            return False, {"error": "缺少API Key"}

        # 检查缓存
        cache_key = f"api_key:{api_key}"
        if cache_key in self.auth_cache:
            auth_info, timestamp = self.auth_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return True, auth_info

        # 验证API Key
        if api_key in self.api_keys:
            auth_info = self.api_keys[api_key].copy()
            auth_info["auth_type"] = "api_key"

            # 缓存认证结果
            self.auth_cache[cache_key] = (auth_info, time.time())

            return True, auth_info

        return False, {"error": "无效的API Key"}

    async def _authenticate_jwt(
        self, request: APIRequest
    ) -> Tuple[bool, Dict[str, Any]]:
        """JWT认证"""
        if not JWT_AVAILABLE:
            return False, {"error": "JWT库未安装"}

        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return False, {"error": "缺少Bearer Token"}

        token = auth_header[7:]  # 移除 "Bearer " 前缀

        # 检查缓存
        cache_key = f"jwt:{hashlib.sha256(token.encode()).hexdigest()}"
        if cache_key in self.auth_cache:
            auth_info, timestamp = self.auth_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return True, auth_info

        try:
            # 验证JWT
            payload = jwt.decode(
                token, self.jwt_secret, algorithms=[self.jwt_algorithm]
            )

            auth_info = {
                "auth_type": "jwt",
                "user_id": payload.get("user_id"),
                "username": payload.get("username"),
                "roles": payload.get("roles", []),
                "exp": payload.get("exp"),
                "iat": payload.get("iat"),
            }

            # 缓存认证结果
            self.auth_cache[cache_key] = (auth_info, time.time())

            return True, auth_info

        except Exception as e:
            if "ExpiredSignatureError" in str(type(e)):
                return False, {"error": "Token已过期"}
            else:
                return False, {"error": "无效的Token"}

    async def _authenticate_basic(
        self, request: APIRequest
    ) -> Tuple[bool, Dict[str, Any]]:
        """Basic认证"""
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Basic "):
            return False, {"error": "缺少Basic认证"}

        # 这里应该实现Basic认证逻辑
        # 为了演示，直接返回成功
        return True, {"auth_type": "basic", "user": "basic_user"}

    def clear_cache(self) -> None:
        """清理认证缓存"""
        current_time = time.time()
        expired_keys = [
            key
            for key, (_, timestamp) in self.auth_cache.items()
            if current_time - timestamp > self.cache_ttl
        ]

        for key in expired_keys:
            del self.auth_cache[key]

    def get_stats(self) -> Dict[str, Any]:
        """获取认证统计"""
        return {
            "cache_size": len(self.auth_cache),
            "api_keys_count": len(self.api_keys),
            "cache_ttl": self.cache_ttl,
        }


class ResponseCache:
    """响应缓存"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, Tuple[APIResponse, float]] = {}
        self.access_order: deque = deque()
        self.hit_count = 0
        self.miss_count = 0
        self.lock = threading.Lock()

    def _generate_cache_key(self, request: APIRequest) -> str:
        """生成缓存键"""
        # 基于请求方法、路径、查询参数和认证信息生成键
        key_data = {
            "method": request.method.value,
            "path": request.path,
            "query": request.query_params,
            "user_id": request.auth_info.get("user_id", "anonymous"),
        }

        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()

    def get(self, request: APIRequest, ttl: int) -> Optional[APIResponse]:
        """获取缓存的响应"""
        if ttl <= 0:
            return None

        cache_key = self._generate_cache_key(request)

        with self.lock:
            if cache_key in self.cache:
                response, timestamp = self.cache[cache_key]

                # 检查是否过期
                if time.time() - timestamp <= ttl:
                    # 更新访问顺序
                    if cache_key in self.access_order:
                        self.access_order.remove(cache_key)
                    self.access_order.append(cache_key)

                    self.hit_count += 1

                    # 创建新的响应对象，标记为缓存命中
                    cached_response = APIResponse(
                        request_id=request.request_id,
                        status_code=response.status_code,
                        headers=response.headers.copy(),
                        body=response.body,
                        processing_time=0.0,
                        cached=True,
                    )

                    return cached_response
                else:
                    # 删除过期项
                    del self.cache[cache_key]
                    if cache_key in self.access_order:
                        self.access_order.remove(cache_key)

            self.miss_count += 1
            return None

    def put(self, request: APIRequest, response: APIResponse, ttl: int):
        """缓存响应"""
        if ttl <= 0 or response.status_code >= 400:
            return

        cache_key = self._generate_cache_key(request)

        with self.lock:
            # 如果缓存已满，删除最旧的项
            if len(self.cache) >= self.max_size and cache_key not in self.cache:
                if self.access_order:
                    oldest_key = self.access_order.popleft()
                    if oldest_key in self.cache:
                        del self.cache[oldest_key]

            # 添加新项
            self.cache[cache_key] = (response, time.time())

            # 更新访问顺序
            if cache_key in self.access_order:
                self.access_order.remove(cache_key)
            self.access_order.append(cache_key)

    def clear(self) -> None:
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0

        return {
            "cache_size": len(self.cache),
            "max_size": self.max_size,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate_percent": hit_rate,
        }


class Router:
    """路由器"""

    def __init__(self) -> None:
        self.routes: List[RouteConfig] = []
        self.compiled_patterns: List[Tuple[re.Pattern, RouteConfig]] = []

    def add_route(self, route: RouteConfig):
        """添加路由"""
        self.routes.append(route)

        # 编译路径模式
        pattern = self._compile_path_pattern(route.path_pattern)
        self.compiled_patterns.append((pattern, route))

        logger.debug(f"添加路由: {route.methods} {route.path_pattern}")

    def _compile_path_pattern(self, pattern: str) -> re.Pattern:
        """编译路径模式"""
        # 将路径参数转换为正则表达式
        # 例如: /users/{user_id} -> /users/(?P<user_id>[^/]+)
        regex_pattern = pattern

        # 替换路径参数
        regex_pattern = re.sub(r"\{(\w+)\}", r"(?P<\1>[^/]+)", regex_pattern)

        # 确保完全匹配
        regex_pattern = f"^{regex_pattern}$"

        return re.compile(regex_pattern)

    def find_route(
        self, method: HTTPMethod, path: str
    ) -> Tuple[Optional[RouteConfig], Dict[str, str]]:
        """查找匹配的路由"""
        for pattern, route in self.compiled_patterns:
            if method in route.methods:
                match = pattern.match(path)
                if match:
                    path_params = match.groupdict()
                    return route, path_params

        return None, {}

    def get_routes_info(self) -> List[Dict[str, Any]]:
        """获取路由信息"""
        return [
            {
                "path_pattern": route.path_pattern,
                "methods": [m.value for m in route.methods],
                "auth_required": route.auth_required,
                "auth_type": route.auth_type.value,
                "cache_ttl": route.cache_ttl,
                "timeout": route.timeout,
            }
            for route in self.routes
        ]


class Middleware:
    """中间件基类"""

    async def process_request(self, request: APIRequest) -> Optional[APIResponse]:
        """处理请求（在路由处理之前）"""
        return None

    async def process_response(
        self, request: APIRequest, response: APIResponse
    ) -> APIResponse:
        """处理响应（在路由处理之后）"""
        return response


class LoggingMiddleware(Middleware):
    """日志中间件"""

    async def process_request(self, request: APIRequest) -> Optional[APIResponse]:
        logger.info(
            f"API请求: {request.method.value} {request.path} - {request.client_ip}"
        )
        return None

    async def process_response(
        self, request: APIRequest, response: APIResponse
    ) -> APIResponse:
        logger.info(
            f"API响应: {request.request_id} - {response.status_code} - "
            f"{response.processing_time:.3f}s - 缓存: {response.cached}"
        )
        return response


class CORSMiddleware(Middleware):
    """CORS中间件"""

    def __init__(
        self, allowed_origins: List[str] = None, allowed_methods: List[str] = None
    ):
        self.allowed_origins = allowed_origins or ["*"]
        self.allowed_methods = allowed_methods or [
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "OPTIONS",
        ]

    async def process_response(
        self, request: APIRequest, response: APIResponse
    ) -> APIResponse:
        # 添加CORS头
        response.headers.update(
            {
                "Access-Control-Allow-Origin": (
                    "*"
                    if "*" in self.allowed_origins
                    else ",".join(self.allowed_origins)
                ),
                "Access-Control-Allow-Methods": ",".join(self.allowed_methods),
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-API-Key",
                "Access-Control-Max-Age": "86400",
            }
        )

        return response


class APIGateway:
    """API网关"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.router = Router()
        self.auth_manager = AuthenticationManager(config.get("auth", {}))
        self.rate_limiter = None
        self.response_cache = ResponseCache(config.get("cache_size", 1000))

        # 中间件
        self.middleware: List[Middleware] = [
            LoggingMiddleware(),
            CORSMiddleware(
                allowed_origins=config.get("cors", {}).get("allowed_origins", ["*"]),
                allowed_methods=config.get("cors", {}).get(
                    "allowed_methods", ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
                ),
            ),
        ]

        # 统计信息
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "auth_failures": 0,
            "rate_limit_hits": 0,
            "cache_hits": 0,
            "total_processing_time": 0.0,
        }

        # 初始化限流器
        self._initialize_rate_limiter()

        logger.info("API网关初始化完成")

    def _initialize_rate_limiter(self) -> None:
        """初始化限流器"""
        rate_limit_config = self.config.get("rate_limit", {})
        if rate_limit_config.get("enabled", False):
            rules = []

            # 添加默认限流规则
            if "per_minute" in rate_limit_config:
                rules.append(
                    RateLimitRule(
                        limit_type=RateLimitType.PER_MINUTE,
                        max_requests=rate_limit_config["per_minute"],
                        window_size=60,
                    )
                )

            if "per_hour" in rate_limit_config:
                rules.append(
                    RateLimitRule(
                        limit_type=RateLimitType.PER_HOUR,
                        max_requests=rate_limit_config["per_hour"],
                        window_size=3600,
                    )
                )

            if rules:
                self.rate_limiter = RateLimiter(rules)

    def add_route(self, route: RouteConfig):
        """添加路由"""
        self.router.add_route(route)

    def add_middleware(self, middleware: Middleware):
        """添加中间件"""
        self.middleware.append(middleware)

    async def handle_request(self, request: APIRequest) -> APIResponse:
        """处理API请求"""
        start_time = time.time()
        self.stats["total_requests"] += 1

        try:
            # 执行请求中间件
            for middleware in self.middleware:
                early_response = await middleware.process_request(request)
                if early_response:
                    return early_response

            # 处理OPTIONS请求
            if request.method == HTTPMethod.OPTIONS:
                response = APIResponse(
                    request_id=request.request_id,
                    status_code=200,
                    headers={},
                    body=None,
                )
                return await self._process_response_middleware(request, response)

            # 查找路由
            route, path_params = self.router.find_route(request.method, request.path)
            if not route:
                response = APIResponse(
                    request_id=request.request_id,
                    status_code=404,
                    headers={},
                    error="路由未找到",
                )
                return await self._process_response_middleware(request, response)

            # 限流检查
            if self.rate_limiter:
                allowed, limit_info = self.rate_limiter.is_allowed(request)
                if not allowed:
                    self.stats["rate_limit_hits"] += 1
                    response = APIResponse(
                        request_id=request.request_id,
                        status_code=429,
                        headers={
                            "X-RateLimit-Limit": str(limit_info["limit"]),
                            "X-RateLimit-Remaining": "0",
                            "X-RateLimit-Reset": str(int(limit_info["reset_time"])),
                        },
                        error="请求频率超限",
                    )
                    return await self._process_response_middleware(request, response)

            # 认证检查
            if route.auth_required:
                auth_success, auth_info = await self.auth_manager.authenticate(
                    request, route.auth_type
                )
                if not auth_success:
                    self.stats["auth_failures"] += 1
                    response = APIResponse(
                        request_id=request.request_id,
                        status_code=401,
                        headers={},
                        error=auth_info.get("error", "认证失败"),
                    )
                    return await self._process_response_middleware(request, response)

                request.auth_info = auth_info

            # 检查缓存
            if route.cache_ttl > 0:
                cached_response = self.response_cache.get(request, route.cache_ttl)
                if cached_response:
                    self.stats["cache_hits"] += 1
                    cached_response.request_id = request.request_id
                    return await self._process_response_middleware(
                        request, cached_response
                    )

            # 执行路由处理器
            try:
                # 设置超时
                handler_task = asyncio.create_task(route.handler(request, path_params))
                response_body = await asyncio.wait_for(
                    handler_task, timeout=route.timeout
                )

                response = APIResponse(
                    request_id=request.request_id,
                    status_code=200,
                    headers={"Content-Type": "application/json"},
                    body=response_body,
                    processing_time=time.time() - start_time,
                )

                # 缓存响应
                if route.cache_ttl > 0:
                    self.response_cache.put(request, response, route.cache_ttl)

                self.stats["successful_requests"] += 1

            except asyncio.TimeoutError:
                response = APIResponse(
                    request_id=request.request_id,
                    status_code=504,
                    headers={},
                    error="请求超时",
                )
            except Exception as e:
                logger.error(f"路由处理器错误: {e}")
                response = APIResponse(
                    request_id=request.request_id,
                    status_code=500,
                    headers={},
                    error="内部服务器错误",
                )

            return await self._process_response_middleware(request, response)

        except Exception as e:
            logger.error(f"API网关处理错误: {e}")
            self.stats["failed_requests"] += 1

            response = APIResponse(
                request_id=request.request_id,
                status_code=500,
                headers={},
                error="网关内部错误",
            )

            return await self._process_response_middleware(request, response)

        finally:
            processing_time = time.time() - start_time
            self.stats["total_processing_time"] += processing_time

    async def _process_response_middleware(
        self, request: APIRequest, response: APIResponse
    ) -> APIResponse:
        """执行响应中间件"""
        for middleware in reversed(self.middleware):
            response = await middleware.process_response(request, response)

        return response

    def get_stats(self) -> Dict[str, Any]:
        """获取网关统计信息"""
        avg_processing_time = self.stats["total_processing_time"] / max(
            self.stats["total_requests"], 1
        )

        success_rate = (
            self.stats["successful_requests"]
            / max(self.stats["total_requests"], 1)
            * 100
        )

        return {
            **self.stats,
            "avg_processing_time": avg_processing_time,
            "success_rate_percent": success_rate,
            "routes_count": len(self.router.routes),
            "middleware_count": len(self.middleware),
            "auth_stats": self.auth_manager.get_stats(),
            "cache_stats": self.response_cache.get_stats(),
            "rate_limiter_stats": (
                self.rate_limiter.get_stats() if self.rate_limiter else {}
            ),
        }

    def get_routes_info(self) -> List[Dict[str, Any]]:
        """获取路由信息"""
        return self.router.get_routes_info()

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        issues = []

        # 检查成功率
        if self.stats["total_requests"] > 0:
            success_rate = (
                self.stats["successful_requests"] / self.stats["total_requests"] * 100
            )
            if success_rate < 95:
                issues.append(f"API成功率过低: {success_rate:.1f}%")

        # 检查认证失败率
        if self.stats["total_requests"] > 0:
            auth_failure_rate = (
                self.stats["auth_failures"] / self.stats["total_requests"] * 100
            )
            if auth_failure_rate > 10:
                issues.append(f"认证失败率过高: {auth_failure_rate:.1f}%")

        # 检查限流命中率
        if self.stats["total_requests"] > 0:
            rate_limit_rate = (
                self.stats["rate_limit_hits"] / self.stats["total_requests"] * 100
            )
            if rate_limit_rate > 5:
                issues.append(f"限流命中率过高: {rate_limit_rate:.1f}%")

        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "total_requests": self.stats["total_requests"],
            "success_rate": self.stats["successful_requests"]
            / max(self.stats["total_requests"], 1)
            * 100,
            "routes_count": len(self.router.routes),
        }


# 全局API网关实例
api_gateway = None


def get_api_gateway(config: Dict[str, Any] = None) -> APIGateway:
    """获取API网关实例"""
    global api_gateway
    if api_gateway is None:
        api_gateway = APIGateway(config or {})
    return api_gateway


# 示例路由处理器
async def get_health_handler(
    request: APIRequest, path_params: Dict[str, str]
) -> Dict[str, Any]:
    """健康检查处理器"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    }


async def get_user_handler(
    request: APIRequest, path_params: Dict[str, str]
) -> Dict[str, Any]:
    """获取用户信息处理器"""
    user_id = path_params.get("user_id")

    # 模拟用户数据
    return {
        "user_id": user_id,
        "username": f"user_{user_id}",
        "email": f"user_{user_id}@example.com",
        "created_at": datetime.now().isoformat(),
    }


# 示例配置
EXAMPLE_CONFIG = {
    "auth": {
        "jwt_secret": "your_jwt_secret_key",
        "jwt_algorithm": "HS256",
        "auth_cache_ttl": 300,
        "api_keys": {
            "test_key_123": {
                "name": "测试应用",
                "permissions": ["read", "write"],
                "created_at": "2024-01-01T00:00:00Z",
            }
        },
    },
    "rate_limit": {"enabled": True, "per_minute": 100, "per_hour": 1000},
    "cors": {
        "allowed_origins": ["*"],
        "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    },
    "cache_size": 1000,
}


def initialize_api_gateway(config: Dict[str, Any]) -> APIGateway:
    """初始化API网关"""
    gateway = get_api_gateway(config)

    # 添加示例路由
    gateway.add_route(
        RouteConfig(
            path_pattern="/health",
            methods=[HTTPMethod.GET],
            handler=get_health_handler,
            auth_required=False,
            cache_ttl=60,
        )
    )

    gateway.add_route(
        RouteConfig(
            path_pattern="/api/v1/users/{user_id}",
            methods=[HTTPMethod.GET],
            handler=get_user_handler,
            auth_required=True,
            auth_type=AuthType.JWT,
            cache_ttl=300,
        )
    )

    logger.info("API网关初始化完成")
    return gateway


if __name__ == "__main__":
    # 测试代码
    async def test_api_gateway() -> None:
        gateway = initialize_api_gateway(EXAMPLE_CONFIG)

        # 测试健康检查请求
        request = APIRequest(
            request_id="test_001",
            method=HTTPMethod.GET,
            path="/health",
            headers={},
            query_params={},
            client_ip="127.0.0.1",
        )

        response = await gateway.handle_request(request)
        print(f"健康检查响应: {response}")

        # 获取统计信息
        stats = gateway.get_stats()
        print(f"网关统计: {stats}")

    asyncio.run(test_api_gateway())
