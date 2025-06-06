"""
device - 索克生活项目模块
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from typing import Dict, Any, Optional
from user_service.database import Base
import uuid

"""用户设备数据模型"""




class UserDevice(Base):
    """用户设备模型"""
    
    __tablename__ = "user_devices"
    
    # 主键
    binding_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 外键
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    
    # 设备信息
    device_id = Column(String, nullable=False, index=True)
    device_type = Column(String, nullable=False)  # mobile, tablet, smartwatch, etc.
    device_name = Column(String, nullable=True)
    device_metadata = Column(JSON, nullable=False, default=dict)
    
    # 绑定信息
    binding_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_active = Column(Boolean, nullable=False, default=True)
    last_active_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="devices")
    
    def __repr__(self):
        return f"<UserDevice(binding_id={self.binding_id}, user_id={self.user_id}, device_id={self.device_id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "binding_id": self.binding_id,
            "user_id": self.user_id,
            "device_id": self.device_id,
            "device_type": self.device_type,
            "device_name": self.device_name,
            "device_metadata": self.device_metadata,
            "binding_time": self.binding_time.isoformat() if self.binding_time else None,
            "is_active": self.is_active,
            "last_active_time": self.last_active_time.isoformat() if self.last_active_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 