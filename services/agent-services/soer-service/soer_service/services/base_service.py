"""
基础服务类

提供所有服务的通用功能
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..core.database import get_mongodb, get_redis
from ..core.monitoring import record_database_operation


class BaseService(ABC):
    """基础服务抽象类"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.mongodb = get_mongodb()
        self.redis = get_redis()
    
    async def log_operation(self, operation: str, success: bool, details: Optional[Dict[str, Any]] = None):
        """记录操作日志"""
        if success:
            self.logger.info(f"操作成功: {operation}", extra=details or {})
        else:
            self.logger.error(f"操作失败: {operation}", extra=details or {})
        
        # 记录到监控系统
        record_database_operation(
            database=self.__class__.__name__,
            operation=operation,
            success=success
        )
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        pass
