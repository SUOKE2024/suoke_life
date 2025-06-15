"""
速率限制中间件
基于令牌桶算法实现的API访问速率限制
"""
import asyncio
import logging
import time
from datetime import datetime
from typing import Optional, Dict, List, Tuple

from fastapi import FastAPI, Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from internal.observability.metrics import prometheus_metrics

# 日志记录器
logger = logging.getLogger(__name__)

class TokenBucket:
    """令牌桶算法实现"""
    
    def __init__(self, tokens: float, fill_rate: float, max_tokens: Optional[float] = None):
        """
        初始化令牌桶
        
        Args:
            tokens: 初始令牌数量
            fill_rate: 令牌填充速率（每秒）
            max_tokens: 最大令牌数量（默认与初始令牌数量相同）
        """
        self.capacity = float(tokens)  # 最大容量
        self.tokens = float(tokens)  # 当前令牌数量
        self.fill_rate = float(fill_rate)  # 填充速率
        self.last_update = time.time()  # 上次更新时间
        self.max_tokens = float(max_tokens) if max_tokens is not None else float(tokens)
    
    def consume(self, tokens: float) -> bool:
        """
        消费令牌
        
        Args:
            tokens: 要消费的令牌数量
            
        Returns:
            bool: 是否成功消费
        """
        # 更新令牌数量
        self._update()
        
        # 检查是否有足够的令牌
        if tokens <= self.tokens:
            self.tokens -= tokens
            return True
        
        return False
    
    def _update(self):
        """更新令牌数量"""
        now = time.time()
        delta = now - self.last_update
        
        # 计算新增令牌数量
        new_tokens = delta * self.fill_rate
        
        # 更新令牌数量，不超过最大容量
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        
        # 更新最后更新时间
        self.last_update = now
    
    def get_tokens(self) -> float:
        """
        获取当前令牌数量
        
        Returns:
            float: 当前令牌数量
        """
        self._update()
        return self.tokens
    
    def get_wait_time(self, tokens: float) -> float:
        """
        计算等待时间
        
        Args:
            tokens: 需要的令牌数量
            
        Returns:
            float: 需要等待的秒数
        """
        self._update()
        
        # 如果已有足够的令牌，不需要等待
        if tokens <= self.tokens:
            return 0.0
        
        # 计算需要等待多长时间才能获得足够的令牌
        additional_tokens_needed = tokens - self.tokens
        wait_time = additional_tokens_needed / self.fill_rate
        
        return wait_time

class RateLimiter:
    """速率限制器"""
    
    def __init__(self):
        """初始化速率限制器"""
        # 按IP地址存储令牌桶
        self.ip_buckets: Dict[str, TokenBucket] = {}
        
        # 按用户ID存储令牌桶
        self.user_buckets: Dict[str, TokenBucket] = {}
        
        # 按端点存储令牌桶
        self.endpoint_buckets: Dict[str, TokenBucket] = {}
        
        # 全局令牌桶
        self.global_bucket = TokenBucket(1000, 100, 1000)  # 每秒100个请求，最多1000个并发请求
        
        # 配置
        self.default_ip_tokens = 10  # 每个IP默认每秒允许的请求数
        self.default_user_tokens = 20  # 每个用户默认每秒允许的请求数
        self.default_endpoint_tokens = 50  # 每个端点默认每秒允许的请求数
        
        # 端点限制配置
        self.endpoint_limits: Dict[str, Tuple[int, int]] = {
            # 路径: (每秒请求数, 突发请求数)
            "/api/users": (20, 30),  # 用户查询API限制
            "/api/users/register": (5, 10),  # 注册API严格限制
            "/api/token": (10, 15),  # 令牌获取API限制
        }
        
        # IP黑名单
        self.blacklisted_ips: List[str] = []
        
        # 锁，用于同步访问
        self.lock = asyncio.Lock()
    
    async def configure_endpoint(self, path: str, rate: int, burst: int):
        """
        配置端点限制
        
        Args:
            path: API路径
            rate: 每秒请求数
            burst: 突发请求数
        """
        async with self.lock:
            self.endpoint_limits[path] = (rate, burst)
            # 如果已经有该端点的令牌桶，更新它
            if path in self.endpoint_buckets:
                # 只有在配置变更时才更新
                current_bucket = self.endpoint_buckets[path]
                if current_bucket.fill_rate != float(rate) or current_bucket.capacity != float(burst):
                    self.endpoint_buckets[path] = TokenBucket(burst, rate, burst)
    
    async def blacklist_ip(self, ip: str):
        """
        将IP加入黑名单
        
        Args:
            ip: IP地址
        """
        async with self.lock:
            if ip not in self.blacklisted_ips:
                self.blacklisted_ips.append(ip)
                logger.warning(f"IP {ip} 已加入黑名单")
    
    async def remove_from_blacklist(self, ip: str):
        """
        将IP从黑名单中移除
        
        Args:
            ip: IP地址
        """
        async with self.lock:
            if ip in self.blacklisted_ips:
                self.blacklisted_ips.remove(ip)
                logger.info(f"IP {ip} 已从黑名单中移除")
    
    async def is_allowed(
        self, 
        ip: str, 
        user_id: Optional[str] = None, 
        path: str = "/", 
        tokens: float = 1.0
    ) -> Tuple[bool, float, str]:
        """
        检查请求是否允许通过速率限制
        
        Args:
            ip: 客户端IP地址
            user_id: 用户ID（如果已认证）
            path: API路径
            tokens: 消耗的令牌数量
        
        Returns:
            Tuple[bool, float, str]: (是否允许, 需要等待的时间, 限制原因)
        """
        # 检查IP黑名单
        if ip in self.blacklisted_ips:
            return False, 3600, "ip_blacklisted"  # 黑名单中的IP默认等待1小时
        
        # 先检查全局限制
        if not self.global_bucket.consume(tokens):
            wait_time = self.global_bucket.get_wait_time(tokens)
            return False, wait_time, "global_limit"
        
        # 检查IP限制
        async with self.lock:
            # 如果是该IP的第一个请求，创建新的令牌桶
            if ip not in self.ip_buckets:
                self.ip_buckets[ip] = TokenBucket(
                    self.default_ip_tokens, 
                    self.default_ip_tokens / 2,  # 每2秒填充满
                    self.default_ip_tokens
                )
            
            ip_bucket = self.ip_buckets[ip]
            if not ip_bucket.consume(tokens):
                wait_time = ip_bucket.get_wait_time(tokens)
                return False, wait_time, "ip_limit"
        
        # 如果有用户ID，检查用户限制
        if user_id:
            async with self.lock:
                # 如果是该用户的第一个请求，创建新的令牌桶
                if user_id not in self.user_buckets:
                    self.user_buckets[user_id] = TokenBucket(
                        self.default_user_tokens, 
                        self.default_user_tokens / 2,  # 每2秒填充满
                        self.default_user_tokens
                    )
                
                user_bucket = self.user_buckets[user_id]
                if not user_bucket.consume(tokens):
                    wait_time = user_bucket.get_wait_time(tokens)
                    return False, wait_time, "user_limit"
        
        # 检查端点限制
        path_key = None
        for endpoint in self.endpoint_limits:
            if path.startswith(endpoint):
                path_key = endpoint
                break
        
        if path_key:
            async with self.lock:
                # 如果是该端点的第一个请求，创建新的令牌桶
                if path_key not in self.endpoint_buckets:
                    rate, burst = self.endpoint_limits[path_key]
                    self.endpoint_buckets[path_key] = TokenBucket(burst, rate, burst)
                
                endpoint_bucket = self.endpoint_buckets[path_key]
                if not endpoint_bucket.consume(tokens):
                    wait_time = endpoint_bucket.get_wait_time(tokens)
                    return False, wait_time, "endpoint_limit"
        
        # 所有检查都通过
        return True, 0, "allowed"

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    速率限制中间件
    限制API请求频率，防止滥用
    """
    
    def __init__(
        self, 
        app: ASGIApp, 
        limiter: Optional[RateLimiter] = None,
        exclude_paths: Optional[List[str]] = None
    ):
        """
        初始化中间件
        
        Args:
            app: ASGI应用
            limiter: 速率限制器实例
            exclude_paths: 排除的路径列表（不检查限制）
        """
        super().__init__(app)
        self.limiter = limiter or RateLimiter()
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        处理请求
        
        Args:
            request: FastAPI请求对象
            call_next: 调用下一个中间件
            
        Returns:
            Response: 响应对象
        """
        path = request.url.path
        
        # 跳过排除的路径
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            return await call_next(request)
        
        # 获取客户端IP
        client_ip = self._get_client_ip(request)
        
        # 获取用户ID（如果已认证）
        user_id = None
        try:
            # 从认证头中获取用户ID
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                from jose import jwt
                token = auth_header.split(" ")[1]
                # JWT密钥应该从配置中获取
                from pkg.middleware.rbac import JWT_SECRET_KEY, JWT_ALGORITHM
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
                user_id = payload.get("sub")
        except Exception as e:
            # 如果无法解析令牌，忽略错误，视为未认证请求
            logger.debug(f"无法获取用户ID: {str(e)}")
        
        # 检查请求是否允许
        is_allowed, wait_time, reason = await self.limiter.is_allowed(
            ip=client_ip,
            user_id=user_id,
            path=path,
            tokens=1.0  # 默认每个请求消耗1个令牌
        )
        
        if not is_allowed:
            # 记录速率限制命中
            prometheus_metrics.record_rate_limit_hit(path)
            
            # 记录速率限制事件
            logger.warning(
                f"速率限制: IP={client_ip}, 用户ID={user_id}, 路径={path}, 原因={reason}",
                extra={
                    "client_ip": client_ip,
                    "user_id": user_id,
                    "path": path,
                    "reason": reason,
                    "wait_time": wait_time
                }
            )
            
            # 返回速率限制响应
            retry_after = int(wait_time) + 1
            resp = Response(
                content=f"{{'error': '请求过于频繁', 'reason': '{reason}', 'retry_after': {retry_after}}}",
                status_code=429,
                headers={
                    "Content-Type": "application/json",
                    "Retry-After": str(retry_after)
                }
            )
            return resp
        
        # 请求被允许，继续处理
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """
        获取客户端真实IP地址
        处理代理情况
        
        Args:
            request: FastAPI请求对象
            
        Returns:
            str: 客户端IP地址
        """
        # 尝试从X-Forwarded-For头获取
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # 取第一个IP（最接近客户端的IP）
            return forwarded_for.split(",")[0].strip()
        
        # 尝试从X-Real-IP头获取
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # 如果没有代理头，使用连接的客户端地址
        client = request.client
        if client and client.host:
            return client.host
        
        # 默认
        return "unknown"

def add_rate_limit_middleware(app: FastAPI) -> RateLimiter:
    """
    将速率限制中间件添加到FastAPI应用
    
    Args:
        app: FastAPI应用实例
        
    Returns:
        RateLimiter: 速率限制器实例，可用于动态配置
    """
    limiter = RateLimiter()
    app.add_middleware(
        RateLimitMiddleware,
        limiter=limiter,
        exclude_paths=["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]
    )
    return limiter 