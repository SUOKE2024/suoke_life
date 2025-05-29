"""
中间件
Middleware

提供请求处理中间件，包括日志、指标、安全等功能
"""

import time
import uuid
from typing import Callable

import structlog
from fastapi import Request, Response
from prometheus_client import Counter, Gauge, Histogram
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger(__name__)

# Prometheus 指标
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status_code"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

ACTIVE_REQUESTS = Gauge("http_requests_active", "Active HTTP requests")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """请求ID中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        为每个请求生成唯一ID

        Args:
            request: HTTP请求
            call_next: 下一个中间件或路由处理器

        Returns:
            HTTP响应
        """
        # 生成请求ID
        request_id = str(uuid.uuid4())

        # 将请求ID添加到请求状态
        request.state.request_id = request_id

        # 处理请求
        response = await call_next(request)

        # 将请求ID添加到响应头
        response.headers["X-Request-ID"] = request_id

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        记录请求和响应日志

        Args:
            request: HTTP请求
            call_next: 下一个中间件或路由处理器

        Returns:
            HTTP响应
        """
        start_time = time.time()

        # 获取请求ID
        request_id = getattr(request.state, "request_id", "unknown")

        # 记录请求开始
        logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )

        try:
            # 处理请求
            response = await call_next(request)

            # 计算处理时间
            process_time = time.time() - start_time

            # 记录请求完成
            logger.info(
                "Request completed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                process_time=process_time,
            )

            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            # 计算处理时间
            process_time = time.time() - start_time

            # 记录请求错误
            logger.error(
                "Request failed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                error=str(e),
                process_time=process_time,
            )

            raise


class MetricsMiddleware(BaseHTTPMiddleware):
    """指标中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        收集请求指标

        Args:
            request: HTTP请求
            call_next: 下一个中间件或路由处理器

        Returns:
            HTTP响应
        """
        start_time = time.time()

        # 增加活跃请求计数
        ACTIVE_REQUESTS.inc()

        try:
            # 处理请求
            response = await call_next(request)

            # 计算处理时间
            process_time = time.time() - start_time

            # 获取端点路径
            endpoint = request.url.path

            # 记录指标
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status_code=response.status_code,
            ).inc()

            REQUEST_DURATION.labels(method=request.method, endpoint=endpoint).observe(
                process_time
            )

            return response

        except Exception as e:
            # 记录错误指标
            REQUEST_COUNT.labels(
                method=request.method, endpoint=request.url.path, status_code=500
            ).inc()

            raise

        finally:
            # 减少活跃请求计数
            ACTIVE_REQUESTS.dec()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全头部中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        添加安全头部

        Args:
            request: HTTP请求
            call_next: 下一个中间件或路由处理器

        Returns:
            HTTP响应
        """
        response = await call_next(request)

        # 添加安全头部
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response
