"""
Base Model Classes
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel as PydanticBaseModel, Field
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

# SQLAlchemy Base
SQLAlchemyBase = declarative_base()


@dataclass
class BaseModel(ABC):
    """基础模型类"""
    id: Optional[str] = None
    created_at: Optional[datetime] = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典创建实例"""
        # 处理datetime字段
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)


@dataclass
class BaseDBModel(BaseModel):
    """数据库模型基类"""
    version: int = 1
    is_active: bool = True
    extra_metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    def update_timestamp(self):
        """更新时间戳"""
        self.updated_at = datetime.now()


@dataclass
class BaseRequest(ABC):
    """基础请求模型"""
    user_id: str
    request_id: Optional[str] = None
    timestamp: Optional[datetime] = field(default_factory=datetime.now)


@dataclass
class BaseResponse(ABC):
    """基础响应模型"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    timestamp: Optional[datetime] = field(default_factory=datetime.now)


class BaseDBModel(SQLAlchemyBase):
    """SQLAlchemy基础模型"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)


class BaseModel(PydanticBaseModel):
    """Pydantic基础模型"""
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BaseResponse(BaseModel):
    """API响应基础模型"""
    success: bool = True
    message: str = "操作成功"
    timestamp: datetime = Field(default_factory=datetime.now)


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页数量")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PaginationResponse(BaseModel):
    """分页响应"""
    total: int = Field(description="总数量")
    page: int = Field(description="当前页码")
    size: int = Field(description="每页数量")
    pages: int = Field(description="总页数")
    
    @classmethod
    def create(cls, total: int, page: int, size: int):
        pages = (total + size - 1) // size
        return cls(
            total=total,
            page=page,
            size=size,
            pages=pages
        ) 