"""健康数据模型"""

from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from user_service.database import Base


class HealthSummary(Base):
    """用户健康摘要模型"""
    
    __tablename__ = "health_summaries"
    
    # 主键
    summary_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 外键
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True, unique=True)
    
    # 健康指标
    health_score = Column(Float, nullable=False, default=0.0)  # 综合健康分数 0-100
    metrics = Column(JSON, nullable=False, default=dict)  # 详细健康指标
    
    # 时间戳
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="health_summary")
    
    def __repr__(self):
        return f"<HealthSummary(summary_id={self.summary_id}, user_id={self.user_id}, health_score={self.health_score})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "summary_id": self.summary_id,
            "user_id": self.user_id,
            "health_score": self.health_score,
            "metrics": self.metrics,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class HealthDataPoint(Base):
    """健康数据点模型"""
    
    __tablename__ = "health_data_points"
    
    # 主键
    data_point_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 外键
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    
    # 数据信息
    metric_type = Column(String, nullable=False, index=True)  # heart_rate, steps, weight, etc.
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # 元数据
    metadata = Column(JSON, nullable=False, default=dict)
    source = Column(String, nullable=False, default="manual")  # manual, device, api
    device_id = Column(String, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="health_data")
    
    def __repr__(self):
        return f"<HealthDataPoint(data_point_id={self.data_point_id}, user_id={self.user_id}, metric_type={self.metric_type}, value={self.value})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "data_point_id": self.data_point_id,
            "user_id": self.user_id,
            "metric_type": self.metric_type,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata,
            "source": self.source,
            "device_id": self.device_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class HealthGoal(Base):
    """健康目标模型"""
    
    __tablename__ = "health_goals"
    
    # 主键
    goal_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 外键
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    
    # 目标信息
    goal_type = Column(String, nullable=False)  # daily_steps, weight_loss, etc.
    target_value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    deadline = Column(DateTime, nullable=True)
    description = Column(String, nullable=True)
    
    # 状态
    is_active = Column(Boolean, nullable=False, default=True)
    progress = Column(Float, nullable=False, default=0.0)  # 0.0 - 1.0
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="health_goals")
    
    def __repr__(self):
        return f"<HealthGoal(goal_id={self.goal_id}, user_id={self.user_id}, goal_type={self.goal_type})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "goal_id": self.goal_id,
            "user_id": self.user_id,
            "goal_type": self.goal_type,
            "target_value": self.target_value,
            "unit": self.unit,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "description": self.description,
            "is_active": self.is_active,
            "progress": self.progress,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 