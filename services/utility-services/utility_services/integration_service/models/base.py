"""
base - 索克生活项目模块
"""

from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.ext.declarative import declarative_base

"""
基础数据模型
"""


Base = declarative_base()


class BaseModel(Base):
    """基础模型类"""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
