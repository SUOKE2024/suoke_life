"""
领域层仓库接口定义
提供数据访问的抽象接口
"""
from abc import ABC, abstractmethod
from datetime import datetime

from internal.domain.user import User, UserStatus, UserRole
from internal.model.user import (
    UserHealthSummary, DeviceInfo, HealthMetric, 
    ConstitutionType, HealthCondition
)

class UserRepository(ABC):
    """用户仓库接口"""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """创建用户"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """根据ID获取用户"""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """更新用户"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """删除用户（软删除）"""
        pass
    
    @abstractmethod
    async def list_users(
        self, 
        offset: int = 0, 
        limit: int = 10,
        status: Optional[UserStatus] = None,
        role: Optional[UserRole] = None,
        search: Optional[str] = None
    ) -> Tuple[List[User], int]:
        """获取用户列表"""
        pass
    
    @abstractmethod
    async def count_users(
        self, 
        status: Optional[UserStatus] = None,
        role: Optional[UserRole] = None
    ) -> int:
        """统计用户数量"""
        pass
    
    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """检查用户名是否存在"""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """检查邮箱是否存在"""
        pass

class HealthRepository(ABC):
    """健康数据仓库接口"""
    
    @abstractmethod
    async def get_health_summary(self, user_id: UUID) -> Optional[UserHealthSummary]:
        """获取用户健康摘要"""
        pass
    
    @abstractmethod
    async def update_health_summary(
        self, 
        user_id: UUID, 
        health_summary: UserHealthSummary
    ) -> UserHealthSummary:
        """更新用户健康摘要"""
        pass
    
    @abstractmethod
    async def add_health_metric(
        self, 
        user_id: UUID, 
        metric: HealthMetric
    ) -> bool:
        """添加健康指标"""
        pass
    
    @abstractmethod
    async def get_health_metrics(
        self,
        user_id: UUID,
        metric_names: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[HealthMetric]:
        """获取健康指标历史"""
        pass
    
    @abstractmethod
    async def update_constitution_scores(
        self,
        user_id: UUID,
        constitution_scores: Dict[str, float],
        dominant_constitution: Optional[ConstitutionType] = None
    ) -> bool:
        """更新体质评分"""
        pass
    
    @abstractmethod
    async def add_health_condition(
        self,
        user_id: UUID,
        condition: HealthCondition
    ) -> bool:
        """添加健康状况"""
        pass
    
    @abstractmethod
    async def update_health_condition(
        self,
        user_id: UUID,
        condition_name: str,
        status: str,
        notes: Optional[str] = None
    ) -> bool:
        """更新健康状况"""
        pass
    
    @abstractmethod
    async def get_health_conditions(
        self,
        user_id: UUID,
        status: Optional[str] = None
    ) -> List[HealthCondition]:
        """获取健康状况列表"""
        pass

class DeviceRepository(ABC):
    """设备仓库接口"""
    
    @abstractmethod
    async def bind_device(
        self,
        user_id: UUID,
        device_info: DeviceInfo
    ) -> str:
        """绑定设备"""
        pass
    
    @abstractmethod
    async def unbind_device(
        self,
        user_id: UUID,
        device_id: str
    ) -> bool:
        """解绑设备"""
        pass
    
    @abstractmethod
    async def get_user_devices(
        self,
        user_id: UUID,
        active_only: bool = True
    ) -> List[DeviceInfo]:
        """获取用户设备列表"""
        pass
    
    @abstractmethod
    async def get_device_info(
        self,
        device_id: str
    ) -> Optional[DeviceInfo]:
        """获取设备信息"""
        pass
    
    @abstractmethod
    async def update_device_activity(
        self,
        device_id: str,
        last_active_time: datetime
    ) -> bool:
        """更新设备活跃时间"""
        pass
    
    @abstractmethod
    async def is_device_bound(
        self,
        device_id: str
    ) -> bool:
        """检查设备是否已绑定"""
        pass
    
    @abstractmethod
    async def count_user_devices(
        self,
        user_id: UUID,
        active_only: bool = True
    ) -> int:
        """统计用户设备数量"""
        pass

class AuditRepository(ABC):
    """审计日志仓库接口"""
    
    @abstractmethod
    async def create_audit_log(
        self,
        user_id: UUID,
        action: str,
        target_user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """创建审计日志"""
        pass
    
    @abstractmethod
    async def get_audit_logs(
        self,
        user_id: Optional[UUID] = None,
        target_user_id: Optional[UUID] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        offset: int = 0,
        limit: int = 100
    ) -> Tuple[List[Dict[str, Any]], int]:
        """获取审计日志"""
        pass
    
    @abstractmethod
    async def get_user_activity_summary(
        self,
        user_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """获取用户活动摘要"""
        pass

class SessionRepository(ABC):
    """会话仓库接口"""
    
    @abstractmethod
    async def create_session(
        self,
        user_id: UUID,
        session_token: str,
        expires_at: datetime,
        device_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """创建会话"""
        pass
    
    @abstractmethod
    async def get_session(
        self,
        session_token: str
    ) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        pass
    
    @abstractmethod
    async def update_session_activity(
        self,
        session_token: str,
        last_activity: datetime
    ) -> bool:
        """更新会话活跃时间"""
        pass
    
    @abstractmethod
    async def invalidate_session(
        self,
        session_token: str
    ) -> bool:
        """使会话失效"""
        pass
    
    @abstractmethod
    async def invalidate_user_sessions(
        self,
        user_id: UUID,
        exclude_session: Optional[str] = None
    ) -> int:
        """使用户所有会话失效"""
        pass
    
    @abstractmethod
    async def cleanup_expired_sessions(self) -> int:
        """清理过期会话"""
        pass
    
    @abstractmethod
    async def get_user_active_sessions(
        self,
        user_id: UUID
    ) -> List[Dict[str, Any]]:
        """获取用户活跃会话"""
        pass

class CacheRepository(ABC):
    """缓存仓库接口"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        pass
    
    @abstractmethod
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """设置缓存值"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查缓存键是否存在"""
        pass
    
    @abstractmethod
    async def expire(self, key: str, ttl: int) -> bool:
        """设置缓存过期时间"""
        pass
    
    @abstractmethod
    async def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的缓存"""
        pass 