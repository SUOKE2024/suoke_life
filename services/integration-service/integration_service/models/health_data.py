"""
health_data - 索克生活项目模块
"""

from .base import BaseModel
from enum import Enum
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import JSON, Column, Float, ForeignKey, String
from sqlalchemy.orm import relationship

"""
健康数据模型
"""





class HealthDataType(str, Enum):
    """健康数据类型"""
    STEPS = "steps"
    HEART_RATE = "heart_rate"
    BLOOD_PRESSURE = "blood_pressure"
    WEIGHT = "weight"
    HEIGHT = "height"
    SLEEP = "sleep"
    EXERCISE = "exercise"
    CALORIES = "calories"
    DISTANCE = "distance"
    BLOOD_GLUCOSE = "blood_glucose"
    BODY_TEMPERATURE = "body_temperature"
    OXYGEN_SATURATION = "oxygen_saturation"


class HealthData(BaseModel):
    """健康数据模型"""

    __tablename__ = "health_data"

    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    platform_id = Column(String(50), ForeignKey("platforms.id"), nullable=False, index=True)
    data_type = Column(SQLEnum(HealthDataType), nullable=False, index=True)
    value = Column(Float, nullable=True)
    unit = Column(String(20), nullable=True)
    extra_data = Column(JSON, nullable=True)
    source_id = Column(String(100), nullable=True)  # 第三方平台的数据ID

    # 关联关系
    user = relationship("User", back_populates="health_data")
    platform = relationship("Platform", back_populates="health_data")

    def __repr__(self) -> str:
        return f"<HealthData(user_id={self.user_id}, type={self.data_type}, value={self.value})>"
    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'healthdata'
        ordering = ['-created_at']

