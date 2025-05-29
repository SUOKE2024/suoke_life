"""
健康数据模型
"""

from enum import Enum

from sqlalchemy import JSON, Column, Float, ForeignKey, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from .base import BaseModel


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
    metadata = Column(JSON, nullable=True)
    source_id = Column(String(100), nullable=True)  # 第三方平台的数据ID

    # 关联关系
    user = relationship("User", back_populates="health_data")
    platform = relationship("Platform", back_populates="health_data")

    def __repr__(self) -> str:
        return f"<HealthData(user_id={self.user_id}, type={self.data_type}, value={self.value})>"
