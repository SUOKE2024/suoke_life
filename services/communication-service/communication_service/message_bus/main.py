"""
索克生活事件驱动消息总线服务
集成智能体协同、健康数据处理和智能数据访问
"""

import asyncio
import os
import signal
import sys
from typing import Any, Optional

import structlog
from prometheus_client import start_http_server

# 导入事件总线组件
from ..event_bus.core.event_bus import SuokeEventBus, initialize_event_bus
from ..event_bus.core.event_store import EventStore, initialize_event_store
from ..event_bus.handlers.agent_handlers import (
    AgentCollaborationOrchestrator,
    AgentEventHandlers,
)
from ..event_bus.handlers.health_handlers import HealthEventHandlers
from ..event_bus.utils.event_router import (
    CacheService,
    DatabaseService,
    DataConsistencyManager,
    SmartDataAccessRouter,
)

# 配置结构化日志
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


class SuokeMessageBusService:
    """索克生活消息总线服务"""

    def __init__(self):
        """初始化消息总线服务"""
        self.running = False
        self._shutdown_event = asyncio.Event()

        # 配置参数
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.database_url = os.getenv(
            "DATABASE_URL", "postgresql://suoke:suoke123@localhost:5432/suoke_db"
        )
        self.service_name = os.getenv("SERVICE_NAME", "message-bus-service")
        self.metrics_port = int(os.getenv("METRICS_PORT", "8000"))

        # 核心组件
        self.event_bus: Optional[SuokeEventBus] = None
        self.event_store: Optional[EventStore] = None
        self.cache_service: Optional[CacheService] = None
        self.database_service: Optional[DatabaseService] = None

        # 事件处理器
        self.agent_handlers: Optional[AgentEventHandlers] = None
        self.health_handlers: Optional[HealthEventHandlers] = None
        self.data_router: Optional[SmartDataAccessRouter] = None
        self.consistency_manager: Optional[DataConsistencyManager] = None

        # 协同编排器
        self.collaboration_orchestrator: Optional[AgentCollaborationOrchestrator] = None

    async def initialize_components(self) -> None:
        """初始化所有组件"""
        try:
            logger.info("开始初始化消息总线组件...")

            # 1. 初始化事件总线
            self.event_bus = await initialize_event_bus(
                redis_url=self.redis_url, service_name=self.service_name
            )
            logger.info("事件总线初始化完成")

            # 2. 初始化事件存储
            self.event_store = await initialize_event_store(
                database_url=self.database_url
            )
            logger.info("事件存储初始化完成")

            # 3. 初始化缓存服务
            self.cache_service = CacheService(self.redis_url)
            await self.cache_service.initialize()
            logger.info("缓存服务初始化完成")

            # 4. 初始化数据库服务
            self.database_service = DatabaseService(self.database_url)
            logger.info("数据库服务初始化完成")

            # 5. 初始化智能数据路由器
            self.data_router = SmartDataAccessRouter(
                self.event_bus, self.cache_service, self.database_service
            )
            logger.info("智能数据路由器初始化完成")

            # 6. 初始化数据一致性管理器
            self.consistency_manager = DataConsistencyManager(
                self.event_bus, self.cache_service, self.database_service
            )
            await self.consistency_manager.register_consistency_handlers()
            logger.info("数据一致性管理器初始化完成")

            # 7. 初始化智能体事件处理器
            self.agent_handlers = AgentEventHandlers(self.event_bus, self.event_store)
            await self.agent_handlers.register_handlers()
            logger.info("智能体事件处理器初始化完成")

            # 8. 初始化健康数据事件处理器
            self.health_handlers = HealthEventHandlers(self.event_bus, self.event_store)
            await self.health_handlers.register_handlers()
            logger.info("健康数据事件处理器初始化完成")

            # 9. 初始化协同编排器
            self.collaboration_orchestrator = AgentCollaborationOrchestrator(
                self.event_bus
            )
            logger.info("智能体协同编排器初始化完成")

            logger.info("所有消息总线组件初始化完成")

        except Exception as e:
            logger.error("消息总线组件初始化失败", error=str(e))
            raise

    async def start(self) -> None:
        """启动消息总线服务"""
        try:
            logger.info("启动索克生活消息总线服务...", service=self.service_name)

            # 初始化组件
            await self.initialize_components()

            # 启动Prometheus监控服务器
            start_http_server(self.metrics_port)
            logger.info("Prometheus监控服务器已启动", port=self.metrics_port)

            # 启动健康检查任务
            asyncio.create_task(self._health_check_loop())

            # 启动事件统计任务
            asyncio.create_task(self._statistics_loop())

            # 启动数据清理任务
            asyncio.create_task(self._cleanup_loop())

            self.running = True
            logger.info("消息总线服务启动成功", service=self.service_name)

            # 发布服务启动事件
            await self.event_bus.publish(
                "system.service.started",
                {
                    "service_name": self.service_name,
                    "version": "1.0.0",
                    "components": [
                        "event_bus",
                        "event_store",
                        "agent_handlers",
                        "health_handlers",
                        "data_router",
                        "consistency_manager",
                    ],
                    "timestamp": asyncio.get_event_loop().time(),
                },
            )

            # 等待关闭信号
            await self._shutdown_event.wait()

        except Exception as e:
            logger.error("消息总线服务启动失败", error=str(e))
            raise

    async def stop(self) -> None:
        """停止消息总线服务"""
        try:
            logger.info("正在停止消息总线服务...", service=self.service_name)
            self.running = False

            # 发布服务停止事件
            if self.event_bus:
                await self.event_bus.publish(
                    "system.service.stopped",
                    {
                        "service_name": self.service_name,
                        "timestamp": asyncio.get_event_loop().time(),
                        "stats": self.event_bus.get_stats(),
                    },
                )

            # 停止所有组件
            if self.event_bus:
                await self.event_bus.stop()

            if self.event_store:
                await self.event_store.close()

            self._shutdown_event.set()

            logger.info("消息总线服务已停止", service=self.service_name)

        except Exception as e:
            logger.error("停止消息总线服务失败", error=str(e))

    def handle_shutdown(self, signum: int, frame: Any) -> None:
        """处理关闭信号"""
        logger.info("收到关闭信号", signal=signum, service=self.service_name)
        asyncio.create_task(self.stop())

    async def _health_check_loop(self) -> None:
        """健康检查循环"""
        while self.running:
            try:
                # 检查事件总线状态
                if self.event_bus:
                    stats = self.event_bus.get_stats()

                    # 发布健康检查事件
                    await self.event_bus.publish(
                        "system.service.health_check",
                        {
                            "service_name": self.service_name,
                            "status": "healthy",
                            "stats": stats,
                            "timestamp": asyncio.get_event_loop().time(),
                        },
                    )

                # 每30秒检查一次
                await asyncio.sleep(30)

            except Exception as e:
                logger.error("健康检查失败", error=str(e))
                await asyncio.sleep(30)

    async def _statistics_loop(self) -> None:
        """统计信息循环"""
        while self.running:
            try:
                if self.event_store:
                    # 获取事件统计
                    stats = await self.event_store.get_event_statistics()

                    logger.info(
                        "事件统计",
                        total_events=stats.get("total_events", 0),
                        recent_24h=stats.get("recent_24h_events", 0),
                    )

                # 每5分钟统计一次
                await asyncio.sleep(300)

            except Exception as e:
                logger.error("统计信息收集失败", error=str(e))
                await asyncio.sleep(300)

    async def _cleanup_loop(self) -> None:
        """数据清理循环"""
        while self.running:
            try:
                if self.event_store:
                    # 清理90天前的事件
                    deleted_count = await self.event_store.cleanup_old_events(days=90)

                    if deleted_count > 0:
                        logger.info("事件清理完成", deleted_count=deleted_count)

                # 每天清理一次
                await asyncio.sleep(86400)

            except Exception as e:
                logger.error("数据清理失败", error=str(e))
                await asyncio.sleep(86400)

    async def get_service_status(self) -> dict:
        """获取服务状态"""
        status = {
            "service_name": self.service_name,
            "running": self.running,
            "components": {},
        }

        if self.event_bus:
            status["components"]["event_bus"] = self.event_bus.get_stats()

        if self.agent_handlers:
            status["components"][
                "agent_handlers"
            ] = await self.agent_handlers.get_agent_status()

        if self.event_store:
            status["components"][
                "event_store"
            ] = await self.event_store.get_event_statistics()

        return status

    # API接口方法
    async def start_diagnosis(self, user_id: str, user_data: dict) -> str:
        """启动诊断流程"""
        if not self.collaboration_orchestrator:
            raise RuntimeError("协同编排器未初始化")

        return await self.collaboration_orchestrator.start_collaborative_diagnosis(
            user_id, user_data
        )

    async def get_user_health_data(
        self, user_id: str, data_type: str, **kwargs
    ) -> dict:
        """获取用户健康数据"""
        if not self.data_router:
            raise RuntimeError("数据路由器未初始化")

        return await self.data_router.get_user_health_data(user_id, data_type, **kwargs)

    async def update_user_health_data(
        self, user_id: str, data_type: str, data: dict
    ) -> bool:
        """更新用户健康数据"""
        if not self.data_router:
            raise RuntimeError("数据路由器未初始化")

        return await self.data_router.update_user_health_data(user_id, data_type, data)


async def main() -> None:
    """主函数"""
    service = SuokeMessageBusService()

    # 注册信号处理器
    signal.signal(signal.SIGINT, service.handle_shutdown)
    signal.signal(signal.SIGTERM, service.handle_shutdown)

    try:
        await service.start()
    except Exception as e:
        logger.error("服务启动失败", error=str(e))
        sys.exit(1)
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
