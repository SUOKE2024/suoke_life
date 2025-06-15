"""日志中间件

记录所有HTTP请求和响应的详细信息，包括请求ID、处理时间、用户信息等。
"""

from collections.abc import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from xiaoke_service.core.logging import get_request_logger
import time
import uuid
from typing import Optional

logger = get_request_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件
    
    为每个请求生成唯一ID，记录详细的请求和响应信息，
    支持链路追踪和性能监控。
    """

    def __init__(self, app, exclude_paths: Optional[list[str]] = None):
        """初始化日志中间件
        
        Args:
            app: FastAPI应用实例
            exclude_paths: 排除记录的路径列表
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/metrics",
        ]

    def _should_log_request(self, path: str) -> bool:
        """判断是否应该记录请求
        
        Args:
            path: 请求路径
            
        Returns:
            是否应该记录
        """
        return not any(path.startswith(exclude_path) for exclude_path in self.exclude_paths)

    def _get_client_info(self, request: Request) -> dict:
        """获取客户端信息
        
        Args:
            request: HTTP请求对象
            
        Returns:
            客户端信息字典
        """
        return {
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "referer": request.headers.get("referer"),
            "x_forwarded_for": request.headers.get("x-forwarded-for"),
            "x_real_ip": request.headers.get("x-real-ip"),
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并记录日志
        
        Args:
            request: HTTP请求对象
            call_next: 下一个中间件或路由处理器
            
        Returns:
            HTTP响应对象
        """
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # 记录请求开始时间
        start_time = time.time()

        # 获取用户信息(如果有)
        user_id = getattr(request.state, "user_id", None)
        authenticated = getattr(request.state, "authenticated", False)

        # 获取客户端信息
        client_info = self._get_client_info(request)

        # 判断是否需要记录
        should_log = self._should_log_request(request.url.path)

        try:
            # 处理请求
            response = await call_next(request)

            # 计算处理时间
            duration = time.time() - start_time

            # 记录成功请求
            if should_log:
                logger.log_request(
                    method=request.method,
                    path=str(request.url.path),
                    status_code=response.status_code,
                    duration=duration,
                    user_id=user_id,
                    request_id=request_id,
                    query_params=dict(request.query_params),
                    authenticated=authenticated,
                    **client_info,
                )

            # 添加请求ID到响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{round(duration * 1000, 2)}ms"

            return response

        except Exception as e:
            # 计算处理时间
            duration = time.time() - start_time

            # 记录错误请求
            if should_log:
                logger.log_error(
                    method=request.method,
                    path=str(request.url.path),
                    error=e,
                    user_id=user_id,
                    request_id=request_id,
                    duration=duration,
                    query_params=dict(request.query_params),
                    authenticated=authenticated,
                    **client_info,
                )

            # 重新抛出异常
            raise