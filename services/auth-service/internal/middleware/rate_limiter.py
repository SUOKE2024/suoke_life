"""
请求速率限制中间件

提供基于令牌桶算法的请求速率限制功能，支持多种限制策略。
"""
import asyncio
import time
import logging
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import redis.asyncio as redis

from internal.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class TokenBucket:
    """令牌桶"""
    capacity: int  # 桶容量
    tokens: float  # 当前令牌数
    refill_rate: float  # 令牌补充速率（每秒）
    last_refill: float = field(default_factory=time.time)
    
    def consume(self, tokens: int = 1) -> bool:
        """消费令牌"""
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def _refill(self):
        """补充令牌"""
        now = time.time()
        time_passed = now - self.last_refill
        
        # 计算应该补充的令牌数
        tokens_to_add = time_passed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now


@dataclass
class RateLimitRule:
    """速率限制规则"""
    requests: int  # 请求数量
    window: int  # 时间窗口（秒）
    burst: Optional[int] = None  # 突发请求数量
    key_func: Optional[str] = None  # 键函数名称
    
    @property
    def rate(self) -> float:
        """每秒请求速率"""
        return self.requests / self.window


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.local_buckets: Dict[str, TokenBucket] = {}
        self.cleanup_interval = 300  # 5分钟清理一次
        self.last_cleanup = time.time()
        
        # 默认限制规则
        self.rules = {
            "login": RateLimitRule(requests=5, window=300, burst=10),  # 5分钟5次登录
            "register": RateLimitRule(requests=3, window=3600, burst=5),  # 1小时3次注册
            "password_reset": RateLimitRule(requests=3, window=3600),  # 1小时3次密码重置
            "mfa_verify": RateLimitRule(requests=10, window=300),  # 5分钟10次MFA验证
            "api_general": RateLimitRule(requests=100, window=60),  # 1分钟100次API调用
            "api_sensitive": RateLimitRule(requests=10, window=60),  # 1分钟10次敏感API调用
        }
    
    async def check_rate_limit(
        self, 
        request: Request, 
        rule_name: str,
        identifier: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """检查速率限制"""
        rule = self.rules.get(rule_name)
        if not rule:
            logger.warning(f"未找到速率限制规则: {rule_name}")
            return True, {}
        
        # 生成限制键
        key = self._generate_key(request, rule_name, identifier, rule)
        
        # 清理过期的本地桶
        self._cleanup_local_buckets()
        
        # 检查限制
        if self.redis_client:
            allowed, info = await self._check_redis_limit(key, rule)
        else:
            allowed, info = await self._check_local_limit(key, rule)
        
        # 记录限制事件
        if not allowed:
            logger.warning(
                f"速率限制触发: rule={rule_name}, key={key}, "
                f"requests={info.get('requests', 0)}, "
                f"window={rule.window}秒"
            )
        
        return allowed, info
    
    async def _check_redis_limit(
        self, 
        key: str, 
        rule: RateLimitRule
    ) -> Tuple[bool, Dict[str, Any]]:
        """使用Redis检查速率限制"""
        try:
            # 使用滑动窗口算法
            now = time.time()
            window_start = now - rule.window
            
            # 清理过期记录
            await self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # 获取当前窗口内的请求数
            current_requests = await self.redis_client.zcard(key)
            
            if current_requests >= rule.requests:
                # 获取最早请求的时间
                earliest = await self.redis_client.zrange(key, 0, 0, withscores=True)
                reset_time = earliest[0][1] + rule.window if earliest else now + rule.window
                
                return False, {
                    "requests": current_requests,
                    "limit": rule.requests,
                    "window": rule.window,
                    "reset_time": reset_time,
                    "retry_after": int(reset_time - now)
                }
            
            # 记录当前请求
            await self.redis_client.zadd(key, {str(now): now})
            await self.redis_client.expire(key, rule.window + 1)
            
            return True, {
                "requests": current_requests + 1,
                "limit": rule.requests,
                "window": rule.window,
                "remaining": rule.requests - current_requests - 1
            }
            
        except Exception as e:
            logger.error(f"Redis速率限制检查失败: {str(e)}")
            # 降级到本地限制
            return await self._check_local_limit(key, rule)
    
    async def _check_local_limit(
        self, 
        key: str, 
        rule: RateLimitRule
    ) -> Tuple[bool, Dict[str, Any]]:
        """使用本地令牌桶检查速率限制"""
        # 获取或创建令牌桶
        if key not in self.local_buckets:
            capacity = rule.burst or rule.requests
            self.local_buckets[key] = TokenBucket(
                capacity=capacity,
                tokens=capacity,
                refill_rate=rule.rate
            )
        
        bucket = self.local_buckets[key]
        
        if bucket.consume():
            return True, {
                "requests": int(bucket.capacity - bucket.tokens),
                "limit": rule.requests,
                "window": rule.window,
                "remaining": int(bucket.tokens)
            }
        else:
            # 计算重试时间
            tokens_needed = 1
            retry_after = tokens_needed / bucket.refill_rate
            
            return False, {
                "requests": bucket.capacity,
                "limit": rule.requests,
                "window": rule.window,
                "retry_after": int(retry_after)
            }
    
    def _generate_key(
        self, 
        request: Request, 
        rule_name: str, 
        identifier: Optional[str],
        rule: RateLimitRule
    ) -> str:
        """生成限制键"""
        if identifier:
            return f"rate_limit:{rule_name}:{identifier}"
        
        # 根据规则的键函数生成标识符
        if rule.key_func == "ip":
            client_ip = self._get_client_ip(request)
            return f"rate_limit:{rule_name}:ip:{client_ip}"
        elif rule.key_func == "user":
            user_id = getattr(request.state, "user_id", None)
            if user_id:
                return f"rate_limit:{rule_name}:user:{user_id}"
            else:
                # 未登录用户使用IP
                client_ip = self._get_client_ip(request)
                return f"rate_limit:{rule_name}:ip:{client_ip}"
        else:
            # 默认使用IP
            client_ip = self._get_client_ip(request)
            return f"rate_limit:{rule_name}:ip:{client_ip}"
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        # 检查代理头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _cleanup_local_buckets(self):
        """清理过期的本地令牌桶"""
        now = time.time()
        if now - self.last_cleanup < self.cleanup_interval:
            return
        
        # 清理超过1小时未使用的桶
        expired_keys = []
        for key, bucket in self.local_buckets.items():
            if now - bucket.last_refill > 3600:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.local_buckets[key]
        
        self.last_cleanup = now
        
        if expired_keys:
            logger.info(f"清理了 {len(expired_keys)} 个过期的令牌桶")
    
    def add_rule(self, name: str, rule: RateLimitRule):
        """添加限制规则"""
        self.rules[name] = rule
        logger.info(f"添加速率限制规则: {name} = {rule}")
    
    def remove_rule(self, name: str):
        """移除限制规则"""
        if name in self.rules:
            del self.rules[name]
            logger.info(f"移除速率限制规则: {name}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "rules_count": len(self.rules),
            "local_buckets_count": len(self.local_buckets),
            "redis_enabled": self.redis_client is not None,
            "last_cleanup": self.last_cleanup,
            "rules": {
                name: {
                    "requests": rule.requests,
                    "window": rule.window,
                    "rate": rule.rate,
                    "burst": rule.burst
                }
                for name, rule in self.rules.items()
            }
        }


# 全局速率限制器实例
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """获取速率限制器实例"""
    global _rate_limiter
    if _rate_limiter is None:
        # 尝试连接Redis
        redis_client = None
        if settings.redis_url:
            try:
                redis_client = redis.from_url(settings.redis_url)
            except Exception as e:
                logger.warning(f"Redis连接失败，使用本地限制: {str(e)}")
        
        _rate_limiter = RateLimiter(redis_client)
    
    return _rate_limiter


async def rate_limit_middleware(request: Request, call_next):
    """速率限制中间件"""
    # 跳过健康检查和静态文件
    if request.url.path in ["/health", "/metrics", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    rate_limiter = get_rate_limiter()
    
    # 根据路径确定限制规则
    rule_name = _get_rule_name_for_path(request.url.path)
    
    if rule_name:
        allowed, info = await rate_limiter.check_rate_limit(request, rule_name)
        
        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "请求过于频繁，请稍后再试",
                    "details": info
                },
                headers={
                    "Retry-After": str(info.get("retry_after", 60)),
                    "X-RateLimit-Limit": str(info.get("limit", 0)),
                    "X-RateLimit-Remaining": str(info.get("remaining", 0)),
                    "X-RateLimit-Reset": str(info.get("reset_time", 0))
                }
            )
        
        # 添加速率限制头
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(info.get("limit", 0))
        response.headers["X-RateLimit-Remaining"] = str(info.get("remaining", 0))
        return response
    
    return await call_next(request)


def _get_rule_name_for_path(path: str) -> Optional[str]:
    """根据路径获取限制规则名称"""
    if "/auth/login" in path:
        return "login"
    elif "/auth/register" in path:
        return "register"
    elif "/auth/password/reset" in path:
        return "password_reset"
    elif "/auth/mfa" in path:
        return "mfa_verify"
    elif any(sensitive in path for sensitive in ["/admin", "/users", "/roles"]):
        return "api_sensitive"
    elif "/api/" in path:
        return "api_general"
    
    return None


def create_rate_limit_decorator(rule_name: str):
    """创建速率限制装饰器"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            rate_limiter = get_rate_limiter()
            allowed, info = await rate_limiter.check_rate_limit(request, rule_name)
            
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "rate_limit_exceeded",
                        "message": "请求过于频繁，请稍后再试",
                        "details": info
                    },
                    headers={
                        "Retry-After": str(info.get("retry_after", 60))
                    }
                )
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


# 常用装饰器
login_rate_limit = create_rate_limit_decorator("login")
register_rate_limit = create_rate_limit_decorator("register")
password_reset_rate_limit = create_rate_limit_decorator("password_reset")
mfa_rate_limit = create_rate_limit_decorator("mfa_verify") 