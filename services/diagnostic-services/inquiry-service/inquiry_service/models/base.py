"""
基础模型类

定义所有数据模型的基础类和通用字段。
"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

# SQLAlchemy 基础类
SQLAlchemyBase = declarative_base()


class BaseModel(PydanticBaseModel):
    """Pydantic 基础模型类"""

    class Config:
        # 允许从 ORM 对象创建
        from_attributes = True
        # 使用枚举值而不是枚举名称
        use_enum_values = True
        # 验证赋值
        validate_assignment = True
        # 允许任意类型
        arbitrary_types_allowed = True
        # JSON 编码器
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class TimestampMixin:
    """时间戳混入类"""

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间",
    )


class UUIDMixin:
    """UUID 混入类"""

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4, comment="主键ID")


class BaseEntity(SQLAlchemyBase, TimestampMixin, UUIDMixin):
    """SQLAlchemy 基础实体类"""

    __abstract__ = True

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    def update_from_dict(self, data: dict[str, Any]) -> None:
        """从字典更新属性"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


class PaginationParams(BaseModel):
    """分页参数"""

    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页大小")

    @property
    def offset(self) -> int:
        """计算偏移量"""
        return (self.page - 1) * self.size


class PaginationResult(BaseModel):
    """分页结果"""

    total: int = Field(description="总数量")
    page: int = Field(description="当前页码")
    size: int = Field(description="每页大小")
    pages: int = Field(description="总页数")
    has_next: bool = Field(description="是否有下一页")
    has_prev: bool = Field(description="是否有上一页")

    @classmethod
    def create(
        cls,
        total: int,
        page: int,
        size: int,
    ) -> "PaginationResult":
        """创建分页结果"""
        pages = (total + size - 1) // size
        return cls(
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1,
        )


class APIResponse(BaseModel):
    """API 响应基础类"""

    success: bool = Field(description="是否成功")
    message: str = Field(description="响应消息")
    code: str = Field(default="SUCCESS", description="响应代码")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

    @classmethod
    def success_response(
        cls,
        message: str = "操作成功",
        code: str = "SUCCESS",
    ) -> "APIResponse":
        """创建成功响应"""
        return cls(
            success=True,
            message=message,
            code=code,
        )

    @classmethod
    def error_response(
        cls,
        message: str,
        code: str = "ERROR",
    ) -> "APIResponse":
        """创建错误响应"""
        return cls(
            success=False,
            message=message,
            code=code,
        )


class APIDataResponse(APIResponse):
    """带数据的 API 响应"""

    data: Any | None = Field(default=None, description="响应数据")

    @classmethod
    def success_with_data(
        cls,
        data: Any,
        message: str = "操作成功",
        code: str = "SUCCESS",
    ) -> "APIDataResponse":
        """创建带数据的成功响应"""
        return cls(
            success=True,
            message=message,
            code=code,
            data=data,
        )


class APIPaginatedResponse(APIDataResponse):
    """分页 API 响应"""

    pagination: PaginationResult | None = Field(default=None, description="分页信息")

    @classmethod
    def success_with_pagination(
        cls,
        data: Any,
        pagination: PaginationResult,
        message: str = "操作成功",
        code: str = "SUCCESS",
    ) -> "APIPaginatedResponse":
        """创建带分页的成功响应"""
        return cls(
            success=True,
            message=message,
            code=code,
            data=data,
            pagination=pagination,
        )
