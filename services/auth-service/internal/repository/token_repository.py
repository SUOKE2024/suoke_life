#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
令牌仓储实现

处理刷新令牌和其他令牌数据的存储和检索。
"""
import json
import logging
import time
from typing import Dict, Optional, Any, Tuple, List
from datetime import datetime, UTC, timedelta
import secrets
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, delete

import redis

from internal.model.errors import InvalidTokenError, DatabaseError
from internal.model.refresh_token import RefreshToken
from .base import BaseRepository
from internal.db.models import RefreshTokenModel


class TokenRepository(BaseRepository[RefreshTokenModel]):
    """令牌仓储类"""
    
    def __init__(self, redis_client: redis.Redis, session):
        """
        初始化令牌仓储
        
        Args:
            redis_client: Redis客户端
            session: SQLAlchemy会话
        """
        super().__init__(RefreshTokenModel)
        self.redis = redis_client
        self.session = session
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
            self.redis.setex(key, expires_in, json.dumps(data))
            
            # 如果是访问令牌，还要在用户的令牌集合中存储
            if token_type == 'access' and 'user_id' in data:
                user_tokens_key = f"auth:user_tokens:{data['user_id']}"
                self.redis.sadd(user_tokens_key, token)
                
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
            is_blacklisted = self.redis.exists(f"{self.BLACKLIST_PREFIX}{token}")
            if is_blacklisted:
                raise InvalidTokenError("令牌已被撤销")
            
            # 获取令牌数据
            key = f"{prefix}{token}"
            data = self.redis.get(key)
            
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
            ttl = self.redis.ttl(key)
            
            if ttl <= 0:
                # 令牌已经过期，无需操作
                return True
            
            # 从数据库中删除令牌
            self.redis.delete(key)
            
            # 将令牌加入黑名单，黑名单项的有效期与原令牌相同
            blacklist_key = f"{self.BLACKLIST_PREFIX}{token}"
            self.redis.setex(blacklist_key, ttl, "1")
            
            # 如果提供了用户ID，从用户的令牌集合中移除该令牌
            if user_id and token_type == 'access':
                user_tokens_key = f"auth:user_tokens:{user_id}"
                self.redis.srem(user_tokens_key, token)
            
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
            tokens = self.redis.smembers(user_tokens_key)
            
            # 撤销每个令牌
            for token in tokens:
                token_str = token.decode('utf-8') if isinstance(token, bytes) else token
                await self.revoke_token(token_str, 'access', user_id)
            
            # 清空用户令牌集合
            self.redis.delete(user_tokens_key)
            
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
            self.redis.setex(key, expires_in, code)
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
            stored_code = self.redis.get(key)
            
            if not stored_code:
                return False
                
            stored_code_str = stored_code.decode('utf-8') if isinstance(stored_code, bytes) else stored_code
            return stored_code_str == code
            
        except Exception as e:
            self.logger.exception(f"验证码验证时发生错误: {code_type}, {identifier}")
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
            self.redis.delete(key)
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
            identifier: 标识符(用户ID/IP地址)
            max_attempts: 最大尝试次数
            window_seconds: 时间窗口(秒)
            
        Returns:
            Tuple[bool, Optional[int]]: (是否允许操作, 剩余冷却时间)
            
        Raises:
            DatabaseError: Redis操作失败
        """
        try:
            current_time = int(time.time())
            key = f"auth:rate_limit:{action}:{identifier}"
            
            # 获取当前计数和窗口开始时间
            data = self.redis.get(key)
            
            if data:
                data_dict = json.loads(data)
                attempts = data_dict.get("attempts", 0)
                window_start = data_dict.get("window_start", current_time)
                
                # 检查是否在窗口期内
                if current_time - window_start > window_seconds:
                    # 窗口已过期，重置计数
                    attempts = 1
                    window_start = current_time
                else:
                    # 窗口内，增加计数
                    attempts += 1
                
                # 检查是否超出限制
                if attempts > max_attempts:
                    # 计算剩余冷却时间
                    cooldown = window_seconds - (current_time - window_start)
                    return False, cooldown
                
                # 更新数据
                data_dict = {
                    "attempts": attempts,
                    "window_start": window_start
                }
                self.redis.setex(key, window_seconds, json.dumps(data_dict))
                return True, None
                
            else:
                # 首次尝试，设置初始值
                data_dict = {
                    "attempts": 1,
                    "window_start": current_time
                }
                self.redis.setex(key, window_seconds, json.dumps(data_dict))
                return True, None
                
        except Exception as e:
            self.logger.exception(f"速率限制检查时发生错误: {action}, {identifier}")
            raise DatabaseError(f"速率限制检查失败: {str(e)}")
    
    async def create_refresh_token(
        self, 
        user_id: str, 
        token: str, 
        expires_at: datetime,
        device_info: Optional[Dict[str, Any]] = None
    ) -> RefreshTokenModel:
        """创建刷新令牌"""
        refresh_token = RefreshTokenModel(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            device_info=device_info or {},
            created_at=datetime.utcnow()
        )
        return await self.create(refresh_token)
    
    async def get_by_token(self, token: str) -> Optional[RefreshTokenModel]:
        """根据令牌获取刷新令牌"""
        async with await self.get_session() as session:
            result = await session.execute(
                select(RefreshTokenModel).where(RefreshTokenModel.token == token)
            )
            return result.scalar_one_or_none()
    
    async def get_user_tokens(
        self, 
        user_id: str, 
        active_only: bool = True
    ) -> List[RefreshTokenModel]:
        """获取用户的刷新令牌"""
        async with await self.get_session() as session:
            query = select(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id)
            
            if active_only:
                now = datetime.utcnow()
                query = query.where(
                    and_(
                        RefreshTokenModel.expires_at > now,
                        RefreshTokenModel.revoked_at.is_(None)
                    )
                )
            
            result = await session.execute(query.order_by(RefreshTokenModel.created_at.desc()))
            return list(result.scalars().all())
    
    async def revoke_user_tokens(self, user_id: str, exclude_token: Optional[str] = None) -> int:
        """撤销用户的所有令牌"""
        async with await self.get_session() as session:
            query = select(RefreshTokenModel).where(
                and_(
                    RefreshTokenModel.user_id == user_id,
                    RefreshTokenModel.revoked_at.is_(None)
                )
            )
            
            if exclude_token:
                query = query.where(RefreshTokenModel.token != exclude_token)
            
            result = await session.execute(query)
            tokens = list(result.scalars().all())
            
            count = 0
            now = datetime.utcnow()
            for token in tokens:
                token.revoked_at = now
                count += 1
            
            if count > 0:
                await session.commit()
            
            return count
    
    async def is_token_valid(self, token: str) -> bool:
        """检查令牌是否有效"""
        async with await self.get_session() as session:
            result = await session.execute(
                select(RefreshTokenModel).where(
                    and_(
                        RefreshTokenModel.token == token,
                        RefreshTokenModel.expires_at > datetime.utcnow(),
                        RefreshTokenModel.revoked_at.is_(None)
                    )
                )
            )
            return result.scalar_one_or_none() is not None
    
    async def cleanup_expired_tokens(self) -> int:
        """清理过期的令牌"""
        async with await self.get_session() as session:
            now = datetime.utcnow()
            result = await session.execute(
                delete(RefreshTokenModel).where(
                    or_(
                        RefreshTokenModel.expires_at <= now,
                        RefreshTokenModel.revoked_at.is_not(None)
                    )
                )
            )
            await session.commit()
            return result.rowcount
    
    async def get_token_stats(self, user_id: Optional[str] = None) -> Dict[str, int]:
        """获取令牌统计信息"""
        async with await self.get_session() as session:
            now = datetime.utcnow()
            
            # 基础查询
            base_query = select(RefreshTokenModel)
            if user_id:
                base_query = base_query.where(RefreshTokenModel.user_id == user_id)
            
            # 总数
            total_result = await session.execute(
                select(func.count()).select_from(base_query.subquery())
            )
            total = total_result.scalar()
            
            # 活跃数
            active_result = await session.execute(
                select(func.count()).select_from(
                    base_query.where(
                        and_(
                            RefreshTokenModel.expires_at > now,
                            RefreshTokenModel.revoked_at.is_(None)
                        )
                    ).subquery()
                )
            )
            active = active_result.scalar()
            
            # 过期数
            expired_result = await session.execute(
                select(func.count()).select_from(
                    base_query.where(RefreshTokenModel.expires_at <= now).subquery()
                )
            )
            expired = expired_result.scalar()
            
            # 撤销数
            revoked_result = await session.execute(
                select(func.count()).select_from(
                    base_query.where(RefreshTokenModel.revoked_at.is_not(None)).subquery()
                )
            )
            revoked = revoked_result.scalar()
            
            return {
                "total": total,
                "active": active,
                "expired": expired,
                "revoked": revoked
            }
    
    async def update_last_used(self, token: str) -> bool:
        """更新令牌最后使用时间"""
        async with await self.get_session() as session:
            result = await session.execute(
                select(RefreshTokenModel).where(RefreshTokenModel.token == token)
            )
            refresh_token = result.scalar_one_or_none()
            
            if refresh_token:
                refresh_token.last_used_at = datetime.utcnow()
                await session.commit()
                return True
            
            return False 