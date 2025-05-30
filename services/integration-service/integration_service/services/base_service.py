"""
基础服务类
"""

from typing import Generic, TypeVar

from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)


class BaseService(Generic[ModelType]):
    """基础服务类"""

    def __init__(self, model: type[ModelType], db: Session):
        self.model = model
        self.db = db

    async def create(self, obj_in: dict) -> ModelType:
        """创建对象"""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    async def get(self, id: int) -> ModelType | None:
        """根据ID获取对象"""
        return self.db.query(self.model).filter(self.model.id == id).first()

    async def get_multi(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """获取多个对象"""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    async def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        """更新对象"""
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> ModelType | None:
        """删除对象"""
        obj = self.db.query(self.model).filter(self.model.id == id).first()
        if obj:
            self.db.delete(obj)
            self.db.commit()
        return obj
