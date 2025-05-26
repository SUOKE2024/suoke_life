"""
Platform Auth Repository
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_

from ..model.user_integration import PlatformAuthDB, PlatformType
from ..service.logging_config import LoggerMixin


class PlatformAuthRepository(LoggerMixin):
    """平台认证数据访问层"""
    
    async def create(self, session: AsyncSession, auth_data: dict) -> PlatformAuthDB:
        """创建平台认证"""
        try:
            auth = PlatformAuthDB(**auth_data)
            session.add(auth)
            await session.flush()
            await session.refresh(auth)
            
            self.logger.info("创建平台认证成功", 
                           user_id=auth.user_id,
                           platform=auth.platform)
            return auth
            
        except Exception as e:
            self.logger.error("创建平台认证失败", error=str(e))
            raise
    
    async def get_by_user_platform(
        self, 
        session: AsyncSession, 
        user_id: str, 
        platform: PlatformType
    ) -> Optional[PlatformAuthDB]:
        """根据用户和平台获取认证"""
        try:
            stmt = select(PlatformAuthDB).where(
                and_(
                    PlatformAuthDB.user_id == user_id,
                    PlatformAuthDB.platform == platform.value
                )
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
            
        except Exception as e:
            self.logger.error("获取平台认证失败",
                            user_id=user_id,
                            platform=platform.value,
                            error=str(e))
            raise
    
    async def update_tokens(
        self,
        session: AsyncSession,
        user_id: str,
        platform: PlatformType,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> bool:
        """更新访问令牌"""
        try:
            update_data = {
                "access_token": access_token,
                "updated_at": datetime.now()
            }
            
            if refresh_token:
                update_data["refresh_token"] = refresh_token
            
            if expires_at:
                update_data["expires_at"] = expires_at
            
            stmt = update(PlatformAuthDB).where(
                and_(
                    PlatformAuthDB.user_id == user_id,
                    PlatformAuthDB.platform == platform.value
                )
            ).values(**update_data)
            
            result = await session.execute(stmt)
            success = result.rowcount > 0
            
            if success:
                self.logger.info("更新平台令牌成功",
                               user_id=user_id,
                               platform=platform.value)
            
            return success
            
        except Exception as e:
            self.logger.error("更新平台令牌失败",
                            user_id=user_id,
                            platform=platform.value,
                            error=str(e))
            raise
    
    async def delete(
        self, 
        session: AsyncSession, 
        user_id: str, 
        platform: PlatformType
    ) -> bool:
        """删除平台认证"""
        try:
            stmt = delete(PlatformAuthDB).where(
                and_(
                    PlatformAuthDB.user_id == user_id,
                    PlatformAuthDB.platform == platform.value
                )
            )
            
            result = await session.execute(stmt)
            success = result.rowcount > 0
            
            if success:
                self.logger.info("删除平台认证成功",
                               user_id=user_id,
                               platform=platform.value)
            
            return success
            
        except Exception as e:
            self.logger.error("删除平台认证失败",
                            user_id=user_id,
                            platform=platform.value,
                            error=str(e))
            raise 