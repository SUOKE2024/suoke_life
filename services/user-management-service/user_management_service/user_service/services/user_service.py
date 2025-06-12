"""
用户服务业务逻辑实现
提供用户管理的核心功能
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from user_service.core.exceptions import (
    DeviceNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from user_service.models.device import UserDevice
from user_service.models.health import HealthSummary
from user_service.models.user import User, UserStatus

logger = logging.getLogger(__name__)


class UserService:
    """用户服务类"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create_user(
        self,
        username: str,
        email: str,
        phone: Optional[str] = None,
       **kwargs
    ) -> User:
        """创建新用户"""
        try:
            # 检查用户是否已存在
            existing_user = await self.get_user_by_email(email)
            if existing_user:
                raise UserAlreadyExistsError(f"用户邮箱 {email} 已存在")
            
            # 创建用户
            user = User(
                id=uuid.uuid4(),
                username=username,
                email=email,
                phone=phone,
                status=UserStatus.ACTIVE,
                created_at=datetime.utcnow(),
               **kwargs
            )
            
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"创建用户成功: {user.id}")
            return user
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建用户失败: {e}")
            raise
    
    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """根据ID获取用户"""
        try:
            stmt = select(User).where(User.id==user_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        try:
            stmt = select(User).where(User.email==email)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"根据邮箱获取用户失败: {e}")
            raise
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        try:
            stmt = select(User).where(User.username==username)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"根据用户名获取用户失败: {e}")
            raise
    
    async def update_user(
        self,
        user_id: uuid.UUID,
       **kwargs
    ) -> User:
        """更新用户信息"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundError(f"用户 {user_id} 不存在")
            
            # 更新字段
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"更新用户成功: {user_id}")
            return user
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"更新用户失败: {e}")
            raise
    
    async def delete_user(self, user_id: uuid.UUID) -> bool:
        """删除用户（软删除）"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundError(f"用户 {user_id} 不存在")
            
            # 软删除
            user.status = UserStatus.DELETED
            user.deleted_at = datetime.utcnow()
            
            await self.db.commit()
            
            logger.info(f"删除用户成功: {user_id}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"删除用户失败: {e}")
            raise
    
    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[UserStatus] = None,
        search: Optional[str] = None
    ) -> Tuple[List[User], int]:
        """获取用户列表"""
        try:
            # 构建查询
            stmt = select(User)
            
            # 状态过滤
            if status:
                stmt = stmt.where(User.status==status)
            
            # 搜索过滤
            if search:
                stmt = stmt.where(
                    User.username.ilike(f"%{search}%") |
                    User.email.ilike(f"%{search}%")
                )
            
            # 计算总数
            count_stmt = select(func.count(User.id)).select_from(stmt.subquery())
            total_result = await self.db.execute(count_stmt)
            total = total_result.scalar()
            
            # 分页
            offset = (page - 1) * page_size
            stmt = stmt.offset(offset).limit(page_size)
            stmt = stmt.order_by(User.created_at.desc())
            
            result = await self.db.execute(stmt)
            users = result.scalars().all()
            
            return list(users), total
            
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            raise
    
    async def bind_device(
        self,
        user_id: uuid.UUID,
        device_id: str,
        device_name: str,
        device_type: str
    ) -> UserDevice:
        """绑定用户设备"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundError(f"用户 {user_id} 不存在")
            
            # 检查设备是否已绑定
            stmt = select(UserDevice).where(
                UserDevice.user_id==user_id,
                UserDevice.device_id==device_id
            )
            result = await self.db.execute(stmt)
            existing_device = result.scalar_one_or_none()
            
            if existing_device:
                # 更新设备信息
                existing_device.device_name = device_name
                existing_device.device_type = device_type
                existing_device.updated_at = datetime.utcnow()
                device = existing_device
            else:
                # 创建新设备绑定
                device = UserDevice(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    device_id=device_id,
                    device_name=device_name,
                    device_type=device_type,
                    created_at=datetime.utcnow()
                )
                self.db.add(device)
            
            await self.db.commit()
            await self.db.refresh(device)
            
            logger.info(f"绑定设备成功: 用户 {user_id}, 设备 {device_id}")
            return device
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"绑定设备失败: {e}")
            raise
    
    async def get_user_devices(self, user_id: uuid.UUID) -> List[UserDevice]:
        """获取用户设备列表"""
        try:
            stmt = select(UserDevice).where(UserDevice.user_id==user_id)
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"获取用户设备失败: {e}")
            raise
    
    async def unbind_device(self, user_id: uuid.UUID, device_id: str) -> bool:
        """解绑用户设备"""
        try:
            stmt = select(UserDevice).where(
                UserDevice.user_id==user_id,
                UserDevice.device_id==device_id
            )
            result = await self.db.execute(stmt)
            device = result.scalar_one_or_none()
            
            if not device:
                raise DeviceNotFoundError(f"设备 {device_id} 未绑定到用户 {user_id}")
            
            await self.db.delete(device)
            await self.db.commit()
            
            logger.info(f"解绑设备成功: 用户 {user_id}, 设备 {device_id}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"解绑设备失败: {e}")
            raise
    
    async def get_user_health_summary(self, user_id: uuid.UUID) -> Optional[HealthSummary]:
        """获取用户健康摘要"""
        try:
            stmt = select(HealthSummary).where(HealthSummary.user_id==user_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"获取用户健康摘要失败: {e}")
            raise
    
    async def update_user_health_summary(
        self,
        user_id: uuid.UUID,
        health_data: Dict[str, Any]
    ) -> HealthSummary:
        """更新用户健康摘要"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundError(f"用户 {user_id} 不存在")
            
            # 查找现有健康摘要
            stmt = select(HealthSummary).where(HealthSummary.user_id==user_id)
            result = await self.db.execute(stmt)
            health_summary = result.scalar_one_or_none()
            
            if health_summary:
                # 更新现有摘要
                for key, value in health_data.items():
                    if hasattr(health_summary, key):
                        setattr(health_summary, key, value)
                health_summary.updated_at = datetime.utcnow()
            else:
                # 创建新摘要
                health_summary = HealthSummary(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    created_at=datetime.utcnow(),
                   **health_data
                )
                self.db.add(health_summary)
            
            await self.db.commit()
            await self.db.refresh(health_summary)
            
            logger.info(f"更新用户健康摘要成功: {user_id}")
            return health_summary
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"更新用户健康摘要失败: {e}")
            raise


def main() -> None:
    """主函数 - 用于测试"""
    print("用户服务业务逻辑模块")


if __name__=="__main__":
    main()
