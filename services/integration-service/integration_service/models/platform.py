"""
platform - 索克生活项目模块
"""

from .base import BaseModel
from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

"""
平台模型
"""




class Platform(BaseModel):
    """第三方平台模型"""

    __tablename__ = "platforms"

    id = Column(String(50), primary_key=True, index=True)  # 覆盖基类的 id
    name = Column(String(100), nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    is_enabled = Column(Boolean, default=True, nullable=False)
    api_base_url = Column(String(200), nullable=True)
    auth_type = Column(String(50), nullable=False)  # oauth2, api_key, etc.

    # 关联关系
    health_data = relationship("HealthData", back_populates="platform")
    user_auths = relationship("UserPlatformAuth", back_populates="platform")

    def __repr__(self) -> str:
        return f"<Platform(id={self.id}, name={self.name})>"

    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'platform'
        ordering = ['-created_at']


class PlatformConfig(BaseModel):
    """平台配置模型"""

    __tablename__ = "platform_configs"

    platform_id = Column(String(50), nullable=False, index=True)
    config_key = Column(String(100), nullable=False)
    config_value = Column(String(500), nullable=True)
    is_encrypted = Column(Boolean, default=False, nullable=False)
    description = Column(String(200), nullable=True)

    def __repr__(self) -> str:
        return f"<PlatformConfig(platform_id={self.platform_id}, key={self.config_key})>"
