"""
session_repository - 索克生活项目模块
"""

from auth_service.models.user import UserSession
from datetime import datetime, timedelta
from sqlalchemy import and_, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

"""会话数据仓库"""





class SessionRepository:
    """会话数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_session(
        self,
        user_id: uuid.UUID,
        session_token: str,
        refresh_token: str,
        expires_at: datetime,
        device_id: Optional[str] = None,
        device_name: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        location: Optional[str] = None
    ) -> UserSession:
        """创建用户会话"""
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            device_id=device_id,
            device_name=device_name,
            user_agent=user_agent,
            ip_address=ip_address,
            location=location,
            is_active=True
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def get_by_session_token(self, session_token: str) -> Optional[UserSession]:
        """根据会话令牌获取会话"""
        stmt = select(UserSession).where(
            and_(
                UserSession.session_token == session_token,
                UserSession.is_active == True
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_refresh_token(self, refresh_token: str) -> Optional[UserSession]:
        """根据刷新令牌获取会话"""
        stmt = select(UserSession).where(
            and_(
                UserSession.refresh_token == refresh_token,
                UserSession.is_active == True
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_sessions(
        self,
        user_id: uuid.UUID,
        active_only: bool = True
    ) -> List[UserSession]:
        """获取用户的所有会话"""
        stmt = select(UserSession).where(UserSession.user_id == user_id)
        
        if active_only:
            stmt = stmt.where(UserSession.is_active == True)
        
        stmt = stmt.order_by(UserSession.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all()[:1000]  # 限制查询结果数量)
    
    async def update_session_activity(
        self,
        session_id: uuid.UUID,
        ip_address: Optional[str] = None,
        location: Optional[str] = None
    ) -> bool:
        """更新会话活动信息"""
        update_data = {"last_activity_at": datetime.utcnow()}
        
        if ip_address:
            update_data["ip_address"] = ip_address
        if location:
            update_data["location"] = location
        
        stmt = update(UserSession).where(UserSession.id == session_id).values(**update_data)
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def refresh_session(
        self,
        session_id: uuid.UUID,
        new_session_token: str,
        new_refresh_token: str,
        new_expires_at: datetime
    ) -> bool:
        """刷新会话令牌"""
        stmt = update(UserSession).where(UserSession.id == session_id).values(
            session_token=new_session_token,
            refresh_token=new_refresh_token,
            expires_at=new_expires_at,
            last_activity_at=datetime.utcnow()
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def deactivate_session(self, session_id: uuid.UUID) -> bool:
        """停用会话"""
        stmt = update(UserSession).where(UserSession.id == session_id).values(
            is_active=False
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def deactivate_user_sessions(
        self,
        user_id: uuid.UUID,
        exclude_session_id: Optional[uuid.UUID] = None
    ) -> int:
        """停用用户的所有会话（可排除指定会话）"""
        stmt = update(UserSession).where(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
        )
        
        if exclude_session_id:
            stmt = stmt.where(UserSession.id != exclude_session_id)
        
        stmt = stmt.values(is_active=False)
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount
    
    async def cleanup_expired_sessions(self) -> int:
        """清理过期会话"""
        now = datetime.utcnow()
        stmt = update(UserSession).where(
            and_(
                UserSession.expires_at < now,
                UserSession.is_active == True
            )
        ).values(is_active=False)
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount
    
    async def delete_old_sessions(self, days: int = 30) -> int:
        """删除旧的非活跃会话"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        stmt = delete(UserSession).where(
            and_(
                UserSession.is_active == False,
                UserSession.created_at < cutoff_date
            )
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount 