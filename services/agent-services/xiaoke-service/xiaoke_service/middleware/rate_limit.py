"""限流中间件

基于用户或IP地址的请求限流，支持滑动窗口算法和灵活的限流策略。
"""

from collections import defaultdict
from collections.abc import Callable
from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from xiaoke_service.core.config import settings
from xiaoke_service.core.logging import get_logger
from xiaoke_service.core.exceptions import RateLimitError
import time
from typing import Optional

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件
    
    使用滑动窗口算法实现请求限流，
    支持基于用户ID和IP地址的限流策略。
    """

    def __init__(self, app, skip_paths: Optional[list[str]] = None):
        """初始化限流中间件
        
        Args:
            app: FastAPI应用实例
            skip_paths: 跳过限流的路径列表
        """
        super().__init__(app)
        # 存储每个客户端的请求记录
        self.requests = defaultdict(list)
        self.max_requests = settings.service.rate_limit_requests
        self.window_seconds = settings.service.rate_limit_window
        self.skip_paths = skip_paths or [
            "/health",
            "/ready",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    def _get_client_key(self, request: Request) -> str:
        """获取客户端标识
        
        Args:
            request: HTTP请求对象
            
        Returns:
            客户端唯一标识
        """
        # 优先使用用户ID，否则使用IP地址
        user_id = getattr(request.state, "user_id", None)
        if user_id and user_id != "anonymous":
            return f"user:{user_id}"

        # 获取真实IP地址
        client_ip = (
            request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or request.headers.get("x-real-ip")
            or (request.client.host if request.client else "unknown")
        )
        return f"ip:{client_ip}"

    def _cleanup_expired_requests(self, client_key: str, now: float) -> None:
        """清理过期的请求记录
        
        Args:
            client_key: 客户端标识
            now: 当前时间戳
        """
        self.requests[client_key] = [
            req_time
            for req_time in self.requests[client_key]
            if now - req_time < self.window_seconds
        ]

    def _is_rate_limited(self, client_key: str) -> tuple[bool, int]:
        """检查是否超过限流
        
        Args:
            client_key: 客户端标识
            
        Returns:
            (是否超过限制, 剩余请求数)
        """
        now = time.time()

        # 清理过期的请求记录
        self._cleanup_expired_requests(client_key, now)

        # 检查是否超过限制
        current_requests = len(self.requests[client_key])
        remaining = max(0, self.max_requests - current_requests)

        if current_requests >= self.max_requests:
            return True, 0

        # 记录当前请求
        self.requests[client_key].append(now)
        return False, remaining - 1

    def _get_retry_after(self, client_key: str) -> int:
        """获取重试等待时间
        
        Args:
            client_key: 客户端标识
            
        Returns:
            重试等待秒数
        """
        if not self.requests[client_key]:
            return self.window_seconds

        # 计算最早请求的过期时间
        oldest_request = min(self.requests[client_key])
        retry_after = int(oldest_request + self.window_seconds - time.time())
        return max(1, retry_after)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求限流
        
        Args:
            request: HTTP请求对象
            call_next: 下一个中间件或路由处理器
            
        Returns:
            HTTP响应对象
            
        Raises:
            RateLimitError: 当超过限流时抛出
        """
        # 跳过不需要限流的路径
        if any(request.url.path.startswith(path) for path in self.skip_paths):
            return await call_next(request)

        # 获取客户端标识
        client_key = self._get_client_key(request)

        # 检查限流
        is_limited, remaining = self._is_rate_limited(client_key)

        if is_limited:
            retry_after = self._get_retry_after(client_key)
            
            logger.warning(
                "超过限流限制",
                client_key=client_key,
                path=request.url.path,
                method=request.method,
                max_requests=self.max_requests,
                window_seconds=self.window_seconds,
                retry_after=retry_after,
            )

            raise RateLimitError(
                f"超过限流限制。最大 {self.max_requests} 次请求每 {self.window_seconds} 秒。",
                details={
                    "max_requests": self.max_requests,
                    "window_seconds": self.window_seconds,
                    "retry_after": retry_after,
                    "client_key": client_key,
                }
            )

        # 处理请求
        response = await call_next(request)

        # 添加限流信息到响应头
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            int(time.time() + self.window_seconds)
        )
        response.headers["X-RateLimit-Window"] = str(self.window_seconds)

        return response