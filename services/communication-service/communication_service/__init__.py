"""
通信服务 - 索克生活项目
整合消息总线和RAG服务的统一通信服务

本服务包含以下子服务：
- message_bus: 消息总线服务，负责系统间事件传递和通知
- rag_service: RAG检索增强生成服务，提供智能问答和知识检索

功能特性：
- gRPC 服务间通信
- Kafka 异步消息队列
- Redis 缓存和发布订阅
- 智能文档检索和生成
- 多模态数据处理
- 健康检查和监控
- 分布式追踪
"""

from typing import Dict, List, Any, Optional, Union
import asyncio
import logging
from .message_bus import MessageBusService
from .rag_service.main import main as rag_main

__version__ = "1.0.0"
__author__ = "Suoke Life Team"
__email__ = "dev@suokelife.com"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class CommunicationService:
    """
    统一通信服务主类
    管理消息总线和RAG服务的生命周期
    """
    
    def __init__(self):
        """初始化通信服务"""
        self.message_bus_service = None
        self.rag_service_task = None
        self.running = False
        logger.info("通信服务初始化完成")
    
    async def start_message_bus(self) -> None:
        """启动消息总线服务"""
        try:
            from .message_bus.main import MessageBusService
            self.message_bus_service = MessageBusService()
            await self.message_bus_service.start()
            logger.info("消息总线服务启动成功")
        except Exception as e:
            logger.error(f"消息总线服务启动失败: {e}")
            raise
    
    def start_rag_service(self) -> None:
        """启动RAG服务"""
        try:
            # RAG服务在独立进程中运行
            self.rag_service_task = asyncio.create_task(
                asyncio.to_thread(rag_main)
            )
            logger.info("RAG服务启动成功")
        except Exception as e:
            logger.error(f"RAG服务启动失败: {e}")
            raise
    
    async def start(self) -> None:
        """启动所有服务"""
        logger.info("正在启动通信服务...")
        self.running = True
        
        # 启动子服务
        await asyncio.gather(
            self.start_message_bus(),
            asyncio.to_thread(self.start_rag_service)
        )
        
        logger.info("通信服务启动完成")
    
    async def stop(self) -> None:
        """停止所有服务"""
        logger.info("正在停止通信服务...")
        self.running = False
        
        # 停止消息总线服务
        if self.message_bus_service:
            await self.message_bus_service.stop()
        
        # 停止RAG服务
        if self.rag_service_task:
            self.rag_service_task.cancel()
            try:
                await self.rag_service_task
            except asyncio.CancelledError:
                pass
        
        logger.info("通信服务停止完成")
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取服务健康状态"""
        return {
            "service": "communication-service",
            "version": __version__,
            "status": "running" if self.running else "stopped",
            "components": {
                "message_bus": {
                    "status": "running" if self.message_bus_service and self.message_bus_service.running else "stopped"
                },
                "rag_service": {
                    "status": "running" if self.rag_service_task and not self.rag_service_task.done() else "stopped"
                }
            }
        }

# 导出主要类和函数
__all__ = [
    "CommunicationService",
    "MessageBusService",
    "rag_main",
    "__version__",
    "__author__",
    "__email__"
] 