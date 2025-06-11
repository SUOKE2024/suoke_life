"""
通信服务 - 索克生活项目
整合消息总线和RAG服务的统一通信服务

功能特性：
- 消息总线服务
- RAG检索增强生成服务
- 智能问答和知识检索
- 多模态数据处理
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

__version__ = "1.0.0"
__author__ = "Suoke Life Team"
__email__ = "dev@suokelife.com"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class MessageBusService:
    """消息总线服务"""
    
    def __init__(self):
        """初始化消息总线服务"""
        self.running = False
        logger.info("消息总线服务初始化完成")
    
    async def start(self):
        """启动消息总线服务"""
        self.running = True
        logger.info("消息总线服务启动成功")
    
    async def stop(self):
        """停止消息总线服务"""
        self.running = False
        logger.info("消息总线服务停止完成")

class RAGService:
    """RAG检索增强生成服务"""
    
    def __init__(self):
        """初始化RAG服务"""
        self.running = False
        logger.info("RAG服务初始化完成")
    
    async def start(self):
        """启动RAG服务"""
        self.running = True
        logger.info("RAG服务启动成功")
    
    async def stop(self):
        """停止RAG服务"""
        self.running = False
        logger.info("RAG服务停止完成")

class CommunicationService:
    """
    统一通信服务主类
    管理消息总线和RAG服务的生命周期
    """
    
    def __init__(self):
        """初始化通信服务"""
        self.message_bus_service = MessageBusService()
        self.rag_service = RAGService()
        self.running = False
        logger.info("通信服务初始化完成")
    
    async def start(self) -> None:
        """启动所有服务"""
        logger.info("正在启动通信服务...")
        self.running = True
        
        # 启动子服务
        await asyncio.gather(
            self.message_bus_service.start(),
            self.rag_service.start()
        )
        
        logger.info("通信服务启动完成")
    
    async def stop(self) -> None:
        """停止所有服务"""
        logger.info("正在停止通信服务...")
        self.running = False
        
        # 停止子服务
        await asyncio.gather(
            self.message_bus_service.stop(),
            self.rag_service.stop()
        )
        
        logger.info("通信服务停止完成")
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取服务健康状态"""
        return {
            "service": "communication-service",
            "version": __version__,
            "status": "running" if self.running else "stopped",
            "components": {
                "message_bus": {
                    "status": "running" if self.message_bus_service.running else "stopped"
                },
                "rag_service": {
                    "status": "running" if self.rag_service.running else "stopped"
                }
            }
        }

# 为了向后兼容，添加MessageBus别名
MessageBus = MessageBusService

# 导出主要类和函数
__all__ = [
    "CommunicationService",
    "MessageBusService",
    "MessageBus",  # 添加别名支持
    "RAGService",
    "__version__",
    "__author__",
    "__email__"
] 