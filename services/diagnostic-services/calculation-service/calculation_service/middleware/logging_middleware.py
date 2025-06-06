"""
logging_middleware - 索克生活项目模块
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import logging
import time

"""
日志中间件

记录请求和响应信息
"""


logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求和响应日志"""
        start_time = time.time()
        
        # 记录请求信息
        logger.info(
            f"请求开始 - {request.method} {request.url.path} "
            f"来源IP: {request.client.host if request.client else 'unknown'}"
        )
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            logger.info(
                f"请求完成 - {request.method} {request.url.path} "
                f"状态码: {response.status_code} "
                f"处理时间: {process_time:.3f}s"
            )
            
            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # 记录异常信息
            process_time = time.time() - start_time
            logger.error(
                f"请求异常 - {request.method} {request.url.path} "
                f"错误: {str(e)} "
                f"处理时间: {process_time:.3f}s"
            )
            raise 