"""
User Integration Repository
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_

from ..model.user_integration import (
    UserIntegrationDB, 
    PlatformType,
    IntegrationStatus
)
from ..service.logging_config import LoggerMixin


class UserIntegrationRepository(LoggerMixin):
    """用户集成数据访问层"""
    
    async def create(self, session: AsyncSession, integration_data: dict) -> UserIntegrationDB:
        """创建用户集成"""
        try:
            integration = UserIntegrationDB(**integration_data)
            session.add(integration)
            await session.flush()
            await session.refresh(integration)
            
            self.logger.info("创建用户集成成功", 
                           user_id=integration.user_id,
                           platform=integration.platform)
            return integration
            
        except Exception as e:
            self.logger.error("创建用户集成失败", error=str(e))
            raise
    
    async def get_by_id(self, session: AsyncSession, integration_id: int, user_id: str) -> Optional[UserIntegrationDB]:
        """根据ID获取集成"""
        try:
            stmt = select(UserIntegrationDB).where(
                and_(
                    UserIntegrationDB.id == integration_id,
                    UserIntegrationDB.user_id == user_id
                )
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
            
        except Exception as e:
            self.logger.error("获取集成失败", 
                            integration_id=integration_id,
                            user_id=user_id,
                            error=str(e))
            raise
    
    async def list_by_user(
        self,
        session: AsyncSession,
        user_id: str,
        platform: Optional[PlatformType] = None,
        status: Optional[IntegrationStatus] = None,
        offset: int = 0,
        limit: int = 20
    ) -> List[UserIntegrationDB]:
        """获取用户的集成列表"""
        try:
            stmt = select(UserIntegrationDB).where(
                UserIntegrationDB.user_id == user_id
            )
            
            # 添加过滤条件
            if platform:
                stmt = stmt.where(UserIntegrationDB.platform == platform.value)
            
            if status:
                stmt = stmt.where(UserIntegrationDB.status == status.value)
            
            # 添加分页
            stmt = stmt.offset(offset).limit(limit)
            
            # 按创建时间倒序
            stmt = stmt.order_by(UserIntegrationDB.created_at.desc())
            
            result = await session.execute(stmt)
            return result.scalars().all()
            
        except Exception as e:
            self.logger.error("获取用户集成列表失败",
                            user_id=user_id,
                            error=str(e))
            raise
    
    async def update(
        self,
        session: AsyncSession,
        integration_id: int,
        user_id: str,
        update_data: dict
    ) -> Optional[UserIntegrationDB]:
        """更新集成"""
        try:
            # 添加更新时间
            update_data['updated_at'] = datetime.now()
            
            stmt = update(UserIntegrationDB).where(
                and_(
                    UserIntegrationDB.id == integration_id,
                    UserIntegrationDB.user_id == user_id
                )
            ).values(**update_data)
            
            result = await session.execute(stmt)
            
            if result.rowcount > 0:
                # 重新获取更新后的数据
                return await self.get_by_id(session, integration_id, user_id)
            
            return None
            
        except Exception as e:
            self.logger.error("更新用户集成失败",
                            integration_id=integration_id,
                            user_id=user_id,
                            error=str(e))
            raise
    
    async def delete(self, session: AsyncSession, integration_id: int, user_id: str) -> bool:
        """删除集成"""
        try:
            stmt = delete(UserIntegrationDB).where(
                and_(
                    UserIntegrationDB.id == integration_id,
                    UserIntegrationDB.user_id == user_id
                )
            )
            
            result = await session.execute(stmt)
            success = result.rowcount > 0
            
            if success:
                self.logger.info("删除用户集成成功",
                               integration_id=integration_id,
                               user_id=user_id)
            
            return success
            
        except Exception as e:
            self.logger.error("删除用户集成失败",
                            integration_id=integration_id,
                            user_id=user_id,
                            error=str(e))
            raise 