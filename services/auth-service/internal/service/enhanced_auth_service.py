#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版认证服务
集成JWT密钥轮换、令牌黑名单、会话管理优化等功能
"""

import asyncio
import logging
import time
import jwt
import hashlib
import secrets
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import redis.asyncio as redis

# 导入通用组件
from services.common.governance.circuit_breaker import (
    CircuitBreaker, CircuitBreakerConfig, get_circuit_breaker
)
from services.common.governance.rate_limiter import (
    RateLimitConfig, get_rate_limiter, rate_limit
)
from services.common.observability.tracing import (
    get_tracer, trace, SpanKind
)
from services.common.security.encryption import (
    encrypt_data, decrypt_data, hash_password, verify_password
)

logger = logging.getLogger(__name__)

class AuthMethod(Enum):
    """认证方法"""
    PASSWORD = "password"
    OAUTH2 = "oauth2"
    SAML = "saml"
    MFA = "mfa"
    BIOMETRIC = "biometric"

class TokenType(Enum):
    """令牌类型"""
    ACCESS = "access"
    REFRESH = "refresh"
    ID = "id"

@dataclass
class AuthRequest:
    """认证请求"""
    username: str
    password: Optional[str] = None
    auth_method: AuthMethod = AuthMethod.PASSWORD
    mfa_code: Optional[str] = None
    device_id: Optional[str] = None
    client_ip: str = ""
    user_agent: str = ""

@dataclass
class TokenRequest:
    """令牌请求"""
    grant_type: str  # password, refresh_token, authorization_code
    username: Optional[str] = None
    password: Optional[str] = None
    refresh_token: Optional[str] = None
    code: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    scope: Optional[List[str]] = None

@dataclass
class AuthResponse:
    """认证响应"""
    success: bool
    user_id: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    id_token: Optional[str] = None
    expires_in: int = 3600
    token_type: str = "Bearer"
    scope: Optional[List[str]] = None
    mfa_required: bool = False
    error: Optional[str] = None

@dataclass
class Session:
    """会话信息"""
    session_id: str
    user_id: str
    created_at: float
    last_accessed: float
    expires_at: float
    device_id: Optional[str] = None
    ip_address: str = ""
    user_agent: str = ""
    is_active: bool = True

class EnhancedAuthService:
    """增强版认证服务"""
    
    def __init__(self):
        self.service_name = "auth-service"
        self.tracer = get_tracer(self.service_name)
        
        # JWT密钥管理
        self.jwt_keys = {
            'current': self._generate_jwt_key(),
            'previous': None,
            'rotation_time': time.time() + 86400  # 24小时轮换
        }
        
        # Redis连接池
        self.redis_pool = None
        
        # 初始化断路器配置
        self._init_circuit_breakers()
        
        # 初始化限流器配置
        self._init_rate_limiters()
        
        # 令牌配置
        self.token_config = {
            'access_token_ttl': 3600,      # 1小时
            'refresh_token_ttl': 2592000,  # 30天
            'id_token_ttl': 3600,          # 1小时
            'session_ttl': 86400,          # 24小时
        }
        
        # 安全配置
        self.security_config = {
            'max_login_attempts': 5,
            'lockout_duration': 900,  # 15分钟
            'password_min_length': 8,
            'password_require_special': True,
            'mfa_enabled': True,
        }
        
        # 统计信息
        self.stats = {
            'total_auth_requests': 0,
            'successful_auths': 0,
            'failed_auths': 0,
            'token_issued': 0,
            'token_refreshed': 0,
            'token_revoked': 0,
            'active_sessions': 0,
            'mfa_challenges': 0,
            'average_auth_time': 0.0
        }
        
        logger.info("增强版认证服务初始化完成")
    
    def _init_circuit_breakers(self):
        """初始化断路器配置"""
        self.circuit_breaker_configs = {
            'user_db': CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60.0,
                timeout=5.0
            ),
            'redis': CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30.0,
                timeout=3.0
            ),
            'mfa_service': CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=45.0,
                timeout=10.0
            )
        }
    
    def _init_rate_limiters(self):
        """初始化限流器配置"""
        self.rate_limit_configs = {
            'login': RateLimitConfig(rate=5.0, burst=10),      # 每分钟5次登录
            'token': RateLimitConfig(rate=20.0, burst=40),     # 每分钟20次令牌请求
            'refresh': RateLimitConfig(rate=10.0, burst=20),   # 每分钟10次刷新
            'mfa': RateLimitConfig(rate=3.0, burst=6),         # 每分钟3次MFA尝试
        }
    
    async def _get_redis_connection(self) -> redis.Redis:
        """获取Redis连接"""
        if not self.redis_pool:
            self.redis_pool = redis.ConnectionPool(
                host='localhost',
                port=6379,
                db=1,
                max_connections=50,
                decode_responses=True
            )
        return redis.Redis(connection_pool=self.redis_pool)
    
    def _generate_jwt_key(self) -> Dict[str, Any]:
        """生成JWT密钥"""
        return {
            'key': secrets.token_urlsafe(32),
            'kid': secrets.token_hex(8),
            'created_at': time.time()
        }
    
    async def _rotate_jwt_keys(self):
        """轮换JWT密钥"""
        if time.time() >= self.jwt_keys['rotation_time']:
            logger.info("开始JWT密钥轮换")
            self.jwt_keys['previous'] = self.jwt_keys['current']
            self.jwt_keys['current'] = self._generate_jwt_key()
            self.jwt_keys['rotation_time'] = time.time() + 86400
            
            # 通知其他服务密钥已轮换
            await self._notify_key_rotation()
    
    @trace(service_name="auth-service", kind=SpanKind.SERVER)
    async def authenticate(self, request: AuthRequest) -> AuthResponse:
        """
        用户认证
        
        Args:
            request: 认证请求
            
        Returns:
            AuthResponse: 认证响应
        """
        start_time = time.time()
        self.stats['total_auth_requests'] += 1
        
        try:
            # 限流检查
            limiter = await get_rate_limiter(
                f"{self.service_name}_login_{request.username}",
                config=self.rate_limit_configs['login']
            )
            
            if not await limiter.try_acquire():
                self.stats['failed_auths'] += 1
                return AuthResponse(
                    success=False,
                    error="Too many login attempts. Please try again later."
                )
            
            # 检查账户锁定状态
            if await self._is_account_locked(request.username):
                self.stats['failed_auths'] += 1
                return AuthResponse(
                    success=False,
                    error="Account is locked due to multiple failed attempts."
                )
            
            # 验证用户凭证
            user = await self._verify_credentials(request)
            if not user:
                await self._record_failed_attempt(request.username, request.client_ip)
                self.stats['failed_auths'] += 1
                return AuthResponse(
                    success=False,
                    error="Invalid username or password."
                )
            
            # 检查是否需要MFA
            if self.security_config['mfa_enabled'] and user.get('mfa_enabled'):
                if not request.mfa_code:
                    self.stats['mfa_challenges'] += 1
                    return AuthResponse(
                        success=False,
                        mfa_required=True,
                        error="MFA code required."
                    )
                
                # 验证MFA代码
                if not await self._verify_mfa_code(user['user_id'], request.mfa_code):
                    self.stats['failed_auths'] += 1
                    return AuthResponse(
                        success=False,
                        error="Invalid MFA code."
                    )
            
            # 创建会话
            session = await self._create_session(user['user_id'], request)
            
            # 生成令牌
            tokens = await self._generate_tokens(user, session)
            
            # 清除失败尝试记录
            await self._clear_failed_attempts(request.username)
            
            # 更新统计
            self.stats['successful_auths'] += 1
            self.stats['token_issued'] += 3  # access, refresh, id tokens
            self._update_average_auth_time(time.time() - start_time)
            
            return AuthResponse(
                success=True,
                user_id=user['user_id'],
                access_token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                id_token=tokens['id_token'],
                expires_in=self.token_config['access_token_ttl'],
                scope=user.get('scope', ['read', 'write'])
            )
            
        except Exception as e:
            self.stats['failed_auths'] += 1
            logger.error(f"认证失败: {e}")
            return AuthResponse(
                success=False,
                error="Authentication failed. Please try again."
            )
    
    @trace(operation_name="verify_credentials")
    async def _verify_credentials(self, request: AuthRequest) -> Optional[Dict[str, Any]]:
        """验证用户凭证"""
        # 使用断路器保护数据库查询
        breaker = await get_circuit_breaker(
            f"{self.service_name}_user_db",
            self.circuit_breaker_configs['user_db']
        )
        
        async with breaker.protect():
            # 模拟数据库查询
            await asyncio.sleep(0.1)
            
            # 这里应该查询真实的用户数据库
            # 示例用户数据
            if request.username == "test_user":
                stored_password_hash = hash_password("test_password")
                if verify_password(request.password, stored_password_hash):
                    return {
                        'user_id': 'user_12345',
                        'username': request.username,
                        'email': 'test@example.com',
                        'mfa_enabled': True,
                        'scope': ['read', 'write'],
                        'roles': ['user']
                    }
            
            return None
    
    async def _is_account_locked(self, username: str) -> bool:
        """检查账户是否被锁定"""
        redis_conn = await self._get_redis_connection()
        
        # 使用断路器保护Redis操作
        breaker = await get_circuit_breaker(
            f"{self.service_name}_redis",
            self.circuit_breaker_configs['redis']
        )
        
        async with breaker.protect():
            lockout_key = f"auth:lockout:{username}"
            lockout_time = await redis_conn.get(lockout_key)
            
            if lockout_time and float(lockout_time) > time.time():
                return True
            
            return False
    
    async def _record_failed_attempt(self, username: str, ip_address: str):
        """记录失败的登录尝试"""
        redis_conn = await self._get_redis_connection()
        
        async with get_circuit_breaker(f"{self.service_name}_redis", self.circuit_breaker_configs['redis']).protect():
            # 记录失败次数
            attempts_key = f"auth:attempts:{username}"
            attempts = await redis_conn.incr(attempts_key)
            await redis_conn.expire(attempts_key, 3600)  # 1小时过期
            
            # 如果超过最大尝试次数，锁定账户
            if attempts >= self.security_config['max_login_attempts']:
                lockout_key = f"auth:lockout:{username}"
                lockout_until = time.time() + self.security_config['lockout_duration']
                await redis_conn.set(lockout_key, lockout_until, ex=self.security_config['lockout_duration'])
                
                # 记录安全事件
                await self._log_security_event('account_locked', {
                    'username': username,
                    'ip_address': ip_address,
                    'attempts': attempts
                })
    
    async def _clear_failed_attempts(self, username: str):
        """清除失败尝试记录"""
        redis_conn = await self._get_redis_connection()
        
        async with get_circuit_breaker(f"{self.service_name}_redis", self.circuit_breaker_configs['redis']).protect():
            attempts_key = f"auth:attempts:{username}"
            await redis_conn.delete(attempts_key)
    
    async def _verify_mfa_code(self, user_id: str, mfa_code: str) -> bool:
        """验证MFA代码"""
        # 使用断路器保护MFA服务
        breaker = await get_circuit_breaker(
            f"{self.service_name}_mfa_service",
            self.circuit_breaker_configs['mfa_service']
        )
        
        async with breaker.protect():
            # 模拟MFA验证
            await asyncio.sleep(0.05)
            
            # 实际应该调用MFA服务或验证TOTP代码
            # 这里简化为固定代码验证
            return mfa_code == "123456"
    
    async def _create_session(self, user_id: str, request: AuthRequest) -> Session:
        """创建会话"""
        session_id = secrets.token_urlsafe(32)
        now = time.time()
        
        session = Session(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_accessed=now,
            expires_at=now + self.token_config['session_ttl'],
            device_id=request.device_id,
            ip_address=request.client_ip,
            user_agent=request.user_agent,
            is_active=True
        )
        
        # 存储会话到Redis
        redis_conn = await self._get_redis_connection()
        
        async with get_circuit_breaker(f"{self.service_name}_redis", self.circuit_breaker_configs['redis']).protect():
            session_key = f"auth:session:{session_id}"
            await redis_conn.hset(session_key, mapping={
                'user_id': session.user_id,
                'created_at': session.created_at,
                'last_accessed': session.last_accessed,
                'expires_at': session.expires_at,
                'device_id': session.device_id or '',
                'ip_address': session.ip_address,
                'user_agent': session.user_agent,
                'is_active': '1' if session.is_active else '0'
            })
            await redis_conn.expire(session_key, self.token_config['session_ttl'])
            
            # 更新活跃会话计数
            self.stats['active_sessions'] = await redis_conn.scard(f"auth:active_sessions:{user_id}")
        
        return session
    
    async def _generate_tokens(self, user: Dict[str, Any], session: Session) -> Dict[str, str]:
        """生成令牌"""
        # 确保密钥是最新的
        await self._rotate_jwt_keys()
        
        current_key = self.jwt_keys['current']
        now = datetime.utcnow()
        
        # 通用声明
        base_claims = {
            'iss': 'suoke-life',
            'sub': user['user_id'],
            'aud': 'suoke-life-api',
            'iat': now,
            'jti': secrets.token_hex(16),
            'sid': session.session_id
        }
        
        # 访问令牌
        access_claims = {
            **base_claims,
            'exp': now + timedelta(seconds=self.token_config['access_token_ttl']),
            'token_type': TokenType.ACCESS.value,
            'scope': ' '.join(user.get('scope', [])),
            'roles': user.get('roles', [])
        }
        access_token = jwt.encode(
            access_claims,
            current_key['key'],
            algorithm='HS256',
            headers={'kid': current_key['kid']}
        )
        
        # 刷新令牌
        refresh_claims = {
            **base_claims,
            'exp': now + timedelta(seconds=self.token_config['refresh_token_ttl']),
            'token_type': TokenType.REFRESH.value
        }
        refresh_token = jwt.encode(
            refresh_claims,
            current_key['key'],
            algorithm='HS256',
            headers={'kid': current_key['kid']}
        )
        
        # ID令牌（OpenID Connect）
        id_claims = {
            **base_claims,
            'exp': now + timedelta(seconds=self.token_config['id_token_ttl']),
            'token_type': TokenType.ID.value,
            'email': user.get('email'),
            'username': user.get('username'),
            'email_verified': user.get('email_verified', False)
        }
        id_token = jwt.encode(
            id_claims,
            current_key['key'],
            algorithm='HS256',
            headers={'kid': current_key['kid']}
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'id_token': id_token
        }
    
    @trace(operation_name="refresh_token")
    @rate_limit(name="refresh", tokens=1)
    async def refresh_token(self, refresh_token: str) -> AuthResponse:
        """刷新访问令牌"""
        try:
            # 验证刷新令牌
            claims = await self._verify_token(refresh_token, TokenType.REFRESH)
            if not claims:
                return AuthResponse(
                    success=False,
                    error="Invalid refresh token."
                )
            
            # 检查令牌是否在黑名单中
            if await self._is_token_blacklisted(claims['jti']):
                return AuthResponse(
                    success=False,
                    error="Token has been revoked."
                )
            
            # 获取用户信息
            user = await self._get_user_by_id(claims['sub'])
            if not user:
                return AuthResponse(
                    success=False,
                    error="User not found."
                )
            
            # 获取会话信息
            session = await self._get_session(claims['sid'])
            if not session or not session.is_active:
                return AuthResponse(
                    success=False,
                    error="Session expired or invalid."
                )
            
            # 更新会话最后访问时间
            await self._update_session_activity(session.session_id)
            
            # 生成新的访问令牌
            tokens = await self._generate_tokens(user, session)
            
            # 更新统计
            self.stats['token_refreshed'] += 1
            
            return AuthResponse(
                success=True,
                user_id=user['user_id'],
                access_token=tokens['access_token'],
                refresh_token=refresh_token,  # 保持原刷新令牌
                id_token=tokens['id_token'],
                expires_in=self.token_config['access_token_ttl'],
                scope=user.get('scope', ['read', 'write'])
            )
            
        except Exception as e:
            logger.error(f"令牌刷新失败: {e}")
            return AuthResponse(
                success=False,
                error="Failed to refresh token."
            )
    
    async def _verify_token(self, token: str, expected_type: TokenType) -> Optional[Dict[str, Any]]:
        """验证令牌"""
        try:
            # 先尝试用当前密钥验证
            header = jwt.get_unverified_header(token)
            kid = header.get('kid')
            
            # 选择正确的密钥
            if kid == self.jwt_keys['current']['kid']:
                key = self.jwt_keys['current']['key']
            elif self.jwt_keys['previous'] and kid == self.jwt_keys['previous']['kid']:
                key = self.jwt_keys['previous']['key']
            else:
                logger.warning(f"未知的密钥ID: {kid}")
                return None
            
            # 验证令牌
            claims = jwt.decode(
                token,
                key,
                algorithms=['HS256'],
                audience='suoke-life-api',
                issuer='suoke-life'
            )
            
            # 验证令牌类型
            if claims.get('token_type') != expected_type.value:
                logger.warning(f"令牌类型不匹配: 期望 {expected_type.value}, 实际 {claims.get('token_type')}")
                return None
            
            return claims
            
        except jwt.ExpiredSignatureError:
            logger.info("令牌已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"无效的令牌: {e}")
            return None
    
    async def revoke_token(self, token: str) -> bool:
        """撤销令牌"""
        try:
            # 解析令牌获取JTI
            header = jwt.get_unverified_header(token)
            claims = jwt.decode(token, options={"verify_signature": False})
            jti = claims.get('jti')
            
            if not jti:
                return False
            
            # 将JTI加入黑名单
            redis_conn = await self._get_redis_connection()
            
            async with get_circuit_breaker(f"{self.service_name}_redis", self.circuit_breaker_configs['redis']).protect():
                blacklist_key = f"auth:blacklist:{jti}"
                ttl = claims.get('exp', 0) - time.time()
                
                if ttl > 0:
                    await redis_conn.set(blacklist_key, '1', ex=int(ttl))
                    self.stats['token_revoked'] += 1
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"撤销令牌失败: {e}")
            return False
    
    async def _is_token_blacklisted(self, jti: str) -> bool:
        """检查令牌是否在黑名单中"""
        redis_conn = await self._get_redis_connection()
        
        async with get_circuit_breaker(f"{self.service_name}_redis", self.circuit_breaker_configs['redis']).protect():
            blacklist_key = f"auth:blacklist:{jti}"
            return await redis_conn.exists(blacklist_key) > 0
    
    async def _get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取用户信息"""
        # 使用断路器保护数据库查询
        breaker = await get_circuit_breaker(
            f"{self.service_name}_user_db",
            self.circuit_breaker_configs['user_db']
        )
        
        async with breaker.protect():
            # 模拟数据库查询
            await asyncio.sleep(0.05)
            
            # 返回示例用户数据
            if user_id == 'user_12345':
                return {
                    'user_id': user_id,
                    'username': 'test_user',
                    'email': 'test@example.com',
                    'mfa_enabled': True,
                    'scope': ['read', 'write'],
                    'roles': ['user']
                }
            
            return None
    
    async def _get_session(self, session_id: str) -> Optional[Session]:
        """获取会话信息"""
        redis_conn = await self._get_redis_connection()
        
        async with get_circuit_breaker(f"{self.service_name}_redis", self.circuit_breaker_configs['redis']).protect():
            session_key = f"auth:session:{session_id}"
            session_data = await redis_conn.hgetall(session_key)
            
            if not session_data:
                return None
            
            return Session(
                session_id=session_id,
                user_id=session_data['user_id'],
                created_at=float(session_data['created_at']),
                last_accessed=float(session_data['last_accessed']),
                expires_at=float(session_data['expires_at']),
                device_id=session_data.get('device_id') or None,
                ip_address=session_data['ip_address'],
                user_agent=session_data['user_agent'],
                is_active=session_data['is_active'] == '1'
            )
    
    async def _update_session_activity(self, session_id: str):
        """更新会话活动时间"""
        redis_conn = await self._get_redis_connection()
        
        async with get_circuit_breaker(f"{self.service_name}_redis", self.circuit_breaker_configs['redis']).protect():
            session_key = f"auth:session:{session_id}"
            await redis_conn.hset(session_key, 'last_accessed', time.time())
            await redis_conn.expire(session_key, self.token_config['session_ttl'])
    
    async def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """记录安全事件"""
        logger.warning(f"安全事件 [{event_type}]: {details}")
        
        # 可以将事件发送到安全监控系统
        # await self._send_to_security_monitor(event_type, details)
    
    async def _notify_key_rotation(self):
        """通知其他服务密钥已轮换"""
        # 可以通过消息队列或其他机制通知
        logger.info("JWT密钥轮换通知已发送")
    
    def _update_average_auth_time(self, auth_time: float):
        """更新平均认证时间"""
        total_auths = self.stats['successful_auths']
        if total_auths == 1:
            self.stats['average_auth_time'] = auth_time
        else:
            current_avg = self.stats['average_auth_time']
            self.stats['average_auth_time'] = (
                (current_avg * (total_auths - 1) + auth_time) / total_auths
            )
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取服务健康状态"""
        return {
            'service': self.service_name,
            'status': 'healthy',
            'stats': self.stats,
            'jwt_key_rotation': {
                'current_kid': self.jwt_keys['current']['kid'],
                'next_rotation': self.jwt_keys['rotation_time'] - time.time()
            },
            'uptime': time.time()
        }
    
    async def cleanup(self):
        """清理资源"""
        if self.redis_pool:
            await self.redis_pool.disconnect()
        
        logger.info("认证服务清理完成")

# 全局服务实例
_auth_service = None

async def get_auth_service() -> EnhancedAuthService:
    """获取认证服务实例"""
    global _auth_service
    if _auth_service is None:
        _auth_service = EnhancedAuthService()
    return _auth_service 