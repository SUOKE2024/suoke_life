"""
数据库基础模型

定义所有数据库模型的基类和通用字段。
"""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """数据库模型基类"""

    # 通用字段
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def __repr__(self) -> str:
        """字符串表示"""
        class_name = self.__class__.__name__
        attrs = []
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            attrs.append(f"{column.name}={value!r}")
        return f"{class_name}({', '.join(attrs)})"
