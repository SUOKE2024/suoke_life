"""
rate_limiter - 索克生活项目模块
"""

import logging
import time
from collections import defaultdict, deque
from collections.abc import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

"""
限流中间件

防止API滥用
"""


logger = logging.getLogger(__name__)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """限流中间件"""

    def __init__(
        self,
        app,
        max_requests: int = 100,
        window_seconds: int = 60,
        enabled: bool = True,
        exclude_paths: list | None = None,
    ):
        """
        初始化限流中间件

        Args:
            app: FastAPI应用实例
            max_requests: 时间窗口内最大请求数
            window_seconds: 时间窗口大小（秒）
            enabled: 是否启用限流
            exclude_paths: 排除的路径列表
        """
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.enabled = enabled
        self.exclude_paths = exclude_paths or [
            "/ping",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

        # 使用滑动窗口算法
        self.request_history: dict[str, deque] = defaultdict(deque)

    def _get_client_id(self, request: Request) -> str:
        """获取客户端标识"""
        # 优先使用真实IP
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            real_ip = request.headers.get("x-real-ip")
            if real_ip:
                client_ip = real_ip
            elif hasattr(request, "client") and request.client:
                client_ip = request.client.host
            else:
                client_ip = "unknown"

        # 可以根据需要添加用户ID等其他标识
        # user_id = request.headers.get("x-user-id")
        # if user_id:
        #     return f"user:{user_id}"

        return f"ip:{client_ip}"

    async def _is_rate_limited(self, client_id: str) -> bool:
        """检查是否触发限流"""
        current_time = time.time()
        window_start = current_time - self.window_seconds

        # 获取客户端请求历史
        request_times = self.request_history[client_id]

        # 清理过期的请求记录
        while request_times and request_times[0] < window_start:
            request_times.popleft()

        # 检查是否超过限制
        return len(request_times) >= self.max_requests

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求限流"""
        if not self.enabled:
            return await call_next(request)

        # 检查是否为排除路径
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # 获取客户端标识
        client_id = self._get_client_id(request)

        # 检查限流
        if await self._is_rate_limited(client_id):
            return await self._create_rate_limit_response(request, client_id)

        # 记录请求
        await self._record_request(client_id)

        # 继续处理请求
        response = await call_next(request)

        # 添加限流信息到响应头
        await self._add_rate_limit_headers(response, client_id)

        return response

    async def _record_request(self, client_id: str) -> None:
        """记录请求"""
        current_time = time.time()
        self.request_history[client_id].append(current_time)

    async def _create_rate_limit_response(
        self, request: Request, client_id: str
    ) -> JSONResponse:
        """创建限流响应"""
        request_id = getattr(request.state, "request_id", "unknown")

        # 计算重试时间
        request_times = self.request_history[client_id]
        if request_times:
            oldest_request = request_times[0]
            retry_after = int(oldest_request + self.window_seconds - time.time()) + 1
        else:
            retry_after = self.window_seconds

        logger.warning(
            f"限流触发: {client_id} - {request.method} {request.url.path}",
            extra={
                "client_id": client_id,
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "current_requests": len(request_times),
                "max_requests": self.max_requests,
                "window_seconds": self.window_seconds,
            },
        )

        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": {
                    "code": 429,
                    "message": f"请求过于频繁，请在 {retry_after} 秒后重试",
                    "type": "rate_limit_exceeded",
                },
                "rate_limit": {
                    "max_requests": self.max_requests,
                    "window_seconds": self.window_seconds,
                    "current_requests": len(request_times),
                    "retry_after": retry_after,
                },
                "request_id": request_id,
                "path": request.url.path,
            },
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(self.max_requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time()) + retry_after),
            },
        )

    async def _add_rate_limit_headers(self, response: Response, client_id: str) -> None:
        """添加限流信息到响应头"""
        request_times = self.request_history[client_id]
        remaining = max(0, self.max_requests - len(request_times))

        # 计算重置时间
        if request_times:
            oldest_request = request_times[0]
            reset_time = int(oldest_request + self.window_seconds)
        else:
            reset_time = int(time.time() + self.window_seconds)

        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        response.headers["X-RateLimit-Window"] = str(self.window_seconds)

    async def get_client_stats(self, client_id: str) -> dict:
        """获取客户端统计信息"""
        current_time = time.time()
        window_start = current_time - self.window_seconds

        request_times = self.request_history[client_id]

        # 清理过期记录
        while request_times and request_times[0] < window_start:
            request_times.popleft()

        return {
            "client_id": client_id,
            "current_requests": len(request_times),
            "max_requests": self.max_requests,
            "remaining_requests": max(0, self.max_requests - len(request_times)),
            "window_seconds": self.window_seconds,
            "is_rate_limited": len(request_times) >= self.max_requests,
        }

    async def clear_client_history(self, client_id: str) -> bool:
        """清理客户端请求历史"""
        if client_id in self.request_history:
            del self.request_history[client_id]
            logger.info(f"已清理客户端 {client_id} 的请求历史")
            return True
        return False

    async def get_all_stats(self) -> dict:
        """获取所有客户端统计信息"""
        current_time = time.time()
        window_start = current_time - self.window_seconds

        stats = {
            "total_clients": len(self.request_history),
            "rate_limit_config": {
                "max_requests": self.max_requests,
                "window_seconds": self.window_seconds,
                "enabled": self.enabled,
            },
            "clients": [],
        }

        for client_id, request_times in self.request_history.items():
            # 清理过期记录
            while request_times and request_times[0] < window_start:
                request_times.popleft()

            if request_times:  # 只包含有活跃请求的客户端
                client_stats = {
                    "client_id": client_id,
                    "current_requests": len(request_times),
                    "remaining_requests": max(
                        0, self.max_requests - len(request_times)
                    ),
                    "is_rate_limited": len(request_times) >= self.max_requests,
                }
                stats["clients"].append(client_stats)

        return stats

    async def cleanup_expired_records(self) -> int:
        """清理过期的请求记录"""
        current_time = time.time()
        window_start = current_time - self.window_seconds
        cleaned_clients = 0

        # 清理过期记录
        clients_to_remove = []
        for client_id, request_times in self.request_history.items():
            while request_times and request_times[0] < window_start:
                request_times.popleft()

            # 如果客户端没有活跃请求，标记为删除
            if not request_times:
                clients_to_remove.append(client_id)

        # 删除空的客户端记录
        for client_id in clients_to_remove:
            del self.request_history[client_id]
            cleaned_clients += 1

        if cleaned_clients > 0:
            logger.debug(f"清理了 {cleaned_clients} 个过期的客户端记录")

        return cleaned_clients


class AdaptiveRateLimiter:
    """自适应限流器"""

    def __init__(
        self, base_limit: int = 100, max_limit: int = 1000, min_limit: int = 10
    ):
        """
        初始化自适应限流器

        Args:
            base_limit: 基础限制
            max_limit: 最大限制
            min_limit: 最小限制
        """
        self.base_limit = base_limit
        self.max_limit = max_limit
        self.min_limit = min_limit
        self.current_limit = base_limit
        self.error_count = 0
        self.success_count = 0
        self.last_adjustment = time.time()

    def record_success(self):
        """记录成功请求"""
        self.success_count += 1
        self._maybe_adjust_limit()

    def record_error(self):
        """记录错误请求"""
        self.error_count += 1
        self._maybe_adjust_limit()

    def _maybe_adjust_limit(self):
        """可能调整限制"""
        now = time.time()
        if now - self.last_adjustment < 60:  # 每分钟最多调整一次
            return

        total_requests = self.success_count + self.error_count
        if total_requests < 10:  # 样本太少
            return

        error_rate = self.error_count / total_requests

        if error_rate > 0.1:  # 错误率超过10%，降低限制
            self.current_limit = max(self.min_limit, int(self.current_limit * 0.8))
            logger.info(
                f"由于错误率过高({error_rate:.2%})，降低限流至 {self.current_limit}"
            )
        elif error_rate < 0.01:  # 错误率低于1%，提高限制
            self.current_limit = min(self.max_limit, int(self.current_limit * 1.2))
            logger.info(
                f"由于错误率较低({error_rate:.2%})，提高限流至 {self.current_limit}"
            )

        # 重置计数器
        self.success_count = 0
        self.error_count = 0
        self.last_adjustment = now

    def get_current_limit(self) -> int:
        """获取当前限制"""
        return self.current_limit
