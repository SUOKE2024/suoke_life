"""
限流中间件

防止API滥用
"""

import time
import logging
from typing import Callable, Dict
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """限流中间件"""
    
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        """
        初始化限流中间件
        
        Args:
            app: FastAPI应用实例
            max_requests: 时间窗口内最大请求数
            window_seconds: 时间窗口大小（秒）
        """
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}
    
    def _get_client_id(self, request: Request) -> str:
        """获取客户端标识"""
        # 优先使用X-Forwarded-For头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # 使用客户端IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_rate_limited(self, client_id: str) -> bool:
        """检查是否超过限流"""
        current_time = time.time()
        
        # 获取客户端请求记录
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        client_requests = self.requests[client_id]
        
        # 清理过期请求记录
        cutoff_time = current_time - self.window_seconds
        client_requests[:] = [req_time for req_time in client_requests if req_time > cutoff_time]
        
        # 检查是否超过限制
        if len(client_requests) >= self.max_requests:
            return True
        
        # 记录当前请求
        client_requests.append(current_time)
        return False
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理限流逻辑"""
        client_id = self._get_client_id(request)
        
        # 检查限流
        if self._is_rate_limited(client_id):
            logger.warning(f"客户端 {client_id} 触发限流")
            
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": f"请求过于频繁，请在 {self.window_seconds} 秒后重试",
                    "type": "rate_limit_error",
                    "retry_after": self.window_seconds
                },
                headers={"Retry-After": str(self.window_seconds)}
            )
        
        # 继续处理请求
        response = await call_next(request)
        
        # 添加限流信息到响应头
        remaining_requests = max(0, self.max_requests - len(self.requests.get(client_id, [])))
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining_requests)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + self.window_seconds))
        
        return response 