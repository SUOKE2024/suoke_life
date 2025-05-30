"""
限流中间件

基于用户或IP地址的请求限流。
"""

import time
from collections import defaultdict
from collections.abc import Callable

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from xiaoke_service.core.config import settings
from xiaoke_service.core.logging import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件"""

    def __init__(self, app):
        super().__init__(app)
        # 存储每个客户端的请求记录
        self.requests = defaultdict(list)
        self.max_requests = settings.service.rate_limit_requests
        self.window_seconds = settings.service.rate_limit_window

    def _get_client_key(self, request: Request) -> str:
        """获取客户端标识"""
        # 优先使用用户ID, 否则使用IP地址
        user_id = getattr(request.state, "user_id", None)
        if user_id and user_id != "anonymous":
            return f"user:{user_id}"

        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

    def _is_rate_limited(self, client_key: str) -> bool:
        """检查是否超过限流"""
        now = time.time()

        # 清理过期的请求记录
        self.requests[client_key] = [
            req_time
            for req_time in self.requests[client_key]
            if now - req_time < self.window_seconds
        ]

        # 检查是否超过限制
        if len(self.requests[client_key]) >= self.max_requests:
            return True

        # 记录当前请求
        self.requests[client_key].append(now)
        return False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        # 跳过健康检查等路径
        skip_paths = ["/health", "/ready", "/metrics"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)

        # 获取客户端标识
        client_key = self._get_client_key(request)

        # 检查限流
        if self._is_rate_limited(client_key):
            logger.warning(
                "Rate limit exceeded",
                client_key=client_key,
                path=request.url.path,
                method=request.method,
                max_requests=self.max_requests,
                window_seconds=self.window_seconds,
            )

            raise HTTPException(
                status_code=429,
                detail={
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Rate limit exceeded. Maximum {self.max_requests} requests per {self.window_seconds} seconds.",
                    "retry_after": self.window_seconds,
                },
            )

        # 处理请求
        response = await call_next(request)

        # 添加限流信息到响应头
        remaining = max(0, self.max_requests - len(self.requests[client_key]))
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            int(time.time() + self.window_seconds)
        )

        return response
