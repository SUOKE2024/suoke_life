#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
增强的安全模块
包含JWT安全验证、智能限流、请求签名验证和DDoS防护
"""

import asyncio
import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict, deque
from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_429_TOO_MANY_REQUESTS

logger = logging.getLogger(__name__)


@dataclass
class SecurityConfig:
    """安全配置"""
    # JWT配置
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    jwt_issuer: str = "suoke-life"
    jwt_audience: str = "suoke-api"
    
    # 限流配置
    rate_limit_enabled: bool = True
    default_rate_limit: int = 100  # 每分钟请求数
    burst_limit: int = 200  # 突发限制
    rate_limit_window: int = 60  # 时间窗口（秒）
    
    # DDoS防护
    ddos_protection_enabled: bool = True
    max_requests_per_ip: int = 1000  # 每小时每IP最大请求数
    suspicious_threshold: int = 500  # 可疑阈值
    block_duration: int = 3600  # 封禁时长（秒）
    
    # 请求签名
    signature_verification_enabled: bool = False
    signature_header: str = "X-Signature"
    timestamp_header: str = "X-Timestamp"
    signature_tolerance: int = 300  # 时间戳容忍度（秒）


@dataclass
class RateLimitRule:
    """限流规则"""
    pattern: str
    limit: int
    window: int
    burst: int = 0
    priority: int = 0


@dataclass
class SecurityMetrics:
    """安全指标"""
    total_requests: int = 0
    blocked_requests: int = 0
    rate_limited_requests: int = 0
    invalid_tokens: int = 0
    signature_failures: int = 0
    suspicious_ips: Set[str] = field(default_factory=set)
    blocked_ips: Set[str] = field(default_factory=set)


class TokenBucket:
    """令牌桶算法实现"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """消费令牌"""
        async with self._lock:
            now = time.time()
            # 添加令牌
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now
            
            # 检查是否有足够令牌
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False


class SlidingWindowCounter:
    """滑动窗口计数器"""
    
    def __init__(self, window_size: int, max_requests: int):
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests = deque()
        self._lock = asyncio.Lock()
    
    async def is_allowed(self) -> bool:
        """检查是否允许请求"""
        async with self._lock:
            now = time.time()
            
            # 清理过期请求
            while self.requests and self.requests[0] <= now - self.window_size:
                self.requests.popleft()
            
            # 检查请求数量
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            
            return False


class EnhancedJWTHandler:
    """增强的JWT处理器"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.security = HTTPBearer()
        self.blacklisted_tokens: Set[str] = set()
        self.token_usage: Dict[str, int] = defaultdict(int)
    
    async def create_access_token(self, data: Dict[str, Any]) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.config.jwt_access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": self.config.jwt_issuer,
            "aud": self.config.jwt_audience,
            "type": "access"
        })
        
        return jwt.encode(to_encode, self.config.jwt_secret_key, algorithm=self.config.jwt_algorithm)
    
    async def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """创建刷新令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.config.jwt_refresh_token_expire_days)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": self.config.jwt_issuer,
            "aud": self.config.jwt_audience,
            "type": "refresh"
        })
        
        return jwt.encode(to_encode, self.config.jwt_secret_key, algorithm=self.config.jwt_algorithm)
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """验证令牌"""
        try:
            # 检查黑名单
            if token in self.blacklisted_tokens:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="令牌已被撤销"
                )
            
            # 解码令牌
            payload = jwt.decode(
                token,
                self.config.jwt_secret_key,
                algorithms=[self.config.jwt_algorithm],
                issuer=self.config.jwt_issuer,
                audience=self.config.jwt_audience
            )
            
            # 检查令牌类型
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="无效的令牌类型"
                )
            
            # 记录令牌使用
            token_id = payload.get("jti", token[:16])
            self.token_usage[token_id] += 1
            
            # 检查异常使用（可能的重放攻击）
            if self.token_usage[token_id] > 1000:  # 阈值可配置
                logger.warning(f"令牌使用次数异常: {token_id}")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="令牌已过期"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=f"无效令牌: {str(e)}"
            )
    
    async def revoke_token(self, token: str):
        """撤销令牌"""
        self.blacklisted_tokens.add(token)
        
        # 清理过期的黑名单令牌
        if len(self.blacklisted_tokens) > 10000:
            await self._cleanup_blacklist()
    
    async def _cleanup_blacklist(self):
        """清理黑名单"""
        valid_tokens = set()
        
        for token in self.blacklisted_tokens:
            try:
                jwt.decode(
                    token,
                    self.config.jwt_secret_key,
                    algorithms=[self.config.jwt_algorithm],
                    options={"verify_exp": True}
                )
                valid_tokens.add(token)
            except jwt.ExpiredSignatureError:
                # 过期令牌可以从黑名单移除
                pass
            except jwt.InvalidTokenError:
                # 无效令牌也可以移除
                pass
        
        self.blacklisted_tokens = valid_tokens


class SmartRateLimiter:
    """智能限流器"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.rules: List[RateLimitRule] = []
        self.buckets: Dict[str, TokenBucket] = {}
        self.counters: Dict[str, SlidingWindowCounter] = {}
        self.ip_requests: Dict[str, deque] = defaultdict(lambda: deque())
        self._lock = asyncio.Lock()
    
    def add_rule(self, pattern: str, limit: int, window: int, burst: int = 0, priority: int = 0):
        """添加限流规则"""
        rule = RateLimitRule(pattern, limit, window, burst, priority)
        
        # 按优先级插入
        inserted = False
        for i, existing_rule in enumerate(self.rules):
            if rule.priority > existing_rule.priority:
                self.rules.insert(i, rule)
                inserted = True
                break
        
        if not inserted:
            self.rules.append(rule)
        
        logger.info(f"添加限流规则: {pattern}, 限制: {limit}/{window}s")
    
    async def is_allowed(self, request: Request) -> Tuple[bool, Optional[str]]:
        """检查请求是否被允许"""
        if not self.config.rate_limit_enabled:
            return True, None
        
        client_ip = self._get_client_ip(request)
        path = request.url.path
        
        # 检查IP级别限流
        if not await self._check_ip_rate_limit(client_ip):
            return False, "IP限流"
        
        # 检查路径级别限流
        for rule in self.rules:
            if self._match_pattern(path, rule.pattern):
                key = f"{client_ip}:{rule.pattern}"
                
                if not await self._check_rule_limit(key, rule):
                    return False, f"路径限流: {rule.pattern}"
        
        # 检查默认限流
        default_key = f"{client_ip}:default"
        if not await self._check_default_limit(default_key):
            return False, "默认限流"
        
        return True, None
    
    async def _check_ip_rate_limit(self, ip: str) -> bool:
        """检查IP级别限流"""
        async with self._lock:
            now = time.time()
            requests = self.ip_requests[ip]
            
            # 清理过期请求
            while requests and requests[0] <= now - 3600:  # 1小时窗口
                requests.popleft()
            
            # 检查请求数量
            if len(requests) < self.config.max_requests_per_ip:
                requests.append(now)
                return True
            
            return False
    
    async def _check_rule_limit(self, key: str, rule: RateLimitRule) -> bool:
        """检查规则限流"""
        if key not in self.counters:
            self.counters[key] = SlidingWindowCounter(rule.window, rule.limit)
        
        return await self.counters[key].is_allowed()
    
    async def _check_default_limit(self, key: str) -> bool:
        """检查默认限流"""
        if key not in self.buckets:
            self.buckets[key] = TokenBucket(
                self.config.burst_limit,
                self.config.default_rate_limit / 60.0  # 每秒速率
            )
        
        return await self.buckets[key].consume()
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        # 检查代理头部
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _match_pattern(self, path: str, pattern: str) -> bool:
        """匹配路径模式"""
        import re
        try:
            return bool(re.match(pattern, path))
        except re.error:
            return path.startswith(pattern)


class DDoSProtector:
    """DDoS防护器"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.ip_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "requests": deque(),
            "blocked_until": 0,
            "suspicious_score": 0
        })
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, request: Request) -> Tuple[bool, Optional[str]]:
        """检查请求是否被允许"""
        if not self.config.ddos_protection_enabled:
            return True, None
        
        client_ip = self._get_client_ip(request)
        
        async with self._lock:
            now = time.time()
            stats = self.ip_stats[client_ip]
            
            # 检查是否在封禁期
            if stats["blocked_until"] > now:
                return False, "IP已被封禁"
            
            # 清理过期请求
            requests = stats["requests"]
            while requests and requests[0] <= now - 3600:  # 1小时窗口
                requests.popleft()
            
            # 添加当前请求
            requests.append(now)
            
            # 检查请求频率
            if len(requests) > self.config.max_requests_per_ip:
                stats["blocked_until"] = now + self.config.block_duration
                stats["suspicious_score"] += 10
                logger.warning(f"IP {client_ip} 因请求过多被封禁")
                return False, "请求频率过高"
            
            # 检查可疑行为
            if len(requests) > self.config.suspicious_threshold:
                stats["suspicious_score"] += 1
                
                # 如果可疑分数过高，临时封禁
                if stats["suspicious_score"] > 50:
                    stats["blocked_until"] = now + 300  # 5分钟临时封禁
                    logger.warning(f"IP {client_ip} 因可疑行为被临时封禁")
                    return False, "可疑行为"
        
        return True, None
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def unblock_ip(self, ip: str):
        """解封IP"""
        async with self._lock:
            if ip in self.ip_stats:
                self.ip_stats[ip]["blocked_until"] = 0
                self.ip_stats[ip]["suspicious_score"] = 0
                logger.info(f"IP {ip} 已解封")


class RequestSignatureVerifier:
    """请求签名验证器"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
    
    async def verify_signature(self, request: Request, secret_key: str) -> bool:
        """验证请求签名"""
        if not self.config.signature_verification_enabled:
            return True
        
        try:
            # 获取签名和时间戳
            signature = request.headers.get(self.config.signature_header)
            timestamp = request.headers.get(self.config.timestamp_header)
            
            if not signature or not timestamp:
                return False
            
            # 检查时间戳
            try:
                request_time = int(timestamp)
                current_time = int(time.time())
                
                if abs(current_time - request_time) > self.config.signature_tolerance:
                    logger.warning("请求时间戳超出容忍范围")
                    return False
            except ValueError:
                logger.warning("无效的时间戳格式")
                return False
            
            # 构建签名字符串
            method = request.method
            path = request.url.path
            query = str(request.url.query) if request.url.query else ""
            
            # 获取请求体
            body = await request.body()
            body_str = body.decode('utf-8') if body else ""
            
            # 构建待签名字符串
            string_to_sign = f"{method}\n{path}\n{query}\n{body_str}\n{timestamp}"
            
            # 计算签名
            expected_signature = hmac.new(
                secret_key.encode('utf-8'),
                string_to_sign.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # 比较签名（防时序攻击）
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"签名验证失败: {e}")
            return False


class EnhancedSecurityManager:
    """增强安全管理器"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.jwt_handler = EnhancedJWTHandler(config)
        self.rate_limiter = SmartRateLimiter(config)
        self.ddos_protector = DDoSProtector(config)
        self.signature_verifier = RequestSignatureVerifier(config)
        self.metrics = SecurityMetrics()
        
        # 后台任务
        self._background_tasks: List[asyncio.Task] = []
        self._running = False
    
    async def start(self):
        """启动安全管理器"""
        if self._running:
            return
        
        # 启动后台清理任务
        self._background_tasks.append(
            asyncio.create_task(self._cleanup_loop())
        )
        
        self._running = True
        logger.info("增强安全管理器已启动")
    
    async def stop(self):
        """停止安全管理器"""
        if not self._running:
            return
        
        self._running = False
        
        # 取消后台任务
        for task in self._background_tasks:
            task.cancel()
        
        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        logger.info("增强安全管理器已停止")
    
    async def authenticate_request(self, request: Request) -> Dict[str, Any]:
        """认证请求"""
        self.metrics.total_requests += 1
        
        try:
            # 获取授权头
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="缺少或无效的授权头"
                )
            
            token = authorization.split(" ")[1]
            payload = await self.jwt_handler.verify_token(token)
            
            return payload
            
        except HTTPException:
            self.metrics.invalid_tokens += 1
            raise
        except Exception as e:
            self.metrics.invalid_tokens += 1
            logger.error(f"认证失败: {e}")
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="认证失败"
            )
    
    async def check_rate_limit(self, request: Request):
        """检查限流"""
        allowed, reason = await self.rate_limiter.is_allowed(request)
        
        if not allowed:
            self.metrics.rate_limited_requests += 1
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail=f"请求过于频繁: {reason}"
            )
    
    async def check_ddos_protection(self, request: Request):
        """检查DDoS防护"""
        allowed, reason = await self.ddos_protector.is_allowed(request)
        
        if not allowed:
            self.metrics.blocked_requests += 1
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                detail=f"请求被阻止: {reason}"
            )
    
    async def verify_request_signature(self, request: Request, secret_key: str):
        """验证请求签名"""
        if not await self.signature_verifier.verify_signature(request, secret_key):
            self.metrics.signature_failures += 1
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="请求签名验证失败"
            )
    
    async def _cleanup_loop(self):
        """清理循环"""
        while self._running:
            try:
                await self._perform_cleanup()
                await asyncio.sleep(3600)  # 每小时清理一次
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"清理任务失败: {e}")
    
    async def _perform_cleanup(self):
        """执行清理"""
        # 清理JWT黑名单
        await self.jwt_handler._cleanup_blacklist()
        
        # 清理过期的限流数据
        current_time = time.time()
        
        # 清理令牌桶
        expired_buckets = [
            key for key, bucket in self.rate_limiter.buckets.items()
            if current_time - bucket.last_refill > 3600
        ]
        for key in expired_buckets:
            del self.rate_limiter.buckets[key]
        
        # 清理DDoS统计
        expired_ips = [
            ip for ip, stats in self.ddos_protector.ip_stats.items()
            if (current_time - stats["blocked_until"] > 86400 and  # 24小时后清理
                len(stats["requests"]) == 0)
        ]
        for ip in expired_ips:
            del self.ddos_protector.ip_stats[ip]
        
        logger.debug("安全数据清理完成")
    
    def get_security_stats(self) -> Dict[str, Any]:
        """获取安全统计"""
        return {
            "total_requests": self.metrics.total_requests,
            "blocked_requests": self.metrics.blocked_requests,
            "rate_limited_requests": self.metrics.rate_limited_requests,
            "invalid_tokens": self.metrics.invalid_tokens,
            "signature_failures": self.metrics.signature_failures,
            "suspicious_ips_count": len(self.metrics.suspicious_ips),
            "blocked_ips_count": len(self.metrics.blocked_ips),
            "blacklisted_tokens": len(self.jwt_handler.blacklisted_tokens),
            "rate_limit_rules": len(self.rate_limiter.rules)
        } 