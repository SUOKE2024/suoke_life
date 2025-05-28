"""
认证中间件

处理用户认证和授权。
"""

import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from xiaoke_service.core.logging import get_logger

logger = get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件"""

    def __init__(self, app, skip_paths: list[str] | None = None):
        super().__init__(app)
        self.skip_paths = skip_paths or [
            "/health",
            "/ready",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        start_time = time.time()

        # 跳过不需要认证的路径
        if any(request.url.path.startswith(path) for path in self.skip_paths):
            response = await call_next(request)
            return response

        # TODO: 实现实际的认证逻辑
        # 这里可以添加 JWT 验证、API Key 验证等

        # 添加用户信息到请求状态
        request.state.user_id = "anonymous"
        request.state.authenticated = False

        try:
            response = await call_next(request)

            # 记录认证信息
            duration = time.time() - start_time
            logger.info(
                "Authentication processed",
                path=request.url.path,
                method=request.method,
                user_id=request.state.user_id,
                authenticated=request.state.authenticated,
                duration_ms=round(duration * 1000, 2),
            )

            return response

        except Exception as e:
            logger.error(
                "Authentication error",
                path=request.url.path,
                method=request.method,
                error=str(e),
            )
            raise
