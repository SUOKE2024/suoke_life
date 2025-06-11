"""
用户管理服务数据模型

定义用户、角色、权限等数据模型
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

__version__ = "1.0.0"
__author__ = "索克生活团队"

# 导出主要类
__all__ = [
    "User",
    "Role", 
    "Permission",
    "UserSession",
    "UserProfile"
]


@dataclass
class User:
    """用户模型"""
    id: str
    username: str
    email: str
    password_hash: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    roles: List[str] = field(default_factory=list)
    profile: Optional['UserProfile'] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "roles": self.roles,
            "profile": self.profile.to_dict() if self.profile else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """从字典创建用户对象"""
        profile_data = data.get("profile")
        profile = UserProfile.from_dict(profile_data) if profile_data else None
        
        return cls(
            id=data["id"],
            username=data["username"],
            email=data["email"],
            password_hash=data["password_hash"],
            is_active=data.get("is_active", True),
            is_verified=data.get("is_verified", False),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.utcnow(),
            last_login=datetime.fromisoformat(data["last_login"]) if data.get("last_login") else None,
            roles=data.get("roles", []),
            profile=profile
        )


@dataclass
class UserProfile:
    """用户档案模型"""
    user_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    birth_date: Optional[datetime] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "gender": self.gender,
            "location": self.location,
            "preferences": self.preferences
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """从字典创建用户档案对象"""
        return cls(
            user_id=data["user_id"],
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            phone=data.get("phone"),
            avatar_url=data.get("avatar_url"),
            bio=data.get("bio"),
            birth_date=datetime.fromisoformat(data["birth_date"]) if data.get("birth_date") else None,
            gender=data.get("gender"),
            location=data.get("location"),
            preferences=data.get("preferences", {})
        )


@dataclass
class Role:
    """角色模型"""
    id: str
    name: str
    description: Optional[str] = None
    permissions: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "permissions": self.permissions,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Role':
        """从字典创建角色对象"""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            permissions=data.get("permissions", []),
            is_active=data.get("is_active", True),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow()
        )


@dataclass
class Permission:
    """权限模型"""
    id: str
    name: str
    resource: str
    action: str
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "resource": self.resource,
            "action": self.action,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Permission':
        """从字典创建权限对象"""
        return cls(
            id=data["id"],
            name=data["name"],
            resource=data["resource"],
            action=data["action"],
            description=data.get("description")
        )


@dataclass
class UserSession:
    """用户会话模型"""
    id: str
    user_id: str
    token: str
    refresh_token: Optional[str] = None
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow())
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "token": self.token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSession':
        """从字典创建会话对象"""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            token=data["token"],
            refresh_token=data.get("refresh_token"),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else datetime.utcnow(),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow(),
            last_accessed=datetime.fromisoformat(data["last_accessed"]) if data.get("last_accessed") else datetime.utcnow(),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            is_active=data.get("is_active", True)
        )


def create_default_roles() -> List[Role]:
    """创建默认角色"""
    return [
        Role(
            id="admin",
            name="管理员",
            description="系统管理员，拥有所有权限",
            permissions=["read", "write", "delete", "admin"]
        ),
        Role(
            id="user",
            name="普通用户",
            description="普通用户，拥有基本权限",
            permissions=["read"]
        ),
        Role(
            id="moderator",
            name="版主",
            description="版主，拥有内容管理权限",
            permissions=["read", "write", "moderate"]
        )
    ]


def create_default_permissions() -> List[Permission]:
    """创建默认权限"""
    return [
        Permission(id="read", name="读取", resource="*", action="read", description="读取权限"),
        Permission(id="write", name="写入", resource="*", action="write", description="写入权限"),
        Permission(id="delete", name="删除", resource="*", action="delete", description="删除权限"),
        Permission(id="admin", name="管理", resource="*", action="admin", description="管理权限"),
        Permission(id="moderate", name="审核", resource="content", action="moderate", description="内容审核权限")
    ]


def main() -> None:
    """主函数"""
    # 创建示例用户
    user = User(
        id="user123",
        username="testuser",
        email="test@suoke.life",
        password_hash="hashed_password"
    )
    
    print(f"创建用户: {user.username}")
    print(f"用户字典: {user.to_dict()}")


if __name__ == "__main__":
    main() 