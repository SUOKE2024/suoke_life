"""
中间件层
提供认证、限流、日志、监控等横切关注点功能
"""
import json
import logging
import time
from collections import defaultdict, deque
from typing import Any

import jwt
from fastapi import HTTPException, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint

from pkg.utils.connection_pool import get_pool_manager
from pkg.utils.error_handling import ErrorContext, get_error_handler
from pkg.utils.metrics import get_metrics_collector

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    def __init__(self, app, exclude_paths: list[str] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]
        self.metrics = get_metrics_collector()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 跳过特定路径
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # 记录请求开始时间
        start_time = time.time()
        request_id = request.headers.get("X-Request-ID", f"req_{int(start_time * 1000)}")

        # 记录请求信息
        logger.info(
            "请求开始",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host,
                "user_agent": request.headers.get("User-Agent", ""),
                "content_length": request.headers.get("Content-Length", 0)
            }
        )

        try:
            # 处理请求
            response = await call_next(request)

            # 计算处理时间
            process_time = time.time() - start_time

            # 记录响应信息
            logger.info(
                "请求完成",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time": process_time,
                    "response_size": response.headers.get("Content-Length", 0)
                }
            )

            # 记录指标
            self.metrics.histogram("request_duration", process_time, {
                "method": request.method,
                "endpoint": request.url.path,
                "status_code": str(response.status_code)
            })

            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            # 记录错误
            process_time = time.time() - start_time
            logger.error(
                "请求处理失败",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "process_time": process_time
                }
            )

            # 记录错误指标
            self.metrics.increment_counter("request_errors", {
                "method": request.method,
                "endpoint": request.url.path,
                "error_type": type(e).__name__
            })

            raise

class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件"""

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        burst_size: int = 10,
        exclude_paths: list[str] = None
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]

        # 使用滑动窗口算法
        self.request_windows: dict[str, deque] = defaultdict(deque)
        self.burst_counters: dict[str, int] = defaultdict(int)
        self.last_reset: dict[str, float] = defaultdict(float)

        self.metrics = get_metrics_collector()

    def _get_client_key(self, request: Request) -> str:
        """获取客户端标识"""
        # 优先使用用户ID，其次使用IP
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            return f"user:{user_id}"
        return f"ip:{request.client.host}"

    def _is_rate_limited(self, client_key: str) -> bool:
        """检查是否触发限流"""
        now = time.time()

        # 清理过期的请求记录
        window = self.request_windows[client_key]
        cutoff_time = now - 60  # 1分钟窗口

        while window and window[0] < cutoff_time:
            window.popleft()

        # 检查分钟级限流
        if len(window) >= self.requests_per_minute:
            return True

        # 检查突发限流
        last_reset_time = self.last_reset[client_key]
        if now - last_reset_time >= 1:  # 每秒重置突发计数器
            self.burst_counters[client_key] = 0
            self.last_reset[client_key] = now

        if self.burst_counters[client_key] >= self.burst_size:
            return True

        return False

    def _record_request(self, client_key: str) -> None:
        """记录请求"""
        now = time.time()
        self.request_windows[client_key].append(now)
        self.burst_counters[client_key] += 1

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 跳过特定路径
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        client_key = self._get_client_key(request)

        # 检查限流
        if self._is_rate_limited(client_key):
            logger.warning(f"客户端 {client_key} 触发限流")

            # 记录限流指标
            self.metrics.increment_counter("rate_limit_exceeded", {
                "client_type": client_key.split(":")[0],
                "endpoint": request.url.path
            })

            raise HTTPException(
                status_code=429,
                detail="请求过于频繁，请稍后再试",
                headers={"Retry-After": "60"}
            )

        # 记录请求
        self._record_request(client_key)

        return await call_next(request)

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """认证中间件"""

    def __init__(self, app, secret_key: str, exclude_paths: list[str] = None):
        super().__init__(app)
        self.secret_key = secret_key
        self.exclude_paths = exclude_paths or [
            "/health", "/metrics", "/docs", "/openapi.json"
        ]
        self.metrics = get_metrics_collector()

    def _extract_token(self, request: Request) -> str | None:
        """提取JWT令牌"""
        # 从Authorization头提取
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]

        # 从Cookie提取
        return request.cookies.get("access_token")

    def _verify_token(self, token: str) -> dict[str, Any] | None:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT令牌已过期")
            return None
        except jwt.InvalidTokenError:
            logger.warning("无效的JWT令牌")
            return None

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 跳过特定路径
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # 提取令牌
        token = self._extract_token(request)
        if not token:
            self.metrics.increment_counter("auth_failures", {"reason": "missing_token"})
            raise HTTPException(
                status_code=401,
                detail="缺少认证令牌",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # 验证令牌
        payload = self._verify_token(token)
        if not payload:
            self.metrics.increment_counter("auth_failures", {"reason": "invalid_token"})
            raise HTTPException(
                status_code=401,
                detail="无效的认证令牌",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # 将用户信息添加到请求状态
        request.state.user_id = payload.get("user_id")
        request.state.user_role = payload.get("role", "user")
        request.state.token_payload = payload

        # 记录认证成功指标
        self.metrics.increment_counter("auth_success", {
            "user_role": request.state.user_role
        })

        return await call_next(request)

class CacheMiddleware(BaseHTTPMiddleware):
    """缓存中间件"""

    def __init__(
        self,
        app,
        cache_ttl: int = 300,
        cacheable_methods: list[str] = None,
        cacheable_paths: list[str] = None
    ):
        super().__init__(app)
        self.cache_ttl = cache_ttl
        self.cacheable_methods = cacheable_methods or ["GET"]
        self.cacheable_paths = cacheable_paths or []

        # 获取Redis连接池
        pool_manager = get_pool_manager()
        self.cache = pool_manager.get_pool('redis')

        self.metrics = get_metrics_collector()

    def _generate_cache_key(self, request: Request) -> str:
        """生成缓存键"""
        # 包含路径、查询参数和用户ID
        user_id = getattr(request.state, 'user_id', 'anonymous')
        query_string = str(request.url.query) if request.url.query else ""

        import hashlib
        key_data = f"{request.url.path}:{query_string}:{user_id}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()

        return f"cache:response:{key_hash}"

    def _is_cacheable(self, request: Request) -> bool:
        """判断请求是否可缓存"""
        if request.method not in self.cacheable_methods:
            return False

        if self.cacheable_paths and request.url.path not in self.cacheable_paths:
            return False

        return True

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 检查是否可缓存
        if not self._is_cacheable(request):
            return await call_next(request)

        cache_key = self._generate_cache_key(request)

        try:
            # 尝试从缓存获取
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                cached_response = json.loads(cached_data)

                # 记录缓存命中
                self.metrics.increment_counter("cache_hits", {
                    "endpoint": request.url.path
                })

                # 构造响应
                response = Response(
                    content=cached_response["content"],
                    status_code=cached_response["status_code"],
                    headers=cached_response["headers"]
                )
                response.headers["X-Cache"] = "HIT"
                return response

        except Exception as e:
            logger.warning(f"缓存读取失败: {e}")

        # 缓存未命中，处理请求
        response = await call_next(request)

        # 记录缓存未命中
        self.metrics.increment_counter("cache_misses", {
            "endpoint": request.url.path
        })

        # 缓存响应（仅缓存成功响应）
        if response.status_code == 200:
            try:
                # 读取响应内容
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk

                # 构造缓存数据
                cache_data = {
                    "content": response_body.decode(),
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                }

                # 存储到缓存
                await self.cache.set(
                    cache_key,
                    json.dumps(cache_data),
                    ttl=self.cache_ttl
                )

                # 重新构造响应
                response = Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=response.headers
                )

            except Exception as e:
                logger.warning(f"缓存写入失败: {e}")

        response.headers["X-Cache"] = "MISS"
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """错误处理中间件"""

    def __init__(self, app):
        super().__init__(app)
        self.error_handler = get_error_handler()
        self.metrics = get_metrics_collector()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except HTTPException:
            # HTTP异常直接抛出，由FastAPI处理
            raise
        except Exception as e:
            # 创建错误上下文
            error_context = ErrorContext(
                user_id=getattr(request.state, 'user_id', None),
                request_id=request.headers.get("X-Request-ID"),
                operation=f"{request.method} {request.url.path}"
            )

            # 处理错误
            await self.error_handler.handle_error(e, error_context)

            # 记录错误指标
            self.metrics.increment_counter("unhandled_errors", {
                "error_type": type(e).__name__,
                "endpoint": request.url.path
            })

            # 返回通用错误响应
            return Response(
                content=json.dumps({
                    "error": "内部服务器错误",
                    "message": "服务暂时不可用，请稍后再试",
                    "request_id": error_context.request_id
                }),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )

def create_middleware_stack(app, config: dict[str, Any]):
    """创建中间件栈"""

    # 错误处理中间件（最外层）
    app.add_middleware(ErrorHandlingMiddleware)

    # 请求日志中间件
    app.add_middleware(RequestLoggingMiddleware)

    # 限流中间件
    rate_limit_config = config.get("rate_limit", {})
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=rate_limit_config.get("requests_per_minute", 60),
        burst_size=rate_limit_config.get("burst_size", 10)
    )

    # 认证中间件
    auth_config = config.get("auth", {})
    if auth_config.get("enabled", False):
        app.add_middleware(
            AuthenticationMiddleware,
            secret_key=auth_config.get("secret_key", "default-secret-key")
        )

    # 缓存中间件
    cache_config = config.get("cache_middleware", {})
    if cache_config.get("enabled", False):
        app.add_middleware(
            CacheMiddleware,
            cache_ttl=cache_config.get("ttl", 300),
            cacheable_paths=cache_config.get("cacheable_paths", [])
        )

    logger.info("中间件栈创建完成")
    return app
