"""
logging - 索克生活项目模块
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import logging
import time
import uuid

"""日志中间件"""


logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求日志"""
        
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取客户端IP
        client_ip = self._get_client_ip(request)
        
        # 记录请求信息
        logger.info(
            f"请求开始",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": client_ip,
                "user_agent": request.headers.get("user-agent", ""),
                "content_type": request.headers.get("content-type", ""),
                "content_length": request.headers.get("content-length", 0)
            }
        )
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            logger.info(
                f"请求完成",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "process_time": round(process_time, 4),
                    "client_ip": client_ip,
                    "user_id": getattr(request.state, "user_id", None),
                    "response_size": response.headers.get("content-length", 0)
                }
            )
            
            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time, 4))
            
            return response
            
        except Exception as e:
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录错误信息
            logger.error(
                f"请求处理失败",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "process_time": round(process_time, 4),
                    "client_ip": client_ip,
                    "user_id": getattr(request.state, "user_id", None)
                },
                exc_info=True
            )
            
            # 重新抛出异常
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        
        # 检查代理头
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # 取第一个IP（原始客户端IP）
            return forwarded_for.split(",")[0].strip()
        
        # 检查其他代理头
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # 使用客户端地址
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown" 