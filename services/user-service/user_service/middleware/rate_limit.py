"""限流中间件"""

import time
import logging
from typing import Dict, Tuple
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        
        # 限流配置
        self.rate_limits = {
            "default": (100, 60),  # 每分钟100次请求
            "auth": (10, 60),      # 认证相关每分钟10次
            "upload": (5, 60),     # 上传相关每分钟5次
        }
        
        # 存储客户端请求记录
        self.client_requests: Dict[str, deque] = defaultdict(deque)
        
        # 清理间隔（秒）
        self.cleanup_interval = 300  # 5分钟
        self.last_cleanup = time.time()
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """处理请求限流"""
        
        # 获取客户端标识
        client_id = self._get_client_id(request)
        
        # 获取限流规则
        limit_key = self._get_limit_key(request)
        max_requests, window_seconds = self.rate_limits.get(limit_key, self.rate_limits["default"])
        
        # 检查限流
        if self._is_rate_limited(client_id, max_requests, window_seconds):
            logger.warning(
                f"客户端 {client_id} 触发限流",
                extra={
                    "client_id": client_id,
                    "path": request.url.path,
                    "limit_key": limit_key,
                    "max_requests": max_requests,
                    "window_seconds": window_seconds
                }
            )
            
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": "请求过于频繁，请稍后再试",
                    "retry_after": window_seconds
                }
            )
        
        # 记录请求
        self._record_request(client_id)
        
        # 定期清理过期记录
        self._cleanup_expired_records()
        
        # 处理请求
        response = await call_next(request)
        
        # 添加限流相关响应头
        remaining = max_requests - len(self.client_requests[client_id])
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + window_seconds))
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """获取客户端标识"""
        
        # 优先使用用户ID（如果已认证）
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # 使用IP地址
        client_ip = self._get_client_ip(request)
        return f"ip:{client_ip}"
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        
        # 检查代理头
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"
    
    def _get_limit_key(self, request: Request) -> str:
        """获取限流规则键"""
        
        path = request.url.path.lower()
        
        # 认证相关路径
        if any(auth_path in path for auth_path in ["/auth", "/login", "/register", "/password"]):
            return "auth"
        
        # 上传相关路径
        if any(upload_path in path for upload_path in ["/upload", "/file", "/image"]):
            return "upload"
        
        return "default"
    
    def _is_rate_limited(self, client_id: str, max_requests: int, window_seconds: int) -> bool:
        """检查是否触发限流"""
        
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # 获取客户端请求记录
        requests = self.client_requests[client_id]
        
        # 移除过期请求
        while requests and requests[0] < cutoff_time:
            requests.popleft()
        
        # 检查是否超过限制
        return len(requests) >= max_requests
    
    def _record_request(self, client_id: str) -> None:
        """记录请求"""
        current_time = time.time()
        self.client_requests[client_id].append(current_time)
    
    def _cleanup_expired_records(self) -> None:
        """清理过期记录"""
        
        current_time = time.time()
        
        # 检查是否需要清理
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        self.last_cleanup = current_time
        
        # 清理所有客户端的过期记录
        max_window = max(window for _, window in self.rate_limits.values())
        cutoff_time = current_time - max_window
        
        clients_to_remove = []
        
        for client_id, requests in self.client_requests.items():
            # 移除过期请求
            while requests and requests[0] < cutoff_time:
                requests.popleft()
            
            # 如果没有请求记录，标记为删除
            if not requests:
                clients_to_remove.append(client_id)
        
        # 删除空的客户端记录
        for client_id in clients_to_remove:
            del self.client_requests[client_id]
        
        logger.debug(f"清理了 {len(clients_to_remove)} 个过期的客户端记录") 