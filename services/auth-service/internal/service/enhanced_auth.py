#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强认证服务
支持JWT增强、OAuth2集成、账户安全保护等功能
"""

import jwt
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import aioredis
import bcrypt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

logger = logging.getLogger(__name__)

class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    ID = "id"

@dataclass
class UserClaims:
    user_id: str
    username: str
    email: str
    roles: List[str]
    permissions: List[str]
    session_id: str
    device_id: str = None
    ip_address: str = None

class EnhancedAuthService:
    """增强认证服务"""
    
    def __init__(self, redis_client: aioredis.Redis, config: Dict[str, Any]):
        self.redis = redis_client
        self.config = config
        
        # JWT配置
        self.jwt_secret = config.get("jwt_secret")
        self.jwt_algorithm = config.get("jwt_algorithm", "HS256")
        self.access_token_expire = config.get("access_token_expire", 3600)  # 1小时
        self.refresh_token_expire = config.get("refresh_token_expire", 86400 * 7)  # 7天
        
        # OAuth2配置
        self.oauth2_providers = config.get("oauth2_providers", {})
        
        # 安全配置
        self.max_login_attempts = config.get("max_login_attempts", 5)
        self.lockout_duration = config.get("lockout_duration", 900)  # 15分钟
        
    async def authenticate_user(self, username: str, password: str, 
                               device_info: Dict[str, str] = None) -> Dict[str, Any]:
        """用户认证"""
        try:
            # 检查账户锁定状态
            if await self._is_account_locked(username):
                return {
                    "success": False,
                    "error": "account_locked",
                    "message": "账户已被锁定，请稍后再试"
                }
            
            # 验证用户凭据
            user = await self._verify_credentials(username, password)
            if not user:
                await self._record_failed_attempt(username)
                return {
                    "success": False,
                    "error": "invalid_credentials",
                    "message": "用户名或密码错误"
                }
            
            # 清除失败尝试记录
            await self._clear_failed_attempts(username)
            
            # 创建会话
            session_id = await self._create_session(user["user_id"], device_info)
            
            # 生成令牌
            tokens = await self._generate_tokens(user, session_id, device_info)
            
            # 记录登录日志
            await self._log_login_event(user["user_id"], device_info, "success")
            
            return {
                "success": True,
                "user": user,
                "tokens": tokens,
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {
                "success": False,
                "error": "internal_error",
                "message": "认证服务内部错误"
            }
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """刷新令牌"""
        try:
            # 验证刷新令牌
            payload = jwt.decode(refresh_token, self.jwt_secret, 
                               algorithms=[self.jwt_algorithm])
            
            if payload.get("type") != TokenType.REFRESH.value:
                return {
                    "success": False,
                    "error": "invalid_token_type",
                    "message": "无效的令牌类型"
                }
            
            # 检查会话状态
            session_id = payload.get("session_id")
            if not await self._is_session_valid(session_id):
                return {
                    "success": False,
                    "error": "invalid_session",
                    "message": "会话已失效"
                }
            
            # 获取用户信息
            user_id = payload.get("user_id")
            user = await self._get_user_by_id(user_id)
            
            if not user:
                return {
                    "success": False,
                    "error": "user_not_found",
                    "message": "用户不存在"
                }
            
            # 生成新的访问令牌
            access_token = await self._generate_access_token(user, session_id)
            
            return {
                "success": True,
                "access_token": access_token,
                "expires_in": self.access_token_expire
            }
            
        except jwt.ExpiredSignatureError:
            return {
                "success": False,
                "error": "token_expired",
                "message": "刷新令牌已过期"
            }
        except jwt.InvalidTokenError:
            return {
                "success": False,
                "error": "invalid_token",
                "message": "无效的刷新令牌"
            }
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self.jwt_secret, 
                               algorithms=[self.jwt_algorithm])
            
            # 检查令牌类型
            if payload.get("type") != TokenType.ACCESS.value:
                return {
                    "valid": False,
                    "error": "invalid_token_type"
                }
            
            # 检查会话状态
            session_id = payload.get("session_id")
            if not await self._is_session_valid(session_id):
                return {
                    "valid": False,
                    "error": "session_expired"
                }
            
            # 构建用户声明
            claims = UserClaims(
                user_id=payload.get("user_id"),
                username=payload.get("username"),
                email=payload.get("email"),
                roles=payload.get("roles", []),
                permissions=payload.get("permissions", []),
                session_id=session_id,
                device_id=payload.get("device_id"),
                ip_address=payload.get("ip_address")
            )
            
            return {
                "valid": True,
                "claims": claims,
                "expires_at": payload.get("exp")
            }
            
        except jwt.ExpiredSignatureError:
            return {
                "valid": False,
                "error": "token_expired"
            }
        except jwt.InvalidTokenError:
            return {
                "valid": False,
                "error": "invalid_token"
            }
    
    async def logout(self, session_id: str) -> bool:
        """用户登出"""
        try:
            # 删除会话
            await self.redis.delete(f"session:{session_id}")
            
            # 将令牌加入黑名单
            await self._blacklist_session_tokens(session_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
    
    async def _generate_tokens(self, user: Dict[str, Any], session_id: str,
                              device_info: Dict[str, str] = None) -> Dict[str, str]:
        """生成令牌"""
        now = datetime.utcnow()
        
        # 基础载荷
        base_payload = {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "roles": user.get("roles", []),
            "permissions": user.get("permissions", []),
            "session_id": session_id,
            "iat": now,
        }
        
        if device_info:
            base_payload.update({
                "device_id": device_info.get("device_id"),
                "ip_address": device_info.get("ip_address")
            })
        
        # 访问令牌
        access_payload = {
            **base_payload,
            "type": TokenType.ACCESS.value,
            "exp": now + timedelta(seconds=self.access_token_expire)
        }
        access_token = jwt.encode(access_payload, self.jwt_secret, 
                                algorithm=self.jwt_algorithm)
        
        # 刷新令牌
        refresh_payload = {
            **base_payload,
            "type": TokenType.REFRESH.value,
            "exp": now + timedelta(seconds=self.refresh_token_expire)
        }
        refresh_token = jwt.encode(refresh_payload, self.jwt_secret,
                                 algorithm=self.jwt_algorithm)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": self.access_token_expire
        }
    
    async def _generate_access_token(self, user: Dict[str, Any], session_id: str) -> str:
        """生成访问令牌"""
        now = datetime.utcnow()
        
        payload = {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "roles": user.get("roles", []),
            "permissions": user.get("permissions", []),
            "session_id": session_id,
            "type": TokenType.ACCESS.value,
            "iat": now,
            "exp": now + timedelta(seconds=self.access_token_expire)
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    async def _verify_credentials(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """验证用户凭据"""
        # 这里应该连接到用户数据库进行验证
        # 示例实现
        user_data = await self.redis.hgetall(f"user:{username}")
        if not user_data:
            return None
        
        stored_password = user_data.get("password")
        if not stored_password:
            return None
        
        # 验证密码
        if bcrypt.checkpw(password.encode(), stored_password.encode()):
            return {
                "user_id": user_data.get("user_id"),
                "username": username,
                "email": user_data.get("email"),
                "roles": user_data.get("roles", "").split(","),
                "permissions": user_data.get("permissions", "").split(",")
            }
        
        return None
    
    async def _get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """根据用户ID获取用户信息"""
        user_data = await self.redis.hgetall(f"user_id:{user_id}")
        if not user_data:
            return None
        
        return {
            "user_id": user_id,
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "roles": user_data.get("roles", "").split(","),
            "permissions": user_data.get("permissions", "").split(",")
        }
    
    async def _is_account_locked(self, username: str) -> bool:
        """检查账户是否被锁定"""
        lock_key = f"account_lock:{username}"
        lock_data = await self.redis.get(lock_key)
        
        if not lock_data:
            return False
        
        lock_time = float(lock_data)
        return (datetime.utcnow().timestamp() - lock_time) < self.lockout_duration
    
    async def _record_failed_attempt(self, username: str):
        """记录失败尝试"""
        attempts_key = f"login_attempts:{username}"
        attempts = await self.redis.incr(attempts_key)
        await self.redis.expire(attempts_key, self.lockout_duration)
        
        if attempts >= self.max_login_attempts:
            # 锁定账户
            lock_key = f"account_lock:{username}"
            await self.redis.setex(lock_key, self.lockout_duration, 
                                 datetime.utcnow().timestamp())
    
    async def _clear_failed_attempts(self, username: str):
        """清除失败尝试记录"""
        attempts_key = f"login_attempts:{username}"
        await self.redis.delete(attempts_key)
    
    async def _create_session(self, user_id: str, device_info: Dict[str, str] = None) -> str:
        """创建会话"""
        import uuid
        session_id = str(uuid.uuid4())
        
        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "device_info": device_info or {}
        }
        
        await self.redis.setex(f"session:{session_id}", 
                              self.refresh_token_expire, 
                              str(session_data))
        
        return session_id
    
    async def _is_session_valid(self, session_id: str) -> bool:
        """检查会话是否有效"""
        session_data = await self.redis.get(f"session:{session_id}")
        return session_data is not None
    
    async def _blacklist_session_tokens(self, session_id: str):
        """将会话令牌加入黑名单"""
        blacklist_key = f"blacklist:session:{session_id}"
        await self.redis.setex(blacklist_key, self.refresh_token_expire, "1")
    
    async def _log_login_event(self, user_id: str, device_info: Dict[str, str], status: str):
        """记录登录事件"""
        event_data = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": status,
            "device_info": device_info or {},
            "ip_address": device_info.get("ip_address") if device_info else None
        }
        
        # 记录到日志流
        await self.redis.xadd("auth_events", event_data) 