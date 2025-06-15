from typing import Dict, List, Any, Optional, Union

"""
security - 索克生活项目模块
"""

from ..core.logging import get_logger
from collections.abc import Awaitable, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

"""Security middleware for HTTP security headers."""




logger = get_logger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) - > Response:
        """Add security headers to response.

        Args:
            request: HTTP request
            call_next: Next middleware / handler

        Returns:
            HTTP response with security headers
        """
        response = await call_next(request)

        # Security headers
        security_headers = {
            "X - Content - Type - Options": "nosniff",
            "X - Frame - Options": "DENY",
            "X - XSS - Protection": "1; mode = block",
            "Strict - Transport - Security": "max - age = 31536000; includeSubDomains",
            "Referrer - Policy": "strict - origin - when - cross - origin",
            "Content - Security - Policy": (
                "default - src 'self'; "
                "script - src 'self' 'unsafe - inline'; "
                "style - src 'self' 'unsafe - inline'; "
                "img - src 'self' data: https:; "
                "font - src 'self'; "
                "connect - src 'self'; "
                "frame - ancestors 'none';"
            ),
            "Permissions - Policy": (
                "geolocation = (), "
                "microphone = (), "
                "camera = (), "
                "payment = (), "
                "usb = (), "
                "magnetometer = (), "
                "accelerometer = (), "
                "gyroscope = ()"
            ),
        }

        # Add headers to response
        for header, value in security_headers.items():
            response.headers[header] = value

        # Remove server header for security
        if "server" in response.headers:
            del response.headers["server"]

        logger.debug(
            "Security headers added",
            path = request.url.path,
            method = request.method,
            headers_count = len(security_headers),
        )

        return response
