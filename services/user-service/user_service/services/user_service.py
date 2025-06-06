"""
user_service - 索克生活项目模块
"""

from datetime import datetime, timedelta
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from user_service.core.exceptions import UserNotFoundError, UserAlreadyExistsError, DeviceNotFoundError
from user_service.models.device import UserDevice
from user_service.models.health import HealthSummary
from user_service.models.user import User, UserStatus, UserRole

"""用户服务核心业务逻辑"""




class UserService:
    """用户服务核心业务逻辑类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(
        self,
        username: str,
        email: str,
        phone: Optional[str] = None,
        full_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> User:
        """创建新用户"""
        
        # 检查用户名和邮箱是否已存在
        existing_user = await self.get_user_by_username_or_email(username, email)
        if existing_user:
            raise UserAlreadyExistsError("用户名或邮箱已存在")
        
        # 创建用户对象
        user = User(
            username=username,
            email=email,
            phone=phone,
            full_name=full_name,
            status=UserStatus.ACTIVE,
            roles=[UserRole.USER],
            metadata=metadata or {},
            preferences={
                "language": "zh-CN",
                "timezone": "Asia/Shanghai",
                "notifications": {
                    "email": True,
                    "push": True,
                    "sms": False
                },
                "privacy": {
                    "profile_visibility": "private",
                    "data_sharing": False
                }
            }
        )
        
        # 保存到数据库
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        result = await self.db.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username_or_email(self, username: str, email: str) -> Optional[User]:
        """根据用户名或邮箱获取用户"""
        result = await self.db.execute(
            select(User).where(
                (User.username == username) | (User.email == email)
            )
        )
        return result.scalar_one_or_none()
    
    async def update_user(self, user_id: str, **kwargs) -> User:
        """更新用户信息"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError("用户不存在")
        
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> User:
        """更新用户偏好设置"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError("用户不存在")
        
        # 合并偏好设置
        if user.preferences:
            user.preferences.update(preferences)
        else:
            user.preferences = preferences
        
        user.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def delete_user(self, user_id: str) -> bool:
        """删除用户（软删除）"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        # 软删除：更新状态为已删除
        user.status = UserStatus.DELETED
        user.updated_at = datetime.utcnow()
        
        await self.db.commit()
        return True
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[UserStatus] = None
    ) -> List[User]:
        """获取用户列表"""
        query = select(User)
        
        if status_filter:
            query = query.where(User.status == status_filter)
        
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()[:1000]  # 限制查询结果数量
    
    # 设备管理方法
    async def bind_device(
        self,
        user_id: str,
        device_id: str,
        device_type: str,
        device_name: Optional[str] = None,
        device_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """绑定设备到用户"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError("用户不存在")
        
        # 检查设备是否已绑定
        existing_device = await self.db.execute(
            select(UserDevice).where(
                (UserDevice.user_id == user_id) & 
                (UserDevice.device_id == device_id)
            )
        )
        if existing_device.scalar_one_or_none():
            raise ValueError("设备已绑定到此用户")
        
        # 创建设备绑定
        device_binding = UserDevice(
            user_id=user_id,
            device_id=device_id,
            device_type=device_type,
            device_name=device_name,
            device_metadata=device_metadata or {},
            binding_time=datetime.utcnow(),
            is_active=True,
            last_active_time=datetime.utcnow()
        )
        
        self.db.add(device_binding)
        await self.db.commit()
        await self.db.refresh(device_binding)
        
        return device_binding.binding_id
    
    async def get_user_devices(self, user_id: str) -> List[UserDevice]:
        """获取用户的设备列表"""
        result = await self.db.execute(
            select(UserDevice).where(
                (UserDevice.user_id == user_id) & 
                (UserDevice.is_active == True)
            ).order_by(UserDevice.binding_time.desc())
        )
        return result.scalars().all()[:1000]  # 限制查询结果数量
    
    async def unbind_device(self, user_id: str, device_id: str) -> bool:
        """解绑设备"""
        result = await self.db.execute(
            select(UserDevice).where(
                (UserDevice.user_id == user_id) & 
                (UserDevice.device_id == device_id) &
                (UserDevice.is_active == True)
            )
        )
        device = result.scalar_one_or_none()
        
        if not device:
            return False
        
        # 软删除：设置为非活跃状态
        device.is_active = False
        device.updated_at = datetime.utcnow()
        
        await self.db.commit()
        return True
    
    async def update_device_activity(self, user_id: str, device_id: str) -> bool:
        """更新设备活跃时间"""
        result = await self.db.execute(
            select(UserDevice).where(
                (UserDevice.user_id == user_id) & 
                (UserDevice.device_id == device_id) &
                (UserDevice.is_active == True)
            )
        )
        device = result.scalar_one_or_none()
        
        if not device:
            return False
        
        device.last_active_time = datetime.utcnow()
        await self.db.commit()
        return True
    
    # 健康数据相关方法
    async def get_user_health_summary(self, user_id: str) -> HealthSummary:
        """获取用户健康摘要"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError("用户不存在")
        
        # 查询健康摘要
        result = await self.db.execute(
            select(HealthSummary).where(HealthSummary.user_id == user_id)
        )
        health_summary = result.scalar_one_or_none()
        
        if not health_summary:
            # 如果不存在，创建默认健康摘要
            health_summary = HealthSummary(
                user_id=user_id,
                health_score=75.0,  # 默认健康分数
                last_updated=datetime.utcnow()
            )
            self.db.add(health_summary)
            await self.db.commit()
            await self.db.refresh(health_summary)
        
        return health_summary
    
    async def update_user_health_summary(
        self, 
        user_id: str, 
        health_score: float,
        metrics: Optional[Dict[str, Any]] = None
    ) -> HealthSummary:
        """更新用户健康摘要"""
        health_summary = await self.get_user_health_summary(user_id)
        
        health_summary.health_score = health_score
        if metrics:
            health_summary.metrics = metrics
        health_summary.last_updated = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(health_summary)
        
        return health_summary
    
    # 用户统计方法
    async def get_user_statistics(self) -> Dict[str, Any]:
        """获取用户统计信息"""
        # 总用户数
        total_users_result = await self.db.execute(
            select(User).where(User.status != UserStatus.DELETED)
        )
        total_users = len(total_users_result.scalars().all()[:1000]  # 限制查询结果数量)
        
        # 活跃用户数
        active_users_result = await self.db.execute(
            select(User).where(User.status == UserStatus.ACTIVE)
        )
        active_users = len(active_users_result.scalars().all()[:1000]  # 限制查询结果数量)
        
        # 今日新增用户
        today = datetime.utcnow().date()
        new_users_today_result = await self.db.execute(
            select(User).where(
                (User.created_at >= today) & 
                (User.status != UserStatus.DELETED)
            )
        )
        new_users_today = len(new_users_today_result.scalars().all()[:1000]  # 限制查询结果数量)
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "new_users_today": new_users_today,
            "user_growth_rate": 0.05,  # 模拟增长率
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def get_user_activity_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """获取用户活动摘要"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError("用户不存在")
        
        # 模拟活动数据
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        return {
            "user_id": user_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "activity_summary": {
                "login_count": 25,
                "active_days": 20,
                "avg_session_duration": 45.5,  # 分钟
                "last_login": (end_date - timedelta(hours=2)).isoformat(),
                "device_usage": {
                    "mobile": 18,
                    "web": 7
                }
            },
            "health_data_points": 150,
            "goals_completed": 3,
            "insights_generated": 8
        } 