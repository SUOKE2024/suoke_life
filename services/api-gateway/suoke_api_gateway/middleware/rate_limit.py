from typing import Any, Dict, List, Optional, Union

"""
rate_limit - 索克生活项目模块
"""

import time

from fastapi import Request, Response, status
from limits import RateLimitItemPerSecond, parse
from limits.storage import RedisStorage
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.config import get_settings
from ..core.logging import get_logger, log_security_event

"""
限流中间件

基于 Redis 的分布式限流实现，支持多种限流策略。
"""




logger = get_logger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件"""

    def __init__(self, app, settings = None):
"""TODO: 添加文档字符串"""
super().__init__(app)
self.settings = settings or get_settings()
self.rate_limit_config = self.settings.rate_limit

# 初始化 Redis 存储
self.redis_client = None
self.storage = None

# 不限流的路径
self.skip_paths = {
            " / health",
            " / health / ready",
            " / health / live",
            " / metrics",
}

# 解析默认限流规则
self.default_limit = parse(self.rate_limit_config.default_rate)

    async def dispatch(self, request: Request, call_next):
"""处理请求"""
if not self.rate_limit_config.enabled:
            return await call_next(request)

# 跳过不需要限流的路径
if request.url.path in self.skip_paths:
            return await call_next(request)

# 初始化存储（延迟初始化）
if self.storage is None:
            await self._init_storage()

# 获取限流键
rate_limit_key = self._get_rate_limit_key(request)

# 获取适用的限流规则
limit = self._get_applicable_limit(request)

try:
            # 检查限流
            if not await self._check_rate_limit(rate_limit_key, limit):
                # 记录限流事件
                log_security_event(
                    event_type = "rate_limit_exceeded",
                    user_id = getattr(request.state, "user_id", None),
                    ip_address = self._get_client_ip(request),
                    path = request.url.path,
                    method = request.method,
                    rate_limit_key = rate_limit_key,
                )

                return self._create_rate_limit_response()

            # 继续处理请求
            response = await call_next(request)

            # 添加限流信息到响应头
            remaining = await self._get_remaining_requests(rate_limit_key, limit)
            response.headers["X - RateLimit - Limit"] = str(limit.amount)
            response.headers["X - RateLimit - Remaining"] = str(remaining)
            response.headers["X - RateLimit - Reset"] = str(int(time.time()) + limit.per)

            return response

except Exception as e:
            logger.error(
                "Rate limiting error",
                error = str(e),
                rate_limit_key = rate_limit_key,
                path = request.url.path,
                exc_info = True,
            )
            # 限流失败时允许请求通过
            return await call_next(request)

    async def _init_storage(self) -> None:
"""初始化 Redis 存储"""
try:
            self.redis_client = redis.from_url(
                self.rate_limit_config.storage_url,
                decode_responses = True,
            )
            # 测试连接
            await self.redis_client.ping()
            self.storage = RedisStorage(self.rate_limit_config.storage_url)
            logger.info("Rate limiting storage initialized")
except Exception as e:
            logger.error("Failed to initialize rate limiting storage", error = str(e))
            raise

    def _get_rate_limit_key(self, request: Request) -> str:
"""获取限流键"""
# 优先使用用户ID
user_id = getattr(request.state, "user_id", None)
if user_id:
            return f"user:{user_id}"

# 回退到IP地址
client_ip = self._get_client_ip(request)
return f"ip:{client_ip}"

    def _get_applicable_limit(self, request: Request) -> RateLimitItemPerSecond:
"""获取适用的限流规则"""
# 这里可以根据路径、用户角色等实现不同的限流策略
path = request.url.path

# API 路径的特殊限流规则
if path.startswith(" / api / v1 / auth"):
            # 认证接口更严格的限流
            return parse("10 / minute")
elif path.startswith(" / api / v1 / upload"):
            # 上传接口的限流
            return parse("5 / minute")

# 用户角色限流（如果有用户信息）
user_roles = getattr(request.state, "user_roles", [])
if "premium" in user_roles:
            return parse("1000 / minute")
elif "admin" in user_roles:
            return parse("10000 / minute")

# 默认限流规则
return self.default_limit

    async def _check_rate_limit(self, key: str, limit: RateLimitItemPerSecond) -> bool:
"""检查是否超过限流"""
try:
            # 使用滑动窗口算法
            current_time = int(time.time())
            window_start = current_time - limit.per

            # 清理过期的记录
            await self.redis_client.zremrangebyscore(key, 0, window_start)

            # 获取当前窗口内的请求数
            current_requests = await self.redis_client.zcard(key)

            if current_requests >=limit.amount:
                return False

            # 记录当前请求
            await self.redis_client.zadd(key, {str(current_time): current_time})

            # 设置过期时间
            await self.redis_client.expire(key, limit.per)

            return True

except Exception as e:
            logger.error("Rate limit check failed", error = str(e), key = key)
            # 出错时允许请求通过
            return True

    async def _get_remaining_requests(self, key: str, limit: RateLimitItemPerSecond) -> int:
"""获取剩余请求数"""
try:
            current_requests = await self.redis_client.zcard(key)
            return max(0, limit.amount - current_requests)
except Exception:
            return limit.amount

    def _get_client_ip(self, request: Request) -> str:
"""获取客户端IP地址"""
# 检查代理头
forwarded_for = request.headers.get("X - Forwarded - For")
if forwarded_for:
            return forwarded_for.split(",")[0].strip()

real_ip = request.headers.get("X - Real - IP")
if real_ip:
            return real_ip

# 回退到直接连接IP
if hasattr(request, "client") and request.client:
            return request.client.host

return "unknown"

    def _create_rate_limit_response(self) -> Response:
"""创建限流响应"""
return Response(
            content = '{"error": "Rate limit exceeded", "message": "Too many requests"}',
            status_code = status.HTTP_429_TOO_MANY_REQUESTS,
            headers = {
                "Content - Type": "application / json",
                "Retry - After": "60",
            },
)
