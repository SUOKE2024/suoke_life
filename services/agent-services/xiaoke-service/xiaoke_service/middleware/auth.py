"""
auth - 索克生活项目模块
"""

from collections.abc import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from xiaoke_service.core.logging import get_logger
import time

"""
认证中间件

处理用户认证和授权。
"""




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

        # 基础认证逻辑框架
        auth_header = request.headers.get("Authorization")
        api_key = request.headers.get("X-API-Key")

        # 初始化用户状态
        request.state.user_id = "anonymous"
        request.state.authenticated = False

        # 简单的认证检查
        if auth_header and auth_header.startswith("Bearer "):
            # 这里应该验证JWT token
            token = auth_header.split(" ")[1]
            if token:  # 简单验证, 实际应该解析JWT
                request.state.authenticated = True
                request.state.user_id = "authenticated_user"
        elif api_key:
            # 这里应该验证API Key
            if api_key:  # 简单验证, 实际应该查询数据库
                request.state.authenticated = True
                request.state.user_id = f"api_user_{api_key[:8]}"

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
