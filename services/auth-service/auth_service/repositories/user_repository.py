"""用户数据仓库"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth_service.models.user import User, UserProfile, UserStatus
from auth_service.config.settings import get_settings


class UserRepository:
    """用户数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()
    
    async def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        phone: Optional[str] = None,
        is_verified: bool = False
    ) -> User:
        """创建用户"""
        user = User(
            username=username,
            email=email,
            phone=phone,
            password_hash=password_hash,
            is_verified=is_verified,
            status=UserStatus.ACTIVE
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """根据ID获取用户"""
        stmt = select(User).where(User.id == user_id).options(
            selectinload(User.profile)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        stmt = select(User).where(User.username == username).options(
            selectinload(User.profile)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        stmt = select(User).where(User.email == email).options(
            selectinload(User.profile)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        """根据用户名或邮箱获取用户"""
        stmt = select(User).where(
            or_(User.username == identifier, User.email == identifier)
        ).options(selectinload(User.profile))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_user(
        self,
        user_id: uuid.UUID,
        **kwargs
    ) -> Optional[User]:
        """更新用户信息"""
        stmt = update(User).where(User.id == user_id).values(**kwargs)
        await self.db.execute(stmt)
        await self.db.commit()
        
        return await self.get_by_id(user_id)
    
    async def update_password(
        self,
        user_id: uuid.UUID,
        password_hash: str
    ) -> bool:
        """更新用户密码"""
        stmt = update(User).where(User.id == user_id).values(
            password_hash=password_hash,
            password_changed_at=datetime.utcnow()
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def increment_failed_attempts(self, user_id: uuid.UUID) -> None:
        """增加失败登录尝试次数"""
        user = await self.get_by_id(user_id)
        if not user:
            return
        
        failed_attempts = user.failed_login_attempts + 1
        update_data = {"failed_login_attempts": failed_attempts}
        
        # 检查是否需要锁定账户
        if failed_attempts >= self.settings.security.max_login_attempts:
            lockout_duration = timedelta(
                minutes=self.settings.security.lockout_duration_minutes
            )
            update_data["locked_until"] = datetime.utcnow() + lockout_duration
        
        await self.update_user(user_id, **update_data)
    
    async def reset_failed_attempts(self, user_id: uuid.UUID) -> None:
        """重置失败登录尝试次数"""
        await self.update_user(
            user_id,
            failed_login_attempts=0,
            locked_until=None
        )
    
    async def update_last_login(
        self,
        user_id: uuid.UUID,
        ip_address: Optional[str] = None
    ) -> None:
        """更新最后登录信息"""
        update_data = {
            "last_login_at": datetime.utcnow(),
            "login_count": User.login_count + 1
        }
        
        if ip_address:
            update_data["last_login_ip"] = ip_address
        
        await self.update_user(user_id, **update_data)
    
    async def enable_mfa(self, user_id: uuid.UUID, secret: str) -> bool:
        """启用MFA"""
        stmt = update(User).where(User.id == user_id).values(
            mfa_enabled=True,
            mfa_secret=secret
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def disable_mfa(self, user_id: uuid.UUID) -> bool:
        """禁用MFA"""
        stmt = update(User).where(User.id == user_id).values(
            mfa_enabled=False,
            mfa_secret=None
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def verify_user(self, user_id: uuid.UUID) -> bool:
        """验证用户"""
        stmt = update(User).where(User.id == user_id).values(
            is_verified=True
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def list_users(
        self,
        offset: int = 0,
        limit: int = 10,
        status: Optional[UserStatus] = None
    ) -> List[User]:
        """获取用户列表"""
        stmt = select(User).options(selectinload(User.profile))
        
        if status:
            stmt = stmt.where(User.status == status)
        
        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def count_users(self, status: Optional[UserStatus] = None) -> int:
        """统计用户数量"""
        from sqlalchemy import func
        
        stmt = select(func.count(User.id))
        
        if status:
            stmt = stmt.where(User.status == status)
        
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def delete_user(self, user_id: uuid.UUID) -> bool:
        """删除用户（软删除）"""
        stmt = update(User).where(User.id == user_id).values(
            status=UserStatus.DELETED
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0 