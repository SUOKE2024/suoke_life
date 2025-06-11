
"""
user - 索克生活项目模块
"""

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from .base import BaseModel

"""
用户模型
"""




class User(BaseModel):
    """用户模型"""

    __tablename__ = "users"

    id = Column(String(50), primary_key = True, index = True)  # 覆盖基类的 id
    username = Column(String(100), unique = True, nullable = False, index = True)
    email = Column(String(200), unique = True, nullable = True, index = True)
    phone = Column(String(20), unique = True, nullable = True, index = True)
    is_active = Column(Boolean, default = True, nullable = False)
    profile = Column(JSON, nullable = True)  # 用户档案信息

    # 关联关系
    health_data = relationship("HealthData", back_populates = "user")
    platform_auths = relationship("UserPlatformAuth", back_populates = "user")

    def __repr__(self) -> str:
        """TODO: 添加文档字符串"""
        return f"<User(id = {self.id}, username = {self.username})>"

    class Meta:
        """TODO: 添加文档字符串"""
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields = ['created_at']),
            # models.Index(fields = ['user_id']),
            # models.Index(fields = ['status']),
        ]
        # 数据库表选项
        db_table = 'user'
        ordering = [' - created_at']


class UserPlatformAuth(BaseModel):
    """用户平台授权模型"""

    __tablename__ = "user_platform_auths"

    user_id = Column(String(50), ForeignKey("users.id"), nullable = False, index = True)
    platform_id = Column(String(50), ForeignKey("platforms.id"), nullable = False, index = True)
    access_token = Column(String(500), nullable = True)
    refresh_token = Column(String(500), nullable = True)
    token_expires_at = Column(DateTime, nullable = True)
    is_active = Column(Boolean, default = True, nullable = False)
    auth_metadata = Column(JSON, nullable = True)  # 额外的认证信息

    # 关联关系
    user = relationship("User", back_populates = "platform_auths")
    platform = relationship("Platform", back_populates = "user_auths")

    def __repr__(self) -> str:
        """TODO: 添加文档字符串"""
        return f"<UserPlatformAuth(user_id = {self.user_id}, platform_id = {self.platform_id})>"
