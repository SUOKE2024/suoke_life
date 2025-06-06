"""
middleware - 索克生活项目模块
"""

            from fastapi import HTTPException
from collections.abc import Awaitable, Callable
from fastapi import Request, Response
from laoke_service.core.logging import get_logger
from prometheus_client import Counter, Gauge, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Any
import time

"""
API 中间件模块

提供日志记录、指标收集、错误处理等中间件
"""




# Prometheus 指标
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'http_active_connections',
    'Number of active HTTP connections'
)

ERROR_COUNT = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'error_type']
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志记录中间件"""

    def __init__(self, app: Any, logger_name: str = "laoke.api") -> None:
        super().__init__(app)
        self.logger = get_logger(logger_name)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """处理请求并记录日志"""
        start_time = time.time()

        # 记录请求开始
        self.logger.info(
            "HTTP request started",
            method=request.method,
            path=str(request.url.path),
            query_params=str(request.url.query) if request.url.query else None,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )

        try:
            # 处理请求
            response = await call_next(request)  # type: ignore[return-value]

            # 计算处理时间
            duration = time.time() - start_time

            # 记录请求完成
            self.logger.info(
                "HTTP request completed",
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2)
            )

            return response

        except Exception as e:
            # 计算处理时间
            duration = time.time() - start_time

            # 记录请求错误
            self.logger.error(
                "HTTP request failed",
                method=request.method,
                path=str(request.url.path),
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration * 1000, 2)
            )

            raise


class MetricsMiddleware(BaseHTTPMiddleware):
    """指标收集中间件"""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """收集请求指标"""
        start_time = time.time()
        method = request.method
        path = str(request.url.path)

        # 增加活跃连接数
        ACTIVE_CONNECTIONS.inc()

        try:
            # 处理请求
            response = await call_next(request)  # type: ignore[return-value]

            # 计算处理时间
            duration = time.time() - start_time

            # 记录指标
            REQUEST_COUNT.labels(
                method=method,
                endpoint=path,
                status_code=response.status_code
            ).inc()

            REQUEST_DURATION.labels(
                method=method,
                endpoint=path
            ).observe(duration)

            return response

        except Exception as e:
            # 记录错误指标
            ERROR_COUNT.labels(
                method=method,
                endpoint=path,
                error_type=type(e).__name__
            ).inc()

            raise

        finally:
            # 减少活跃连接数
            ACTIVE_CONNECTIONS.dec()


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """错误处理中间件"""

    def __init__(self, app: Any, logger_name: str = "laoke.error") -> None:
        super().__init__(app)
        self.logger = get_logger(logger_name)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """处理未捕获的异常"""
        try:
            return await call_next(request)  # type: ignore[return-value]

        except Exception as e:
            # 记录未处理的异常
            self.logger.error(
                "Unhandled exception in request processing",
                method=request.method,
                path=str(request.url.path),
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )

            # 重新抛出异常，让 FastAPI 的异常处理器处理
            raise


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """添加安全头部"""
        response = await call_next(request)  # type: ignore[return-value]

        # 添加安全头部
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """速率限制中间件（简单实现）"""

    def __init__(self, app: Any, requests_per_minute: int = 60) -> None:
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts: dict[tuple[str, int], int] = {}
        self.logger = get_logger("laoke.ratelimit")

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """检查速率限制"""
        client_ip = request.client.host if request.client else "unknown"
        current_time = int(time.time() / 60)  # 当前分钟

        # 清理过期的计数
        self.request_counts = {
            key: count for key, count in self.request_counts.items()
            if key[1] >= current_time - 1
        }

        # 检查当前客户端的请求数
        key = (client_ip, current_time)
        current_count = self.request_counts.get(key, 0)

        if current_count >= self.requests_per_minute:
            self.logger.warning(
                "Rate limit exceeded",
                client_ip=client_ip,
                requests_per_minute=self.requests_per_minute,
                current_count=current_count
            )

            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )

        # 增加请求计数
        self.request_counts[key] = current_count + 1

        return await call_next(request)  # type: ignore[return-value]


async def cors_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """CORS中间件"""
    # 处理预检请求
    if request.method == "OPTIONS":
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response

    # 处理实际请求
    response = await call_next(request)  # type: ignore[return-value]
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response
