#!/usr/bin/env python3
"""
索克生活 API 网关链路追踪中间件

集成 OpenTelemetry 进行分布式链路追踪。
"""

from ..core.config import get_settings
from ..core.logging import get_logger
from fastapi import Request, Response
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import time

logger=get_logger(__name__)


class TracingMiddleware(BaseHTTPMiddleware):
    """链路追踪中间件"""

    def __init__(self, app, settings=None):
        """TODO: 添加文档字符串"""
        super().__init__(app)
        self.settings=settings or get_settings()
        self.tracer=trace.get_tracer(__name__)

        # 不追踪的路径
        self.skip_paths={
            "/health",
            "/health/ready",
            "/health/live",
            "/metrics",
        }

    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        # 跳过不需要追踪的路径
        if request.url.path in self.skip_paths:
            return await call_next(request)

        # 创建 span
        span_name=f"{request.method} {request.url.path}"

        with self.tracer.start_as_current_span(span_name) as span:
            # 设置 span 属性
            self._set_span_attributes(span, request)

            try:
                # 处理请求
                start_time=time.time()
                response=await call_next(request)
                process_time=time.time()-start_time

                # 设置响应属性
                self._set_response_attributes(span, response, process_time)

                # 添加追踪头到响应
                self._add_trace_headers(response, span)

                return response

            except Exception as e:
                # 记录异常
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))

                logger.error(
                    "Request failed in tracing middleware",
                    error=str(e),
                    span_id=format(span.get_span_context().span_id, '016x'),
                    trace_id=format(span.get_span_context().trace_id, '032x'),
                    exc_info=True,
                )

                # 重新抛出异常
                raise

    def _set_span_attributes(self, span: trace.Span, request: Request)-> None:
        """设置 span 属性"""
        # HTTP 属性
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", str(request.url))
        span.set_attribute("http.scheme", request.url.scheme)
        span.set_attribute("http.host", request.url.hostname or "")
        span.set_attribute("http.target", request.url.path)

        # 用户属性
        user_id=getattr(request.state, "user_id", None)
        if user_id:
            span.set_attribute("user.id", user_id)

        # 请求属性
        request_id=getattr(request.state, "request_id", None)
        if request_id:
            span.set_attribute("request.id", request_id)

        # 客户端属性
        client_ip=self._get_client_ip(request)
        if client_ip:
            span.set_attribute("http.client_ip", client_ip)

        user_agent=request.headers.get("User-Agent")
        if user_agent:
            span.set_attribute("http.user_agent", user_agent)

    def _set_response_attributes(
        self,
        span: trace.Span,
        response: Response,
        process_time: float
    )-> None:
        """设置响应属性"""
        # HTTP 响应属性
        span.set_attribute("http.status_code", response.status_code)
        span.set_attribute("http.response_size",
                        len(response.body) if hasattr(response, 'body') else 0)

        # 性能属性
        span.set_attribute("http.response_time_ms", round(process_time * 1000, 2))

        # 设置状态
        if response.status_code >=400:
            span.set_status(Status(StatusCode.ERROR, f"HTTP {response.status_code}"))
        else:
            span.set_status(Status(StatusCode.OK))

    def _add_trace_headers(self, response: Response, span: trace.Span)-> None:
        """添加追踪头到响应"""
        span_context=span.get_span_context()

        # 添加追踪ID和span ID
        response.headers["X-Trace-ID"]=format(span_context.trace_id, '032x')
        response.headers["X-Span-ID"]=format(span_context.span_id, '016x')

    def _get_client_ip(self, request: Request)-> Optional[str]:
        """获取客户端IP地址"""
        # 检查代理头
        forwarded_for=request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip=request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # 回退到直接连接IP
        if hasattr(request, "client") and request.client:
            return request.client.host

        return None