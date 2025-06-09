"""
统一健康数据服务 - 索克生活项目
整合健康数据服务和数据库服务的统一数据管理服务

本服务包含以下子服务：
- health_data_service: 健康数据管理服务，负责健康数据的收集、处理和分析
- database_service: 数据库服务，提供统一的数据存储和查询接口

功能特性：
- 健康数据收集和验证
- 多模态健康数据处理
- 中医五诊数据管理
- 数据库事务管理
- 数据查询优化
- 健康数据分析和报告
- 数据安全和隐私保护
- 分布式数据存储
- 实时数据同步
"""

from typing import Dict, List, Any, Optional, Union
import asyncio
import logging
from .health_data_service import HealthDataService

__version__ = "1.0.0"
__author__ = "Suoke Life Team"
__email__ = "dev@suokelife.com"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class UnifiedHealthDataService:
    """
    统一健康数据服务主类
    管理健康数据服务和数据库服务的生命周期
    """
    
    def __init__(self):
        """初始化统一健康数据服务"""
        self.health_data_service = None
        self.database_service = None
        self.running = False
        logger.info("统一健康数据服务初始化完成")
    
    async def start_health_data_service(self) -> None:
        """启动健康数据服务"""
        try:
            from .health_data_service.services.health_data_service import HealthDataService
            self.health_data_service = HealthDataService()
            await self.health_data_service.start()
            logger.info("健康数据服务启动成功")
        except Exception as e:
            logger.error(f"健康数据服务启动失败: {e}")
            raise
    
    async def start_database_service(self) -> None:
        """启动数据库服务"""
        try:
            from .health_data_service.core.database import DatabaseService
            self.database_service = DatabaseService()
            await self.database_service.initialize()
            logger.info("数据库服务启动成功")
        except Exception as e:
            logger.error(f"数据库服务启动失败: {e}")
            raise
    
    async def start(self) -> None:
        """启动所有服务"""
        logger.info("正在启动统一健康数据服务...")
        self.running = True
        
        # 启动子服务
        await asyncio.gather(
            self.start_database_service(),
            self.start_health_data_service()
        )
        
        logger.info("统一健康数据服务启动完成")
    
    async def stop(self) -> None:
        """停止所有服务"""
        logger.info("正在停止统一健康数据服务...")
        self.running = False
        
        # 停止健康数据服务
        if self.health_data_service:
            await self.health_data_service.stop()
        
        # 停止数据库服务
        if self.database_service:
            await self.database_service.close()
        
        logger.info("统一健康数据服务停止完成")
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取服务健康状态"""
        return {
            "service": "unified-health-data-service",
            "version": __version__,
            "status": "running" if self.running else "stopped",
            "components": {
                "health_data_service": {
                    "status": "running" if self.health_data_service and hasattr(self.health_data_service, 'running') and self.health_data_service.running else "stopped"
                },
                "database_service": {
                    "status": "running" if self.database_service and hasattr(self.database_service, 'connected') and self.database_service.connected else "stopped"
                }
            }
        }
    
    async def process_health_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理健康数据"""
        if not self.health_data_service:
            raise RuntimeError("健康数据服务未启动")
        
        return await self.health_data_service.process_data(data)
    
    async def store_health_data(self, data: Dict[str, Any]) -> str:
        """存储健康数据"""
        if not self.database_service:
            raise RuntimeError("数据库服务未启动")
        
        return await self.database_service.store_data(data)
    
    async def query_health_data(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """查询健康数据"""
        if not self.database_service:
            raise RuntimeError("数据库服务未启动")
        
        return await self.database_service.query_data(query)

# 导出主要类和函数
__all__ = [
    "UnifiedHealthDataService",
    "HealthDataService",
    "__version__",
    "__author__",
    "__email__"
] 