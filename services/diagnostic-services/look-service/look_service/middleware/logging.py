from typing import Dict, List, Any, Optional, Union

"""
logging - 索克生活项目模块
"""

from ..core.logging import get_logger
from collections.abc import Awaitable, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid

"""Logging middleware for request / response logging."""




logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) - > Response:
        """Log request and response details.

        Args:
            request: HTTP request
            call_next: Next middleware / handler

        Returns:
            HTTP response
        """
        # Generate request ID
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Log request
        logger.info(
            "Request started",
            request_id = request_id,
            method = request.method,
            url = str(request.url),
            client_ip = request.client.host if request.client else "unknown",
            user_agent = request.headers.get("user - agent", "unknown"),
        )

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            "Request completed",
            request_id = request_id,
            method = request.method,
            url = str(request.url),
            status_code = response.status_code,
            duration = f"{duration:.3f}s",
        )

        # Add request ID to response headers
        response.headers["X - Request - ID"] = request_id

        return response
