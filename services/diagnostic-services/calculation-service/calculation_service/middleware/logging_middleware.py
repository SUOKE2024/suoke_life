"""
日志中间件
索克生活 - 算诊服务日志记录中间件
"""

import logging
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志记录中间件"""

    def __init__(self, app, log_requests: bool = True, log_responses: bool = True):
        """
        初始化日志中间件

        Args:
            app: FastAPI应用实例
            log_requests: 是否记录请求日志
            log_responses: 是否记录响应日志
        """
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求和响应的日志记录"""

        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # 记录请求开始时间
        start_time = time.time()

        # 记录请求信息
        if self.log_requests:
            await self._log_request(request, request_id)

        # 处理请求
        try:
            response = await call_next(request)

            # 计算处理时间
            process_time = time.time() - start_time

            # 记录响应信息
            if self.log_responses:
                await self._log_response(request, response, request_id, process_time)

            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            # 记录错误信息
            process_time = time.time() - start_time
            await self._log_error(request, e, request_id, process_time)
            raise

    async def _log_request(self, request: Request, request_id: str):
        """记录请求信息"""
        try:
            # 获取客户端IP
            client_ip = self._get_client_ip(request)

            # 获取用户代理
            user_agent = request.headers.get("user-agent", "")

            # 构建请求日志
            log_data = {
                "event": "request_start",
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": client_ip,
                "user_agent": user_agent,
                "headers": dict(request.headers),
                "timestamp": time.time(),
            }

            # 记录请求体（仅对POST/PUT/PATCH请求）
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    # 注意：这里需要小心处理，避免消费request body
                    content_type = request.headers.get("content-type", "")
                    if "application/json" in content_type:
                        log_data["content_type"] = content_type
                except Exception:
                    pass

            logger.info(
                f"请求开始: {request.method} {request.url.path}",
                extra={"log_data": log_data},
            )

        except Exception as e:
            logger.error(f"记录请求日志失败: {e}")

    async def _log_response(
        self, request: Request, response: Response, request_id: str, process_time: float
    ):
        """记录响应信息"""
        try:
            log_data = {
                "event": "request_complete",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": process_time,
                "response_headers": dict(response.headers),
                "timestamp": time.time(),
            }

            # 根据状态码确定日志级别
            if response.status_code >= 500:
                log_level = "error"
            elif response.status_code >= 400:
                log_level = "warning"
            else:
                log_level = "info"

            log_message = f"请求完成: {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)"

            getattr(logger, log_level)(log_message, extra={"log_data": log_data})

        except Exception as e:
            logger.error(f"记录响应日志失败: {e}")

    async def _log_error(
        self, request: Request, error: Exception, request_id: str, process_time: float
    ):
        """记录错误信息"""
        try:
            log_data = {
                "event": "request_error",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "process_time": process_time,
                "timestamp": time.time(),
            }

            logger.error(
                f"请求错误: {request.method} {request.url.path} - {type(error).__name__}: {error}",
                extra={"log_data": log_data},
                exc_info=True,
            )

        except Exception as e:
            logger.error(f"记录错误日志失败: {e}")

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 尝试从各种头部获取真实IP
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # 回退到直接连接IP
        if hasattr(request, "client") and request.client:
            return request.client.host

        return "unknown"


class StructuredLogger:
    """结构化日志记录器"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_calculation_start(
        self, calc_type: str, input_data: dict, request_id: str = None
    ):
        """记录算诊计算开始"""
        log_data = {
            "event": "calculation_start",
            "calculation_type": calc_type,
            "input_data": input_data,
            "request_id": request_id,
            "timestamp": time.time(),
        }
        self.logger.info(f"算诊计算开始: {calc_type}", extra={"log_data": log_data})

    def log_calculation_complete(
        self, calc_type: str, process_time: float, request_id: str = None
    ):
        """记录算诊计算完成"""
        log_data = {
            "event": "calculation_complete",
            "calculation_type": calc_type,
            "process_time": process_time,
            "request_id": request_id,
            "timestamp": time.time(),
        }
        self.logger.info(
            f"算诊计算完成: {calc_type} ({process_time:.3f}s)",
            extra={"log_data": log_data},
        )

    def log_calculation_error(
        self,
        calc_type: str,
        error: Exception,
        process_time: float,
        request_id: str = None,
    ):
        """记录算诊计算错误"""
        log_data = {
            "event": "calculation_error",
            "calculation_type": calc_type,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "process_time": process_time,
            "request_id": request_id,
            "timestamp": time.time(),
        }
        self.logger.error(
            f"算诊计算错误: {calc_type} - {type(error).__name__}: {error}",
            extra={"log_data": log_data},
            exc_info=True,
        )

    def log_cache_hit(self, cache_key: str, calc_type: str, request_id: str = None):
        """记录缓存命中"""
        log_data = {
            "event": "cache_hit",
            "cache_key": cache_key,
            "calculation_type": calc_type,
            "request_id": request_id,
            "timestamp": time.time(),
        }
        self.logger.debug(f"缓存命中: {calc_type}", extra={"log_data": log_data})

    def log_cache_miss(self, cache_key: str, calc_type: str, request_id: str = None):
        """记录缓存未命中"""
        log_data = {
            "event": "cache_miss",
            "cache_key": cache_key,
            "calculation_type": calc_type,
            "request_id": request_id,
            "timestamp": time.time(),
        }
        self.logger.debug(f"缓存未命中: {calc_type}", extra={"log_data": log_data})


# 全局结构化日志记录器
calculation_logger = StructuredLogger("calculation_service")
