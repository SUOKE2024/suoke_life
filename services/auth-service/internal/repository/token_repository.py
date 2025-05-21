#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
令牌仓储实现
处理认证令牌的存储和管理
"""
import json
import logging
import time
from typing import Dict, Optional, Any, Tuple

import aioredis

from internal.model.errors import InvalidTokenError, DatabaseError


class TokenRepository:
    """令牌仓储，管理JWT令牌的存储、验证和撤销"""

    def __init__(self, redis_pool: aioredis.Redis):
        """
        初始化令牌仓储
        
        Args:
            redis_pool: Redis连接池
        """
        self.redis = redis_pool
        self.logger = logging.getLogger(__name__)
        
        # 令牌相关键前缀
        self.ACCESS_TOKEN_PREFIX = "auth:access_token:"
        self.REFRESH_TOKEN_PREFIX = "auth:refresh_token:"
        self.MFA_TOKEN_PREFIX = "auth:mfa_token:"
        self.BLACKLIST_PREFIX = "auth:blacklist:"
        
    async def store_token_data(self, token: str, token_type: str, data: Dict[str, Any], 
                               expires_in: int) -> bool:
        """
        存储令牌数据
        
        Args:
            token: 令牌字符串
            token_type: 令牌类型 ('access', 'refresh', 'mfa')
            data: 令牌相关数据
            expires_in: 过期时间(秒)
            
        Returns:
            bool: 操作是否成功
            
        Raises:
            DatabaseError: Redis操作失败
        """
        try:
            # 选择正确的键前缀
            if token_type == 'access':
                prefix = self.ACCESS_TOKEN_PREFIX
            elif token_type == 'refresh':
                prefix = self.REFRESH_TOKEN_PREFIX
            elif token_type == 'mfa':
                prefix = self.MFA_TOKEN_PREFIX
            else:
                raise ValueError(f"未知的令牌类型: {token_type}")
            
            # 存储令牌数据
            key = f"{prefix}{token}"
            await self.redis.setex(key, expires_in, json.dumps(data))
            
            # 如果是访问令牌，还要在用户的令牌集合中存储
            if token_type == 'access' and 'user_id' in data:
                user_tokens_key = f"auth:user_tokens:{data['user_id']}"
                await self.redis.sadd(user_tokens_key, token)
                
            return True
            
        except Exception as e:
            self.logger.exception(f"存储令牌数据时发生错误: {token_type}")
            raise DatabaseError(f"存储令牌失败: {str(e)}")
    
    async def get_token_data(self, token: str, token_type: str) -> Dict[str, Any]:
        """
        获取令牌数据
        
        Args:
            token: 令牌字符串
            token_type: 令牌类型 ('access', 'refresh', 'mfa')
            
        Returns:
            Dict: 令牌数据
            
        Raises:
            InvalidTokenError: 令牌无效或已过期
            DatabaseError: Redis操作失败
        """
        try:
            # 选择正确的键前缀
            if token_type == 'access':
                prefix = self.ACCESS_TOKEN_PREFIX
            elif token_type == 'refresh':
                prefix = self.REFRESH_TOKEN_PREFIX
            elif token_type == 'mfa':
                prefix = self.MFA_TOKEN_PREFIX
            else:
                raise ValueError(f"未知的令牌类型: {token_type}")
            
            # 检查令牌是否在黑名单中
            is_blacklisted = await self.redis.exists(f"{self.BLACKLIST_PREFIX}{token}")
            if is_blacklisted:
                raise InvalidTokenError("令牌已被撤销")
            
            # 获取令牌数据
            key = f"{prefix}{token}"
            data = await self.redis.get(key)
            
            if not data:
                raise InvalidTokenError("令牌无效或已过期")
            
            return json.loads(data)
            
        except InvalidTokenError:
            # 重新抛出无效令牌错误
            raise
        except Exception as e:
            self.logger.exception(f"获取令牌数据时发生错误: {token_type}")
            raise DatabaseError(f"获取令牌失败: {str(e)}")
    
    async def revoke_token(self, token: str, token_type: str, user_id: Optional[str] = None) -> bool:
        """
        撤销令牌
        
        Args:
            token: 令牌字符串
            token_type: 令牌类型 ('access', 'refresh', 'mfa')
            user_id: 用户ID (可选，用于清理用户令牌集合)
            
        Returns:
            bool: 操作是否成功
            
        Raises:
            DatabaseError: Redis操作失败
        """
        try:
            # 选择正确的键前缀
            if token_type == 'access':
                prefix = self.ACCESS_TOKEN_PREFIX
            elif token_type == 'refresh':
                prefix = self.REFRESH_TOKEN_PREFIX
            elif token_type == 'mfa':
                prefix = self.MFA_TOKEN_PREFIX
            else:
                raise ValueError(f"未知的令牌类型: {token_type}")
            
            # 获取令牌的剩余有效期
            key = f"{prefix}{token}"
            ttl = await self.redis.ttl(key)
            
            if ttl <= 0:
                # 令牌已经过期，无需操作
                return True
            
            # 从数据库中删除令牌
            await self.redis.delete(key)
            
            # 将令牌加入黑名单，黑名单项的有效期与原令牌相同
            blacklist_key = f"{self.BLACKLIST_PREFIX}{token}"
            await self.redis.setex(blacklist_key, ttl, "1")
            
            # 如果提供了用户ID，从用户的令牌集合中移除该令牌
            if user_id and token_type == 'access':
                user_tokens_key = f"auth:user_tokens:{user_id}"
                await self.redis.srem(user_tokens_key, token)
            
            return True
            
        except Exception as e:
            self.logger.exception(f"撤销令牌时发生错误: {token_type}")
            raise DatabaseError(f"撤销令牌失败: {str(e)}")
    
    async def revoke_all_user_tokens(self, user_id: str) -> bool:
        """
        撤销用户的所有令牌
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 操作是否成功
            
        Raises:
            DatabaseError: Redis操作失败
        """
        try:
            # 获取用户的所有访问令牌
            user_tokens_key = f"auth:user_tokens:{user_id}"
            tokens = await self.redis.smembers(user_tokens_key)
            
            # 撤销每个令牌
            for token in tokens:
                token_str = token.decode('utf-8') if isinstance(token, bytes) else token
                await self.revoke_token(token_str, 'access', user_id)
            
            # 清空用户令牌集合
            await self.redis.delete(user_tokens_key)
            
            return True
            
        except Exception as e:
            self.logger.exception(f"撤销用户所有令牌时发生错误: {user_id}")
            raise DatabaseError(f"撤销用户令牌失败: {str(e)}")
    
    async def store_verification_code(self, code_type: str, identifier: str, code: str, 
                                      expires_in: int) -> bool:
        """
        存储验证码
        
        Args:
            code_type: 验证码类型 ('email', 'sms', 'password_reset')
            identifier: 标识符(电子邮件/手机号)
            code: 验证码
            expires_in: 过期时间(秒)
            
        Returns:
            bool: 操作是否成功
            
        Raises:
            DatabaseError: Redis操作失败
        """
        try:
            key = f"auth:{code_type}_code:{identifier}"
            await self.redis.setex(key, expires_in, code)
            return True
            
        except Exception as e:
            self.logger.exception(f"存储验证码时发生错误: {code_type}, {identifier}")
            raise DatabaseError(f"存储验证码失败: {str(e)}")
    
    async def verify_code(self, code_type: str, identifier: str, code: str) -> bool:
        """
        验证验证码
        
        Args:
            code_type: 验证码类型 ('email', 'sms', 'password_reset')
            identifier: 标识符(电子邮件/手机号)
            code: 验证码
            
        Returns:
            bool: 验证码是否有效
            
        Raises:
            DatabaseError: Redis操作失败
        """
        try:
            key = f"auth:{code_type}_code:{identifier}"
            stored_code = await self.redis.get(key)
            
            if not stored_code:
                return False
            
            stored_code_str = stored_code.decode('utf-8') if isinstance(stored_code, bytes) else stored_code
            return stored_code_str == code
            
        except Exception as e:
            self.logger.exception(f"验证验证码时发生错误: {code_type}, {identifier}")
            raise DatabaseError(f"验证码验证失败: {str(e)}")
    
    async def delete_code(self, code_type: str, identifier: str) -> bool:
        """
        删除验证码
        
        Args:
            code_type: 验证码类型 ('email', 'sms', 'password_reset')
            identifier: 标识符(电子邮件/手机号)
            
        Returns:
            bool: 操作是否成功
            
        Raises:
            DatabaseError: Redis操作失败
        """
        try:
            key = f"auth:{code_type}_code:{identifier}"
            await self.redis.delete(key)
            return True
            
        except Exception as e:
            self.logger.exception(f"删除验证码时发生错误: {code_type}, {identifier}")
            raise DatabaseError(f"删除验证码失败: {str(e)}")
    
    async def rate_limit_check(self, action: str, identifier: str, 
                               max_attempts: int, window_seconds: int) -> Tuple[bool, Optional[int]]:
        """
        速率限制检查
        
        Args:
            action: 操作类型 ('login', 'register', 'password_reset')
            identifier: 标识符(IP地址/用户ID)
            max_attempts: 最大尝试次数
            window_seconds: 时间窗口(秒)
            
        Returns:
            Tuple[bool, Optional[int]]: (是否允许操作, 剩余等待时间(秒))
            
        Raises:
            DatabaseError: Redis操作失败
        """
        try:
            # 构造键
            key = f"auth:rate_limit:{action}:{identifier}"
            
            # 获取当前尝试次数
            count = await self.redis.get(key)
            count = int(count) if count else 0
            
            if count >= max_attempts:
                # 超过限制，获取剩余时间
                ttl = await self.redis.ttl(key)
                return False, ttl if ttl > 0 else window_seconds
            
            # 增加尝试次数
            if count == 0:
                # 第一次尝试，设置初始值和过期时间
                await self.redis.setex(key, window_seconds, "1")
            else:
                # 非第一次尝试，增加计数
                await self.redis.incr(key)
            
            return True, None
            
        except Exception as e:
            self.logger.exception(f"速率限制检查时发生错误: {action}, {identifier}")
            raise DatabaseError(f"速率限制检查失败: {str(e)}") 