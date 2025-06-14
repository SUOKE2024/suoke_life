#!/usr/bin/env python3
"""
索克生活 API 网关日志记录中间件

记录请求响应信息、性能指标等。
"""

from ..core.logging import get_logger, log_request_response
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, List, Any, Optional, Union
import time
import uuid

logger=get_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """日志记录中间件"""

    def __init__(self, app, settings=None):
        """TODO: 添加文档字符串"""
        super().__init__(app)
        self.settings=settings

        # 不记录日志的路径
        self.skip_paths={
            "/health",
            "/health/ready",
            "/health/live",
            "/metrics",
        }

    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        # 生成请求ID
        request_id=str(uuid.uuid4())
        request.state.request_id=request_id

        # 记录请求开始时间
        start_time=time.time()

        # 获取请求信息
        method=request.method
        url=str(request.url)
        path=request.url.path
        client_ip=self._get_client_ip(request)
        user_agent=request.headers.get("User-Agent", "")
        user_id=getattr(request.state, "user_id", None)

        # 记录请求开始
        if path not in self.skip_paths:
            logger.info(
                "Request started",
                request_id=request_id,
                method=method,
                path=path,
                client_ip=client_ip,
                user_agent=user_agent,
                user_id=user_id,
            )

        # 处理请求
        try:
            response=await call_next(request)

            # 计算处理时间
            process_time=time.time()-start_time

            # 添加响应头
            response.headers["X-Request-ID"]=request_id
            response.headers["X-Process-Time"]=f"{process_time:.4f}"

            # 记录请求完成
            if path not in self.skip_paths:
                log_request_response(
                    method=method,
                    url=url,
                    status_code=response.status_code,
                    response_time=process_time,
                    request_size=self._get_request_size(request),
                    response_size=self._get_response_size(response),
                    user_id=user_id,
                    request_id=request_id,
                    client_ip=client_ip,
                )

            return response

        except Exception as e:
            # 计算处理时间
            process_time=time.time()-start_time

            # 记录错误
            logger.error(
                "Request failed",
                request_id=request_id,
                method=method,
                path=path,
                error=str(e),
                process_time=process_time,
                client_ip=client_ip,
                user_id=user_id,
                exc_info=True,
            )

            # 重新抛出异常
            raise

    def _get_client_ip(self, request: Request)-> str:
        """获取客户端IP地址"""
        # 检查代理头
        forwarded_for=request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # 取第一个IP（原始客户端IP）
            return forwarded_for.split(",")[0].strip()

        real_ip=request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # 回退到直接连接IP
        if hasattr(request, "client") and request.client:
            return request.client.host

        return "unknown"

    def _get_request_size(self, request: Request)-> int:
        """获取请求大小"""
        content_length=request.headers.get("Content-Length")
        if content_length:
            try:
                return int(content_length)
            except ValueError:
                pass
        return 0

    def _get_response_size(self, response: Response)-> int:
        """获取响应大小"""
        content_length=response.headers.get("Content-Length")
        if content_length:
            try:
                return int(content_length)
            except ValueError:
                pass
        return 0