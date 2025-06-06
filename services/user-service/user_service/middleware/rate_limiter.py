"""
rate_limiter - 索克生活项目模块
"""

from collections import defaultdict, deque
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Optional, Tuple, Any
import asyncio
import json
import logging
import redis.asyncio as redis
import time

"""
用户服务API限流中间件
实现基于IP和用户的多维度限流保护
"""



logger = logging.getLogger(__name__)


class RateLimiter:
    """高性能限流器"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client
        # 内存存储作为备份
        self.memory_store: Dict[str, deque] = defaultdict(deque)
        self.lock = asyncio.Lock()
        
        # 限流规则配置
        self.rules = {
            # 全局限流
            "global": {
                "requests_per_minute": 1000,
                "requests_per_hour": 10000,
                "burst_size": 100
            },
            # IP限流
            "ip": {
                "requests_per_minute": 60,
                "requests_per_hour": 1000,
                "burst_size": 10
            },
            # 用户限流
            "user": {
                "requests_per_minute": 120,
                "requests_per_hour": 2000,
                "burst_size": 20
            },
            # 端点特定限流
            "endpoints": {
                "/api/v1/auth/login": {
                    "requests_per_minute": 5,
                    "requests_per_hour": 20,
                    "burst_size": 2
                },
                "/api/v1/users/register": {
                    "requests_per_minute": 3,
                    "requests_per_hour": 10,
                    "burst_size": 1
                },
                "/api/v1/health-data": {
                    "requests_per_minute": 30,
                    "requests_per_hour": 500,
                    "burst_size": 5
                }
            }
        }
    
    async def is_allowed(
        self,
        key: str,
        rule_type: str,
        endpoint: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        检查请求是否被允许
        
        Args:
            key: 限流键 (IP地址或用户ID)
            rule_type: 规则类型 (global, ip, user)
            endpoint: 端点路径
            
        Returns:
            (是否允许, 限流信息)
        """
        current_time = time.time()
        
        # 获取适用的规则
        rules = self._get_applicable_rules(rule_type, endpoint)
        
        # 检查每个时间窗口
        for window, limit in rules.items():
            if window.startswith("requests_per_"):
                window_seconds = self._get_window_seconds(window)
                allowed, info = await self._check_window(
                    key, window_seconds, limit, current_time
                )
                if not allowed:
                    return False, info
        
        # 检查突发限制
        burst_allowed, burst_info = await self._check_burst(
            key, rules.get("burst_size", 10), current_time
        )
        
        if not burst_allowed:
            return False, burst_info
        
        # 记录请求
        await self._record_request(key, current_time)
        
        return True, {
            "allowed": True,
            "remaining": await self._get_remaining_requests(key, rules),
            "reset_time": await self._get_reset_time(key)
        }
    
    def _get_applicable_rules(self, rule_type: str, endpoint: Optional[str]) -> Dict[str, int]:
        """获取适用的限流规则"""
        # 端点特定规则优先
        if endpoint and endpoint in self.rules["endpoints"]:
            return self.rules["endpoints"][endpoint]
        
        # 使用类型规则
        return self.rules.get(rule_type, self.rules["global"])
    
    def _get_window_seconds(self, window: str) -> int:
        """获取时间窗口秒数"""
        if "minute" in window:
            return 60
        elif "hour" in window:
            return 3600
        elif "day" in window:
            return 86400
        return 60
    
    async def _check_window(
        self,
        key: str,
        window_seconds: int,
        limit: int,
        current_time: float
    ) -> Tuple[bool, Dict[str, Any]]:
        """检查时间窗口限制"""
        window_key = f"{key}:{window_seconds}"
        
        if self.redis:
            return await self._check_window_redis(window_key, window_seconds, limit, current_time)
        else:
            return await self._check_window_memory(window_key, window_seconds, limit, current_time)
    
    async def _check_window_redis(
        self,
        window_key: str,
        window_seconds: int,
        limit: int,
        current_time: float
    ) -> Tuple[bool, Dict[str, Any]]:
        """使用Redis检查时间窗口"""
        try:
            pipe = self.redis.pipeline()
            
            # 使用滑动窗口算法
            window_start = current_time - window_seconds
            
            # 清理过期记录
            pipe.zremrangebyscore(window_key, 0, window_start)
            
            # 获取当前窗口内的请求数
            pipe.zcard(window_key)
            
            # 添加当前请求
            pipe.zadd(window_key, {str(current_time): current_time})
            
            # 设置过期时间
            pipe.expire(window_key, window_seconds)
            
            results = await pipe.execute()
            current_count = results[1]
            
            if current_count >= limit:
                return False, {
                    "allowed": False,
                    "limit": limit,
                    "current": current_count,
                    "window_seconds": window_seconds,
                    "retry_after": window_seconds
                }
            
            return True, {
                "allowed": True,
                "limit": limit,
                "current": current_count + 1,
                "window_seconds": window_seconds
            }
            
        except Exception as e:
            logger.error(f"Redis限流检查失败: {e}")
            # 降级到内存存储
            return await self._check_window_memory(window_key, window_seconds, limit, current_time)
    
    async def _check_window_memory(
        self,
        window_key: str,
        window_seconds: int,
        limit: int,
        current_time: float
    ) -> Tuple[bool, Dict[str, Any]]:
        """使用内存检查时间窗口"""
        async with self.lock:
            requests = self.memory_store[window_key]
            
            # 清理过期请求
            window_start = current_time - window_seconds
            while requests and requests[0] < window_start:
                requests.popleft()
            
            if len(requests) >= limit:
                return False, {
                    "allowed": False,
                    "limit": limit,
                    "current": len(requests),
                    "window_seconds": window_seconds,
                    "retry_after": window_seconds
                }
            
            # 添加当前请求
            requests.append(current_time)
            
            return True, {
                "allowed": True,
                "limit": limit,
                "current": len(requests),
                "window_seconds": window_seconds
            }
    
    async def _check_burst(
        self,
        key: str,
        burst_size: int,
        current_time: float
    ) -> Tuple[bool, Dict[str, Any]]:
        """检查突发限制"""
        burst_key = f"{key}:burst"
        burst_window = 10  # 10秒突发窗口
        
        if self.redis:
            try:
                pipe = self.redis.pipeline()
                window_start = current_time - burst_window
                
                pipe.zremrangebyscore(burst_key, 0, window_start)
                pipe.zcard(burst_key)
                pipe.zadd(burst_key, {str(current_time): current_time})
                pipe.expire(burst_key, burst_window)
                
                results = await pipe.execute()
                current_burst = results[1]
                
                if current_burst >= burst_size:
                    return False, {
                        "allowed": False,
                        "burst_limit": burst_size,
                        "current_burst": current_burst,
                        "retry_after": burst_window
                    }
                
                return True, {"burst_allowed": True}
                
            except Exception as e:
                logger.error(f"Redis突发限制检查失败: {e}")
        
        # 内存备份
        async with self.lock:
            requests = self.memory_store[burst_key]
            window_start = current_time - burst_window
            
            while requests and requests[0] < window_start:
                requests.popleft()
            
            if len(requests) >= burst_size:
                return False, {
                    "allowed": False,
                    "burst_limit": burst_size,
                    "current_burst": len(requests),
                    "retry_after": burst_window
                }
            
            requests.append(current_time)
            return True, {"burst_allowed": True}
    
    async def _record_request(self, key: str, current_time: float):
        """记录请求"""
        # 在检查方法中已经记录了，这里可以添加额外的统计
        pass
    
    async def _get_remaining_requests(self, key: str, rules: Dict[str, int]) -> Dict[str, int]:
        """获取剩余请求数"""
        remaining = {}
        current_time = time.time()
        
        for window, limit in rules.items():
            if window.startswith("requests_per_"):
                window_seconds = self._get_window_seconds(window)
                window_key = f"{key}:{window_seconds}"
                
                if self.redis:
                    try:
                        window_start = current_time - window_seconds
                        await self.redis.zremrangebyscore(window_key, 0, window_start)
                        current_count = await self.redis.zcard(window_key)
                        remaining[window] = max(0, limit - current_count)
                    except Exception:
                        remaining[window] = limit
                else:
                    requests = self.memory_store[window_key]
                    remaining[window] = max(0, limit - len(requests))
        
        return remaining
    
    async def _get_reset_time(self, key: str) -> int:
        """获取重置时间"""
        current_time = time.time()
        # 返回下一分钟的开始时间
        return int(current_time + (60 - current_time % 60))


class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件"""
    
    def __init__(self, app, redis_client: Optional[redis.Redis] = None):
        super().__init__(app)
        self.limiter = RateLimiter(redis_client)
        
        # 白名单IP
        self.whitelist_ips = {
            "127.0.0.1",
            "::1",
            "localhost"
        }
        
        # 需要跳过限流的路径
        self.skip_paths = {
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json"
        }
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        # 跳过特定路径
        if request.url.path in self.skip_paths:
            return await call_next(request)
        
        # 获取客户端IP
        client_ip = self._get_client_ip(request)
        
        # 白名单检查
        if client_ip in self.whitelist_ips:
            return await call_next(request)
        
        # 获取用户ID
        user_id = self._get_user_id(request)
        
        # 检查限流
        rate_limit_result = await self._check_rate_limits(
            request, client_ip, user_id
        )
        
        if not rate_limit_result["allowed"]:
            return self._create_rate_limit_response(rate_limit_result)
        
        # 添加限流头信息
        response = await call_next(request)
        self._add_rate_limit_headers(response, rate_limit_result)
        
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
        
        # 使用客户端地址
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"
    
    def _get_user_id(self, request: Request) -> Optional[str]:
        """从请求中获取用户ID"""
        # 从JWT token中提取用户ID
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                # 这里应该解析JWT token获取用户ID
                # 简化实现，实际应该使用JWT库
                token = auth_header[7:]
                # 假设从token中提取用户ID的逻辑
                # user_id = extract_user_id_from_token(token)
                return None  # 暂时返回None
            except Exception:
                pass
        
        return None
    
    async def _check_rate_limits(
        self,
        request: Request,
        client_ip: str,
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """检查所有适用的限流规则"""
        endpoint = request.url.path
        
        # 检查全局限流
        global_allowed, global_info = await self.limiter.is_allowed(
            "global", "global", endpoint
        )
        if not global_allowed:
            return global_info
        
        # 检查IP限流
        ip_allowed, ip_info = await self.limiter.is_allowed(
            f"ip:{client_ip}", "ip", endpoint
        )
        if not ip_allowed:
            return ip_info
        
        # 检查用户限流
        if user_id:
            user_allowed, user_info = await self.limiter.is_allowed(
                f"user:{user_id}", "user", endpoint
            )
            if not user_allowed:
                return user_info
        
        # 所有检查通过
        return {
            "allowed": True,
            "global_info": global_info,
            "ip_info": ip_info,
            "user_info": user_info if user_id else None
        }
    
    def _create_rate_limit_response(self, rate_limit_info: Dict[str, Any]) -> JSONResponse:
        """创建限流响应"""
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "请求频率超过限制",
                    "details": {
                        "limit": rate_limit_info.get("limit"),
                        "current": rate_limit_info.get("current"),
                        "window_seconds": rate_limit_info.get("window_seconds"),
                        "retry_after": rate_limit_info.get("retry_after")
                    }
                }
            },
            headers={
                "Retry-After": str(rate_limit_info.get("retry_after", 60)),
                "X-RateLimit-Limit": str(rate_limit_info.get("limit", 0)),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(rate_limit_info.get("retry_after", 60))
            }
        )
    
    def _add_rate_limit_headers(self, response: Response, rate_limit_info: Dict[str, Any]):
        """添加限流头信息"""
        if rate_limit_info.get("allowed"):
            # 从IP信息中获取限流数据
            ip_info = rate_limit_info.get("ip_info", {})
            
            response.headers["X-RateLimit-Limit"] = str(ip_info.get("limit", 60))
            response.headers["X-RateLimit-Remaining"] = str(
                ip_info.get("limit", 60) - ip_info.get("current", 0)
            )
            response.headers["X-RateLimit-Reset"] = str(
                int(time.time()) + ip_info.get("window_seconds", 60)
            )


# 工厂函数
def create_rate_limit_middleware(redis_url: Optional[str] = None):
    """创建限流中间件"""
    redis_client = None
    if redis_url:
        try:
            redis_client = redis.from_url(redis_url)
        except Exception as e:
            logger.warning(f"无法连接Redis，使用内存存储: {e}")
    
    return RateLimitMiddleware(None, redis_client) 