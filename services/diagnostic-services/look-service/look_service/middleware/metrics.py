from typing import Dict, List, Any, Optional, Union

"""
metrics - 索克生活项目模块
"""

from ..core.logging import get_logger
from collections.abc import Awaitable, Callable
from fastapi import Request, Response
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
import contextlib
import time

"""Metrics middleware for Prometheus monitoring."""




logger = get_logger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

REQUEST_SIZE = Histogram(
    "http_request_size_bytes",
    "HTTP request size in bytes",
    ["method", "endpoint"],
)

RESPONSE_SIZE = Histogram(
    "http_response_size_bytes",
    "HTTP response size in bytes",
    ["method", "endpoint"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) - > Response:
        """Process request and collect metrics."""
        start_time = time.time()
        method = request.method
        path = request.url.path

        # Get request size
        request_size = 0
        if hasattr(request, "body"):
            with contextlib.suppress(Exception):
                body = await request.body()
                request_size = len(body)

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Get response size
        response_size = 0
        if hasattr(response, "body"):
            with contextlib.suppress(Exception):
                response_size = len(response.body)

        # Record metrics
        REQUEST_COUNT.labels(
            method = method,
            endpoint = path,
            status_code = response.status_code,
        ).inc()

        REQUEST_DURATION.labels(
            method = method,
            endpoint = path,
        ).observe(duration)

        REQUEST_SIZE.labels(
            method = method,
            endpoint = path,
        ).observe(request_size)

        RESPONSE_SIZE.labels(
            method = method,
            endpoint = path,
        ).observe(response_size)

        logger.debug(
            "Request processed",
            method = method,
            path = path,
            status_code = response.status_code,
            duration = duration,
            request_size = request_size,
            response_size = response_size,
        )

        return response
