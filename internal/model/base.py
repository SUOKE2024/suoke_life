"""
Base Model Classes
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel as PydanticBaseModel, Field

# SQLAlchemy Base
SQLAlchemyBase = declarative_base()


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