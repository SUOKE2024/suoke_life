"""
logging - 索克生活项目模块
"""

import time
import uuid
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

"""日志中间件"""


logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求日志"""
        # 生成请求ID
        request_id = str(uuid.uuid4())

        # 记录请求开始时间
        start_time = time.time()

        # 获取客户端信息
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user - agent", "")

        # 绑定请求上下文
        bound_logger = logger.bind(
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_ip=client_ip,
            user_agent=user_agent,
        )

        # 将请求ID添加到请求状态
        request.state.request_id = request_id
        request.state.logger = bound_logger

        # 记录请求开始
        bound_logger.info("请求开始")

        try:
            # 处理请求
            response = await call_next(request)

            # 计算处理时间
            process_time = time.time() - start_time

            # 记录请求完成
            bound_logger.info(
                "请求完成",
                status_code=response.status_code,
                process_time=f"{process_time:.3f}s",
            )

            # 添加响应头
            response.headers["X - Request - ID"] = request_id
            response.headers["X - Process - Time"] = f"{process_time:.3f}"

            return response

        except Exception as e:
            # 计算处理时间
            process_time = time.time() - start_time

            # 记录请求异常
            bound_logger.error(
                "请求异常",
                error=str(e),
                error_type=type(e).__name__,
                process_time=f"{process_time:.3f}s",
            )

            raise

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 检查代理头部
        forwarded_for = request.headers.get("x - forwarded - for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x - real - ip")
        if real_ip:
            return real_ip

        # 返回直接连接的IP
        if request.client:
            return request.client.host

        return "unknown"
