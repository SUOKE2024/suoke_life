"""
日志中间件

记录所有HTTP请求和响应的详细信息。
"""

import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from xiaoke_service.core.logging import get_request_logger

logger = get_request_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并记录日志"""
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # 记录请求开始时间
        start_time = time.time()

        # 获取用户信息(如果有)
        user_id = getattr(request.state, "user_id", None)

        try:
            # 处理请求
            response = await call_next(request)

            # 计算处理时间
            duration = time.time() - start_time

            # 记录成功请求
            logger.log_request(
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                duration=duration,
                user_id=user_id,
                request_id=request_id,
                query_params=dict(request.query_params),
                user_agent=request.headers.get("user-agent"),
                client_ip=request.client.host if request.client else None,
            )

            # 添加请求ID到响应头
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # 计算处理时间
            duration = time.time() - start_time

            # 记录错误请求
            logger.log_error(
                method=request.method,
                path=str(request.url.path),
                error=e,
                user_id=user_id,
                request_id=request_id,
                duration=duration,
                query_params=dict(request.query_params),
                user_agent=request.headers.get("user-agent"),
                client_ip=request.client.host if request.client else None,
            )

            # 重新抛出异常
            raise
