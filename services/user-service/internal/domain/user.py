"""
用户领域实体
定义用户相关的核心业务逻辑和规则
"""
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from enum import Enum

from pydantic import BaseModel, Field, validator

class UserStatus(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"

class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    USER = "user"
    HEALTH_PROVIDER = "health_provider"
    RESEARCHER = "researcher"
    AGENT = "agent"

class Gender(str, Enum):
    """性别枚举"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"

class User(BaseModel):
    """用户领域实体"""
    
    user_id: UUID = Field(default_factory=uuid4)
    username: str
    email: str
    password_hash: str
    phone: Optional[str] = None
    full_name: Optional[str] = None
    gender: Optional[Gender] = None
    birth_date: Optional[datetime] = None
    avatar_url: Optional[str] = None
    
    # 状态和角色
    status: UserStatus = UserStatus.ACTIVE
    roles: List[UserRole] = Field(default_factory=lambda: [UserRole.USER])
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
    
    # 扩展信息
    metadata: Dict[str, str] = Field(default_factory=dict)
    preferences: Dict[str, str] = Field(default_factory=dict)
    
    # AI代理分配
    agent_assignments: Dict[str, str] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    
    def __init__(self, **data):
        super().__init__(**data)
        self._domain_events: List[DomainEvent] = []
    
    @property
    def domain_events(self) -> List['DomainEvent']:
        """获取领域事件"""
        return self._domain_events.copy()
    
    def clear_domain_events(self):
        """清除领域事件"""
        self._domain_events.clear()
    
    def add_domain_event(self, event: 'DomainEvent'):
        """添加领域事件"""
        self._domain_events.append(event)
    
    @validator('username')
    def validate_username(cls, v):
        """验证用户名"""
        if not v or len(v) < 3:
            raise ValueError("用户名长度不能少于3个字符")
        if len(v) > 50:
            raise ValueError("用户名长度不能超过50个字符")
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("用户名只能包含字母、数字、下划线和连字符")
        return v
    
    @validator('email')
    def validate_email(cls, v):
        """验证邮箱格式"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError("邮箱格式不正确")
        return v.lower()
    
    @validator('phone')
    def validate_phone(cls, v):
        """验证手机号格式"""
        if v is None:
            return v
        import re
        # 支持中国大陆手机号格式
        pattern = r'^1[3-9]\d{9}$'
        if not re.match(pattern, v):
            raise ValueError("手机号格式不正确")
        return v
    
    def is_active(self) -> bool:
        """检查用户是否活跃"""
        return self.status == UserStatus.ACTIVE
    
    def is_suspended(self) -> bool:
        """检查用户是否被暂停"""
        return self.status == UserStatus.SUSPENDED
    
    def is_deleted(self) -> bool:
        """检查用户是否被删除"""
        return self.status == UserStatus.DELETED
    
    def has_role(self, role: UserRole) -> bool:
        """检查用户是否具有指定角色"""
        return role in self.roles
    
    def add_role(self, role: UserRole):
        """添加角色"""
        if role not in self.roles:
            self.roles.append(role)
            self.updated_at = datetime.utcnow()
            self.add_domain_event(UserRoleAddedEvent(
                user_id=self.user_id,
                role=role,
                timestamp=datetime.utcnow()
            ))
    
    def remove_role(self, role: UserRole):
        """移除角色"""
        if role in self.roles:
            self.roles.remove(role)
            self.updated_at = datetime.utcnow()
            self.add_domain_event(UserRoleRemovedEvent(
                user_id=self.user_id,
                role=role,
                timestamp=datetime.utcnow()
            ))
    
    def activate(self):
        """激活用户"""
        if self.status != UserStatus.ACTIVE:
            old_status = self.status
            self.status = UserStatus.ACTIVE
            self.updated_at = datetime.utcnow()
            self.add_domain_event(UserStatusChangedEvent(
                user_id=self.user_id,
                old_status=old_status,
                new_status=self.status,
                timestamp=datetime.utcnow()
            ))
    
    def suspend(self, reason: Optional[str] = None):
        """暂停用户"""
        if self.status != UserStatus.SUSPENDED:
            old_status = self.status
            self.status = UserStatus.SUSPENDED
            self.updated_at = datetime.utcnow()
            self.add_domain_event(UserSuspendedEvent(
                user_id=self.user_id,
                reason=reason,
                timestamp=datetime.utcnow()
            ))
    
    def soft_delete(self):
        """软删除用户"""
        if self.status != UserStatus.DELETED:
            old_status = self.status
            self.status = UserStatus.DELETED
            self.updated_at = datetime.utcnow()
            self.add_domain_event(UserDeletedEvent(
                user_id=self.user_id,
                timestamp=datetime.utcnow()
            ))
    
    def update_login_time(self):
        """更新最后登录时间"""
        self.last_login_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.add_domain_event(UserLoginEvent(
            user_id=self.user_id,
            timestamp=self.last_login_at
        ))
    
    def update_profile(
        self,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        gender: Optional[Gender] = None,
        birth_date: Optional[datetime] = None,
        avatar_url: Optional[str] = None
    ):
        """更新用户资料"""
        changes = {}
        
        if full_name is not None and full_name != self.full_name:
            changes['full_name'] = {'old': self.full_name, 'new': full_name}
            self.full_name = full_name
        
        if phone is not None and phone != self.phone:
            changes['phone'] = {'old': self.phone, 'new': phone}
            self.phone = phone
        
        if gender is not None and gender != self.gender:
            changes['gender'] = {'old': self.gender, 'new': gender}
            self.gender = gender
        
        if birth_date is not None and birth_date != self.birth_date:
            changes['birth_date'] = {'old': self.birth_date, 'new': birth_date}
            self.birth_date = birth_date
        
        if avatar_url is not None and avatar_url != self.avatar_url:
            changes['avatar_url'] = {'old': self.avatar_url, 'new': avatar_url}
            self.avatar_url = avatar_url
        
        if changes:
            self.updated_at = datetime.utcnow()
            self.add_domain_event(UserProfileUpdatedEvent(
                user_id=self.user_id,
                changes=changes,
                timestamp=datetime.utcnow()
            ))
    
    def assign_agent(self, agent_type: str, agent_id: str):
        """分配AI代理"""
        if self.agent_assignments.get(agent_type) != agent_id:
            old_agent_id = self.agent_assignments.get(agent_type)
            self.agent_assignments[agent_type] = agent_id
            self.updated_at = datetime.utcnow()
            self.add_domain_event(AgentAssignedEvent(
                user_id=self.user_id,
                agent_type=agent_type,
                old_agent_id=old_agent_id,
                new_agent_id=agent_id,
                timestamp=datetime.utcnow()
            ))
    
    def get_age(self) -> Optional[int]:
        """计算用户年龄"""
        if not self.birth_date:
            return None
        
        today = datetime.now().date()
        birth_date = self.birth_date.date() if isinstance(self.birth_date, datetime) else self.birth_date
        
        age = today.year - birth_date.year
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1
        
        return age
    
    def can_perform_action(self, action: str) -> bool:
        """检查用户是否可以执行指定操作"""
        if not self.is_active():
            return False
        
        # 基于角色的权限检查
        role_permissions = {
            UserRole.ADMIN: {'*'},  # 管理员拥有所有权限
            UserRole.HEALTH_PROVIDER: {
                'read_health_data', 'write_health_data', 
                'create_health_plan', 'update_health_plan'
            },
            UserRole.RESEARCHER: {
                'read_health_data', 'export_data', 'create_research'
            },
            UserRole.USER: {
                'read_own_data', 'update_own_profile', 
                'bind_device', 'unbind_device'
            },
            UserRole.AGENT: {
                'read_health_data', 'create_assessment', 
                'update_health_score'
            }
        }
        
        for role in self.roles:
            permissions = role_permissions.get(role, set())
            if '*' in permissions or action in permissions:
                return True
        
        return False

# 领域事件基类
class DomainEvent(BaseModel):
    """领域事件基类"""
    event_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }

class UserCreatedEvent(DomainEvent):
    """用户创建事件"""
    user_id: UUID
    username: str
    email: str

class UserStatusChangedEvent(DomainEvent):
    """用户状态变更事件"""
    user_id: UUID
    old_status: UserStatus
    new_status: UserStatus

class UserSuspendedEvent(DomainEvent):
    """用户暂停事件"""
    user_id: UUID
    reason: Optional[str] = None

class UserDeletedEvent(DomainEvent):
    """用户删除事件"""
    user_id: UUID

class UserLoginEvent(DomainEvent):
    """用户登录事件"""
    user_id: UUID

class UserRoleAddedEvent(DomainEvent):
    """用户角色添加事件"""
    user_id: UUID
    role: UserRole

class UserRoleRemovedEvent(DomainEvent):
    """用户角色移除事件"""
    user_id: UUID
    role: UserRole

class UserProfileUpdatedEvent(DomainEvent):
    """用户资料更新事件"""
    user_id: UUID
    changes: Dict[str, Dict[str, str]]

class AgentAssignedEvent(DomainEvent):
    """AI代理分配事件"""
    user_id: UUID
    agent_type: str
    old_agent_id: Optional[str]
    new_agent_id: str 