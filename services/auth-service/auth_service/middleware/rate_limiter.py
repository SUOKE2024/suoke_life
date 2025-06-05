"""
API 限流中间件
实现基于IP和用户的请求频率限制，防止暴力攻击和滥用
"""

import time
import asyncio
from typing import Dict, Optional, Tuple
from collections import defaultdict, deque
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import redis.asyncio as redis
from datetime import datetime, timedelta

from auth_service.config.settings import get_settings


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.settings = get_settings()
        self.redis_client = redis_client
        
        # 内存存储（当Redis不可用时的备选方案）
        self.memory_store: Dict[str, deque] = defaultdict(deque)
        self.cleanup_interval = 300  # 5分钟清理一次过期记录
        self.last_cleanup = time.time()
    
    async def is_allowed(
        self, 
        key: str, 
        limit: int, 
        window: int,
        identifier: str = "default"
    ) -> Tuple[bool, Dict[str, any]]:
        """
        检查是否允许请求
        
        Args:
            key: 限流键（通常是IP地址或用户ID）
            limit: 时间窗口内允许的最大请求数
            window: 时间窗口（秒）
            identifier: 限流标识符
            
        Returns:
            (是否允许, 限流信息)
        """
        now = time.time()
        
        if self.redis_client:
            return await self._check_redis_limit(key, limit, window, now, identifier)
        else:
            return await self._check_memory_limit(key, limit, window, now, identifier)
    
    async def _check_redis_limit(
        self, 
        key: str, 
        limit: int, 
        window: int, 
        now: float,
        identifier: str
    ) -> Tuple[bool, Dict[str, any]]:
        """使用Redis检查限流"""
        try:
            pipe = self.redis_client.pipeline()
            
            # 使用滑动窗口算法
            window_start = now - window
            redis_key = f"rate_limit:{identifier}:{key}"
            
            # 移除过期的记录
            pipe.zremrangebyscore(redis_key, 0, window_start)
            
            # 获取当前窗口内的请求数
            pipe.zcard(redis_key)
            
            # 添加当前请求
            pipe.zadd(redis_key, {str(now): now})
            
            # 设置过期时间
            pipe.expire(redis_key, window + 1)
            
            results = await pipe.execute()
            current_requests = results[1]
            
            # 检查是否超过限制
            if current_requests >= limit:
                # 获取最早的请求时间来计算重置时间
                earliest = await self.redis_client.zrange(redis_key, 0, 0, withscores=True)
                reset_time = int(earliest[0][1] + window) if earliest else int(now + window)
                
                return False, {
                    "allowed": False,
                    "limit": limit,
                    "remaining": 0,
                    "reset_time": reset_time,
                    "retry_after": reset_time - int(now)
                }
            
            remaining = limit - current_requests - 1
            reset_time = int(now + window)
            
            return True, {
                "allowed": True,
                "limit": limit,
                "remaining": remaining,
                "reset_time": reset_time,
                "retry_after": 0
            }
            
        except Exception as e:
            # Redis错误时回退到内存存储
            return await self._check_memory_limit(key, limit, window, now, identifier)
    
    async def _check_memory_limit(
        self, 
        key: str, 
        limit: int, 
        window: int, 
        now: float,
        identifier: str
    ) -> Tuple[bool, Dict[str, any]]:
        """使用内存检查限流"""
        full_key = f"{identifier}:{key}"
        requests = self.memory_store[full_key]
        
        # 清理过期请求
        window_start = now - window
        while requests and requests[0] < window_start:
            requests.popleft()
        
        # 检查是否超过限制
        if len(requests) >= limit:
            reset_time = int(requests[0] + window)
            return False, {
                "allowed": False,
                "limit": limit,
                "remaining": 0,
                "reset_time": reset_time,
                "retry_after": reset_time - int(now)
            }
        
        # 添加当前请求
        requests.append(now)
        
        # 定期清理内存
        if now - self.last_cleanup > self.cleanup_interval:
            await self._cleanup_memory()
            self.last_cleanup = now
        
        remaining = limit - len(requests)
        reset_time = int(now + window)
        
        return True, {
            "allowed": True,
            "limit": limit,
            "remaining": remaining,
            "reset_time": reset_time,
            "retry_after": 0
        }
    
    async def _cleanup_memory(self):
        """清理内存中的过期记录"""
        now = time.time()
        keys_to_remove = []
        
        for key, requests in self.memory_store.items():
            # 清理过期请求
            while requests and requests[0] < now - 3600:  # 清理1小时前的记录
                requests.popleft()
            
            # 如果队列为空，标记删除
            if not requests:
                keys_to_remove.append(key)
        
        # 删除空队列
        for key in keys_to_remove:
            del self.memory_store[key]


class RateLimitMiddleware:
    """限流中间件"""
    
    def __init__(self, app, redis_client: Optional[redis.Redis] = None):
        self.app = app
        self.rate_limiter = RateLimiter(redis_client)
        self.settings = get_settings()
        
        # 不同端点的限流配置
        self.rate_limits = {
            "/api/v1/auth/login": {"limit": 5, "window": 300, "per": "ip"},  # 5次/5分钟
            "/api/v1/auth/register": {"limit": 3, "window": 3600, "per": "ip"},  # 3次/小时
            "/api/v1/auth/forgot-password": {"limit": 3, "window": 3600, "per": "ip"},  # 3次/小时
            "/api/v1/auth/verify-mfa": {"limit": 10, "window": 300, "per": "user"},  # 10次/5分钟
            "/api/v1/auth/refresh": {"limit": 20, "window": 3600, "per": "user"},  # 20次/小时
        }
        
        # 全局限流配置
        self.global_limits = {
            "per_ip": {"limit": 100, "window": 3600},  # 每IP 100次/小时
            "per_user": {"limit": 1000, "window": 3600}  # 每用户 1000次/小时
        }
    
    async def __call__(self, request: Request, call_next):
        """中间件处理函数"""
        # 获取客户端IP
        client_ip = self._get_client_ip(request)
        
        # 获取用户ID（如果已认证）
        user_id = await self._get_user_id(request)
        
        # 检查特定端点限流
        path = request.url.path
        method = request.method
        
        if path in self.rate_limits:
            config = self.rate_limits[path]
            key = client_ip if config["per"] == "ip" else user_id
            
            if key:  # 只有在有有效key时才检查
                allowed, info = await self.rate_limiter.is_allowed(
                    key, config["limit"], config["window"], f"{method}:{path}"
                )
                
                if not allowed:
                    return self._create_rate_limit_response(info)
        
        # 检查全局IP限流
        if client_ip:
            allowed, info = await self.rate_limiter.is_allowed(
                client_ip, 
                self.global_limits["per_ip"]["limit"],
                self.global_limits["per_ip"]["window"],
                "global_ip"
            )
            
            if not allowed:
                return self._create_rate_limit_response(info, "IP全局限流")
        
        # 检查全局用户限流
        if user_id:
            allowed, info = await self.rate_limiter.is_allowed(
                user_id,
                self.global_limits["per_user"]["limit"],
                self.global_limits["per_user"]["window"],
                "global_user"
            )
            
            if not allowed:
                return self._create_rate_limit_response(info, "用户全局限流")
        
        # 继续处理请求
        response = await call_next(request)
        
        # 添加限流头信息
        if hasattr(request.state, "rate_limit_info"):
            info = request.state.rate_limit_info
            response.headers["X-RateLimit-Limit"] = str(info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(info["reset_time"])
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 检查代理头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 回退到直接连接IP
        return request.client.host if request.client else "unknown"
    
    async def _get_user_id(self, request: Request) -> Optional[str]:
        """获取用户ID（从JWT令牌中）"""
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header.split(" ")[1]
            
            # 这里应该调用认证服务来验证令牌
            # 为了简化，我们假设有一个验证函数
            from auth_service.core.auth import AuthService
            auth_service = AuthService()
            payload = auth_service.verify_token(token)
            
            return payload.get("sub") if payload else None
            
        except Exception:
            return None
    
    def _create_rate_limit_response(self, info: Dict[str, any], message: str = None) -> JSONResponse:
        """创建限流响应"""
        error_message = message or "请求过于频繁，请稍后再试"
        
        headers = {
            "X-RateLimit-Limit": str(info["limit"]),
            "X-RateLimit-Remaining": str(info["remaining"]),
            "X-RateLimit-Reset": str(info["reset_time"]),
            "Retry-After": str(info["retry_after"])
        }
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "rate_limit_exceeded",
                "message": error_message,
                "retry_after": info["retry_after"],
                "reset_time": info["reset_time"]
            },
            headers=headers
        )


# 装饰器版本的限流器
def rate_limit(limit: int, window: int, per: str = "ip", identifier: str = None):
    """
    限流装饰器
    
    Args:
        limit: 限制次数
        window: 时间窗口（秒）
        per: 限流维度（"ip" 或 "user"）
        identifier: 自定义标识符
    """
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            rate_limiter = RateLimiter()
            
            # 获取限流键
            if per == "ip":
                key = request.client.host if request.client else "unknown"
            elif per == "user":
                # 从请求中获取用户ID
                key = await _get_user_id_from_request(request)
                if not key:
                    # 如果没有用户ID，回退到IP
                    key = request.client.host if request.client else "unknown"
            else:
                key = per  # 自定义键
            
            # 检查限流
            func_name = func.__name__
            limit_id = identifier or f"func:{func_name}"
            
            allowed, info = await rate_limiter.is_allowed(key, limit, window, limit_id)
            
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="请求过于频繁，请稍后再试",
                    headers={
                        "X-RateLimit-Limit": str(info["limit"]),
                        "X-RateLimit-Remaining": str(info["remaining"]),
                        "X-RateLimit-Reset": str(info["reset_time"]),
                        "Retry-After": str(info["retry_after"])
                    }
                )
            
            # 存储限流信息到请求状态
            request.state.rate_limit_info = info
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


async def _get_user_id_from_request(request: Request) -> Optional[str]:
    """从请求中获取用户ID"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        
        from auth_service.core.auth import AuthService
        auth_service = AuthService()
        payload = auth_service.verify_token(token)
        
        return payload.get("sub") if payload else None
        
    except Exception:
        return None 