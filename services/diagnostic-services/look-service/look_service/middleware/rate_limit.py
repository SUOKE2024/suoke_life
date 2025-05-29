"""Rate limiting middleware."""

import time
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.logging import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware."""

    def __init__(
        self,
        app: Any,
        requests_per_minute: int = 60,
        burst_size: int = 10,
    ) -> None:
        """Initialize rate limiter.

        Args:
            app: ASGI application
            requests_per_minute: Maximum requests per minute
            burst_size: Maximum burst requests
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.clients: dict[str, dict[str, float]] = {}

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier.

        Args:
            request: HTTP request

        Returns:
            Client identifier
        """
        # Use IP address as client ID
        if request.client:
            return request.client.host
        return "unknown"

    def _is_rate_limited(self, client_id: str) -> bool:
        """Check if client is rate limited.

        Args:
            client_id: Client identifier

        Returns:
            True if rate limited
        """
        now = time.time()

        # Initialize client data if not exists
        if client_id not in self.clients:
            self.clients[client_id] = {
                "requests": 0,
                "window_start": now,
                "last_request": now,
            }

        client_data = self.clients[client_id]

        # Reset window if needed (sliding window)
        if now - client_data["window_start"] >= 60:  # 1 minute
            client_data["requests"] = 0
            client_data["window_start"] = now

        # Check burst limit
        if (
            now - client_data["last_request"] < 1
            and client_data["requests"] >= self.burst_size
        ):  # Less than 1 second and over burst limit
            return True

        # Check rate limit
        if client_data["requests"] >= self.requests_per_minute:
            return True

        # Update client data
        client_data["requests"] += 1
        client_data["last_request"] = now

        return False

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request with rate limiting.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/ready", "/metrics"]:
            return await call_next(request)

        client_id = self._get_client_id(request)

        if self._is_rate_limited(client_id):
            logger.warning(
                "Rate limit exceeded",
                client_id=client_id,
                path=request.url.path,
                method=request.method,
            )

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests",
                        "details": {
                            "limit": self.requests_per_minute,
                            "window": "1 minute",
                        },
                    }
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)

        # Add rate limit headers
        client_data = self.clients.get(client_id, {})
        remaining = max(0, self.requests_per_minute - client_data.get("requests", 0))

        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response
