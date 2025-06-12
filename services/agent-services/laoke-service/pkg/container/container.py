"""
container - 索克生活项目模块
"""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any, TypeVar

from internal.repository.knowledge_repository import KnowledgeRepository
from pkg.utils.config import Config
from pkg.utils.logger import setup_logger
from pkg.utils.metrics import MetricsCollector

"""
依赖注入容器
管理服务的所有依赖组件
"""


T = TypeVar("T")


@dataclass
class ServiceConfig:
    """服务配置"""

    name: str
    version: str
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8080
    grpc_port: int = 50051
    metrics_port: int = 9091


class Container:
    """依赖注入容器"""

    def __init__(self) -> None:
        """初始化依赖注入容器"""
        self._services: dict[str, Any] = {}
        self._factories: dict[str, Callable] = {}
        self._singletons: dict[str, Any] = {}
        self._logger = logging.getLogger(__name__)
        self._initialized = False

    def register_singleton(self, name: str, instance: Any) -> None:
        """注册单例服务"""
        self._singletons[name] = instance
        self._logger.debug(f"注册单例服务: {name}")

    def register_factory(self, name: str, factory: Callable) -> None:
        """注册工厂方法"""
        self._factories[name] = factory
        self._logger.debug(f"注册工厂方法: {name}")

    def get(self, name: str) -> Any:
        """获取服务实例"""
        # 首先检查单例
        if name in self._singletons:
            return self._singletons[name]

        # 然后检查已创建的服务
        if name in self._services:
            return self._services[name]

        # 最后使用工厂创建
        if name in self._factories:
            instance = self._factories[name]()
            self._services[name] = instance
            return instance

        raise ValueError(f"服务未注册: {name}")

    def get_typed(self, service_type: type[T]) -> T:
        """获取指定类型的服务"""
        name = service_type.__name__.lower()
        return self.get(name)

    async def initialize(self) -> None:
        """初始化容器和所有服务"""
        if self._initialized:
            return

        try:
            # 1. 初始化配置
            config = Config()
            self.register_singleton("config", config)

            # 2. 初始化日志
            logger = logging.getLogger("laoke-service")
            setup_logger(logger, level=config.get("logging.level", "INFO"))
            self.register_singleton("logger", logger)

            # 3. 初始化指标收集器
            metrics = MetricsCollector()
            self.register_singleton("metrics", metrics)

            # 4. 初始化服务配置
            service_config = ServiceConfig(
                name=config.get("service.name", "laoke-service"),
                version=config.get("service.version", "0.1.0"),
                debug=config.get("server.debug", False),
                host=config.get("server.host", "0.0.0.0"),
                port=config.get("server.port", 8080),
                grpc_port=config.get("server.grpc_port", 50051),
                metrics_port=config.get("server.metrics_port", 9091),
            )
            self.register_singleton("service_config", service_config)

            # 5. 注册存储库工厂
            self.register_factory(
                "knowledge_repository", self._create_knowledge_repository
            )

            # 6. 初始化存储库索引
            await self._initialize_repositories()

            self._initialized = True
            logger.info("依赖注入容器初始化完成")

        except Exception as e:
            self._logger.error(f"容器初始化失败: {str(e)}")
            raise

    def _create_knowledge_repository(self) -> KnowledgeRepository:
        """创建知识存储库"""
        return KnowledgeRepository()

    async def _initialize_repositories(self) -> None:
        """初始化存储库索引"""
        try:
            # 初始化知识存储库
            knowledge_repo = self.get("knowledge_repository")
            if hasattr(knowledge_repo, "init_indexes"):
                await knowledge_repo.init_indexes()

            self._logger.info("所有存储库索引初始化完成")
        except Exception as e:
            self._logger.error(f"存储库索引初始化失败: {str(e)}")
            raise

    async def cleanup(self) -> None:
        """清理资源"""
        try:
            # 清理存储库连接
            cleanup_tasks = []
            for repo_name in ["knowledge_repository"]:
                if repo_name in self._services:
                    repo = self._services[repo_name]
                    if hasattr(repo, "close"):
                        cleanup_tasks.append(repo.close())

            if cleanup_tasks:
                await asyncio.gather(*cleanup_tasks, return_exceptions=True)

            self._logger.info("容器资源清理完成")
        except Exception as e:
            self._logger.error(f"容器清理失败: {str(e)}")


# 全局容器实例
_container: Container | None = None


def get_container() -> Container:
    """获取全局容器实例"""
    global _container
    if _container is None:
        _container = Container()
    return _container


async def initialize_container() -> Container:
    """初始化全局容器"""
    container = get_container()
    await container.initialize()
    return container


async def cleanup_container() -> None:
    """清理全局容器"""
    global _container
    if _container:
        await _container.cleanup()
        _container = None
