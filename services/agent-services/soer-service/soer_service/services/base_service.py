"""
基础服务类

提供所有服务的通用功能和接口
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..core.database import get_mongodb, get_redis
from ..core.logging import get_logger
from ..config.settings import get_settings


class BaseService(ABC):
    """基础服务抽象类"""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.settings = get_settings()
        self._mongodb = None
        self._redis = None
    
    @property
    def mongodb(self):
        """获取 MongoDB 实例"""
        if self._mongodb is None:
            self._mongodb = get_mongodb()
        return self._mongodb
    
    @property
    def redis(self):
        """获取 Redis 实例"""
        if self._redis is None:
            self._redis = get_redis()
        return self._redis
    
    async def cache_get(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        try:
            return await self.redis.get(key)
        except Exception as e:
            self.logger.warning(f"缓存获取失败: {e}")
            return None
    
    async def cache_set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """设置缓存数据"""
        try:
            await self.redis.set(key, value, ex=expire)
            return True
        except Exception as e:
            self.logger.warning(f"缓存设置失败: {e}")
            return False
    
    async def cache_delete(self, key: str) -> bool:
        """删除缓存数据"""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            self.logger.warning(f"缓存删除失败: {e}")
            return False
    
    def generate_cache_key(self, prefix: str, *args) -> str:
        """生成缓存键"""
        return f"{prefix}:{':'.join(str(arg) for arg in args)}"
    
    async def log_operation(self, operation: str, user_id: str, details: Dict[str, Any] = None):
        """记录操作日志"""
        # 在测试环境下跳过数据库操作
        if self.settings.environment == "testing":
            self.logger.debug("测试环境：跳过操作日志记录")
            return
            
        log_data = {
            "operation": operation,
            "user_id": user_id,
            "service": self.__class__.__name__,
            "timestamp": "now",
            "details": details or {}
        }
        
        try:
            await self.mongodb.operation_logs.insert_one(log_data)
        except Exception as e:
            self.logger.error(f"操作日志记录失败: {e}")
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        pass 