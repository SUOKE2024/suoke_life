#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OAuth仓储实现
处理OAuth连接的存储和管理
"""
import logging
from datetime import datetime, UTC
from typing import Dict, List, Optional, Any, Tuple

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from internal.model.user import OAuthConnection
from internal.model.errors import DatabaseError, UserNotFoundError, ValidationError

logger = logging.getLogger(__name__)

class OAuthRepository:
    """OAuth仓储，管理OAuth连接数据"""

    def __init__(self, session: AsyncSession):
        """
        初始化OAuth仓储
        
        Args:
            session: 数据库会话
        """
        self.session = session
        self.logger = logging.getLogger(__name__)
    
    async def create_connection(self, 
                              user_id: str,
                              provider: str,
                              provider_user_id: str,
                              access_token: str,
                              refresh_token: Optional[str] = None,
                              expires_at: Optional[datetime] = None,
                              user_data: Optional[Dict] = None) -> OAuthConnection:
        """
        创建OAuth连接
        
        Args:
            user_id: 用户ID
            provider: 提供商 (e.g., 'github', 'wechat')
            provider_user_id: 提供商用户ID
            access_token: 访问令牌
            refresh_token: 刷新令牌 (可选)
            expires_at: 过期时间 (可选)
            user_data: 用户数据 (可选)
            
        Returns:
            OAuthConnection: 创建的连接
            
        Raises:
            DatabaseError: 数据库错误
            ValidationError: 连接已存在
        """
        try:
            # 检查连接是否已存在
            existing = await self.get_connection_by_provider_id(provider, provider_user_id)
            if existing:
                raise ValidationError(f"此{provider}账号已关联到其他用户")
            
            # 创建新连接
            stmt = sa.insert(OAuthConnection).values(
                user_id=user_id,
                provider=provider,
                provider_user_id=provider_user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                user_data=user_data or {},
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            ).returning(OAuthConnection)
            
            result = await self.session.execute(stmt)
            connection = result.scalar_one()
            await self.session.commit()
            
            return connection
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"创建OAuth连接失败: {str(e)}")
            if isinstance(e, ValidationError):
                raise
            raise DatabaseError(f"创建OAuth连接失败: {str(e)}")
    
    async def update_connection(self, 
                              connection_id: str,
                              access_token: Optional[str] = None,
                              refresh_token: Optional[str] = None,
                              expires_at: Optional[datetime] = None,
                              user_data: Optional[Dict] = None) -> bool:
        """
        更新OAuth连接
        
        Args:
            connection_id: 连接ID
            access_token: 新的访问令牌 (可选)
            refresh_token: 新的刷新令牌 (可选)
            expires_at: 新的过期时间 (可选)
            user_data: 新的用户数据 (可选)
            
        Returns:
            bool: 更新是否成功
            
        Raises:
            DatabaseError: 数据库错误
        """
        try:
            # 准备更新数据
            update_data = {}
            if access_token is not None:
                update_data["access_token"] = access_token
            if refresh_token is not None:
                update_data["refresh_token"] = refresh_token
            if expires_at is not None:
                update_data["expires_at"] = expires_at
            if user_data is not None:
                update_data["user_data"] = user_data
            
            if not update_data:
                return True  # 没有数据需要更新
            
            # 添加更新时间
            update_data["updated_at"] = datetime.now(UTC)
            
            # 执行更新
            stmt = sa.update(OAuthConnection).where(
                OAuthConnection.id == connection_id
            ).values(**update_data)
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            return result.rowcount > 0
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"更新OAuth连接失败: {str(e)}")
            raise DatabaseError(f"更新OAuth连接失败: {str(e)}")
    
    async def get_connection_by_id(self, connection_id: str) -> Optional[OAuthConnection]:
        """
        通过ID获取OAuth连接
        
        Args:
            connection_id: 连接ID
            
        Returns:
            Optional[OAuthConnection]: 连接对象，如果不存在则为None
            
        Raises:
            DatabaseError: 数据库错误
        """
        try:
            stmt = select(OAuthConnection).where(OAuthConnection.id == connection_id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"获取OAuth连接失败: {str(e)}")
            raise DatabaseError(f"获取OAuth连接失败: {str(e)}")
    
    async def get_connection_by_provider_id(self, provider: str, provider_user_id: str) -> Optional[OAuthConnection]:
        """
        通过提供商和提供商用户ID获取OAuth连接
        
        Args:
            provider: 提供商
            provider_user_id: 提供商用户ID
            
        Returns:
            Optional[OAuthConnection]: 连接对象，如果不存在则为None
            
        Raises:
            DatabaseError: 数据库错误
        """
        try:
            stmt = select(OAuthConnection).where(
                OAuthConnection.provider == provider,
                OAuthConnection.provider_user_id == provider_user_id
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"获取OAuth连接失败: {str(e)}")
            raise DatabaseError(f"获取OAuth连接失败: {str(e)}")

    async def get_connection_by_provider_and_user_id(self, provider: str, user_id: str) -> Optional[OAuthConnection]:
        """
        通过提供商和用户ID获取OAuth连接
        
        Args:
            provider: 提供商
            user_id: 用户ID
            
        Returns:
            Optional[OAuthConnection]: 连接对象，如果不存在则为None
            
        Raises:
            DatabaseError: 数据库错误
        """
        try:
            stmt = select(OAuthConnection).where(
                OAuthConnection.provider == provider,
                OAuthConnection.user_id == user_id
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"获取OAuth连接失败: {str(e)}")
            raise DatabaseError(f"获取OAuth连接失败: {str(e)}")
    
    async def get_user_connections(self, user_id: str) -> List[OAuthConnection]:
        """
        获取用户的所有OAuth连接
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户的所有OAuth连接
            
        Raises:
            DatabaseError: 数据库操作错误
        """
        try:
            stmt = sa.select(OAuthConnection).where(OAuthConnection.user_id == user_id)
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            self.logger.error(f"获取用户OAuth连接失败: {str(e)}")
            raise DatabaseError(f"获取用户OAuth连接失败: {str(e)}")
    
    async def count_user_connections(self, user_id: str) -> int:
        """
        计算用户拥有的OAuth连接数量
        
        Args:
            user_id: 用户ID
            
        Returns:
            int: 连接数量
            
        Raises:
            DatabaseError: 数据库错误
        """
        try:
            stmt = sa.select(sa.func.count()).select_from(OAuthConnection).where(
                OAuthConnection.user_id == user_id
            )
            result = await self.session.execute(stmt)
            return result.scalar() or 0
        except Exception as e:
            self.logger.error(f"计算用户OAuth连接数量失败: {str(e)}")
            raise DatabaseError(f"计算用户OAuth连接数量失败: {str(e)}")
    
    async def delete_connection(self, connection_id: str) -> bool:
        """
        删除OAuth连接
        
        Args:
            connection_id: 连接ID
            
        Returns:
            bool: 删除是否成功
            
        Raises:
            DatabaseError: 数据库错误
        """
        try:
            stmt = sa.delete(OAuthConnection).where(OAuthConnection.id == connection_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            return result.rowcount > 0
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"删除OAuth连接失败: {str(e)}")
            raise DatabaseError(f"删除OAuth连接失败: {str(e)}")
    
    async def delete_user_connections(self, user_id: str) -> int:
        """
        删除用户的所有OAuth连接
        
        Args:
            user_id: 用户ID
            
        Returns:
            int: 删除的连接数量
            
        Raises:
            DatabaseError: 数据库错误
        """
        try:
            stmt = sa.delete(OAuthConnection).where(OAuthConnection.user_id == user_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            return result.rowcount
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"删除用户OAuth连接失败: {str(e)}")
            raise DatabaseError(f"删除用户OAuth连接失败: {str(e)}")