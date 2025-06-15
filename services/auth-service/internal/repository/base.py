"""
仓储基类

提供通用的数据访问功能和模式。
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, delete, and_, or_

from internal.db import get_db_session

T = TypeVar('T')


class BaseRepository(Generic[T], ABC):
    """仓储基类"""
    
    def __init__(self, model_class: type[T]):
        self.model_class = model_class
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def get_session(self) -> AsyncSession:
        """获取数据库会话"""
        async for session in get_db_session():
            return session
    
    async def create(self, entity: T) -> T:
        """创建实体"""
        async with await self.get_session() as session:
            session.add(entity)
            await session.commit()
            await session.refresh(entity)
            return entity
    
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """根据ID获取实体"""
        async with await self.get_session() as session:
            result = await session.execute(
                select(self.model_class).where(self.model_class.id == entity_id)
            )
            return result.scalar_one_or_none()
    
    async def update(self, entity_id: str, update_data: Dict[str, Any]) -> Optional[T]:
        """更新实体"""
        async with await self.get_session() as session:
            # 先获取实体
            entity = await session.get(self.model_class, entity_id)
            if not entity:
                return None
            
            # 更新字段
            for key, value in update_data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            
            await session.commit()
            await session.refresh(entity)
            return entity
    
    async def delete(self, entity_id: str) -> bool:
        """删除实体"""
        async with await self.get_session() as session:
            result = await session.execute(
                delete(self.model_class).where(self.model_class.id == entity_id)
            )
            await session.commit()
            return result.rowcount > 0
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """获取所有实体"""
        async with await self.get_session() as session:
            result = await session.execute(
                select(self.model_class).offset(skip).limit(limit)
            )
            return list(result.scalars().all())
    
    async def count(self) -> int:
        """获取实体总数"""
        async with await self.get_session() as session:
            result = await session.execute(
                select(self.model_class).count()
            )
            return result.scalar()
    
    async def exists(self, entity_id: str) -> bool:
        """检查实体是否存在"""
        entity = await self.get_by_id(entity_id)
        return entity is not None


class CacheableRepository(BaseRepository[T]):
    """支持缓存的仓储基类"""
    
    def __init__(self, model_class: type[T], cache_ttl: int = 300):
        super().__init__(model_class)
        self.cache_ttl = cache_ttl
        self._cache = {}
    
    def _get_cache_key(self, key: str) -> str:
        """生成缓存键"""
        return f"{self.model_class.__name__}:{key}"
    
    async def get_by_id_cached(self, entity_id: str) -> Optional[T]:
        """带缓存的根据ID获取实体"""
        cache_key = self._get_cache_key(entity_id)
        
        # 检查缓存
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # 从数据库获取
        entity = await self.get_by_id(entity_id)
        
        # 缓存结果
        if entity:
            self._cache[cache_key] = entity
        
        return entity
    
    async def invalidate_cache(self, entity_id: str):
        """使缓存失效"""
        cache_key = self._get_cache_key(entity_id)
        if cache_key in self._cache:
            del self._cache[cache_key]
    
    async def update(self, entity_id: str, update_data: Dict[str, Any]) -> Optional[T]:
        """更新实体并使缓存失效"""
        result = await super().update(entity_id, update_data)
        await self.invalidate_cache(entity_id)
        return result
    
    async def delete(self, entity_id: str) -> bool:
        """删除实体并使缓存失效"""
        result = await super().delete(entity_id)
        if result:
            await self.invalidate_cache(entity_id)
        return result 