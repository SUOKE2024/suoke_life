"""
依赖注入容器
管理应用程序的所有依赖项和服务实例
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from neo4j import AsyncGraphDatabase
import redis.asyncio as redis

from app.core.config import get_settings
from app.core.logger import get_logger
from app.repositories.neo4j_repository import Neo4jRepository
from app.services.cache_service import CacheService
from app.services.knowledge_service import KnowledgeService
from app.services.metrics_service import MetricsService


class Container:
    """依赖注入容器"""

    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger()
        self._instances: dict[str, Any] = {}
        self._initialized = False

    async def initialize(self):
        """初始化所有服务"""
        if self._initialized:
            return

        try:
            # 初始化数据库连接
            await self._init_database()

            # 初始化缓存服务
            await self._init_cache()

            # 初始化监控服务
            await self._init_metrics()

            # 初始化业务服务
            await self._init_services()

            self._initialized = True
            self.logger.info("依赖注入容器初始化完成")

        except Exception as e:
            self.logger.error(f"依赖注入容器初始化失败: {e}")
            raise

    async def cleanup(self):
        """清理所有资源"""
        if not self._initialized:
            return

        try:
            # 关闭缓存连接
            if "cache_service" in self._instances:
                await self._instances["cache_service"].close()

            # 关闭数据库连接
            if "neo4j_repository" in self._instances:
                await self._instances["neo4j_repository"].close()

            self._instances.clear()
            self._initialized = False
            self.logger.info("依赖注入容器清理完成")

        except Exception as e:
            self.logger.error(f"依赖注入容器清理失败: {e}")

    async def _init_database(self):
        """初始化数据库连接"""
        db_settings = self.settings.database

        # 创建Neo4j驱动
        driver = AsyncGraphDatabase.driver(
            db_settings.uri,
            auth=(db_settings.username, db_settings.password),
            max_connection_pool_size=db_settings.max_connections,
            connection_timeout=db_settings.connection_timeout,
        )

        # 创建仓库实例
        repository = Neo4jRepository(driver)
        await repository.verify_connectivity()

        self._instances["neo4j_driver"] = driver
        self._instances["neo4j_repository"] = repository

    async def _init_cache(self):
        """初始化缓存服务"""
        if not self.settings.cache or not self.settings.cache.redis.enabled:
            self.logger.info("缓存服务未启用")
            return

        redis_settings = self.settings.cache.redis

        # 创建Redis连接
        redis_client = redis.from_url(
            f"redis://{redis_settings.host}:{redis_settings.port}",
            password=redis_settings.password or None,
            db=redis_settings.db,
            encoding="utf-8",
            decode_responses=True,
        )

        # 测试连接
        await redis_client.ping()

        # 创建缓存服务
        cache_service = CacheService(redis_client, redis_settings.ttl)

        self._instances["redis_client"] = redis_client
        self._instances["cache_service"] = cache_service

    async def _init_metrics(self):
        """初始化监控服务"""
        if not self.settings.metrics or not self.settings.metrics.enabled:
            self.logger.info("监控服务未启用")
            return

        metrics_service = MetricsService()
        self._instances["metrics_service"] = metrics_service

    async def _init_services(self):
        """初始化业务服务"""
        repository = self._instances["neo4j_repository"]
        cache_service = self._instances.get("cache_service")
        metrics_service = self._instances.get("metrics_service")

        # 创建知识服务
        knowledge_service = KnowledgeService(
            repository=repository, cache_service=cache_service, metrics_service=metrics_service
        )

        self._instances["knowledge_service"] = knowledge_service

    def get(self, name: str) -> Any:
        """获取服务实例"""
        if not self._initialized:
            raise RuntimeError("容器尚未初始化")

        if name not in self._instances:
            raise KeyError(f"服务 '{name}' 未找到")

        return self._instances[name]

    @property
    def neo4j_repository(self) -> Neo4jRepository:
        """获取Neo4j仓库"""
        return self.get("neo4j_repository")

    @property
    def knowledge_service(self) -> KnowledgeService:
        """获取知识服务"""
        return self.get("knowledge_service")

    @property
    def cache_service(self) -> CacheService | None:
        """获取缓存服务"""
        return self._instances.get("cache_service")

    @property
    def metrics_service(self) -> MetricsService | None:
        """获取监控服务"""
        return self._instances.get("metrics_service")


# 全局容器实例
_container: Container | None = None


def get_container() -> Container:
    """获取全局容器实例"""
    global _container
    if _container is None:
        _container = Container()
    return _container


@asynccontextmanager
async def lifespan_context() -> AsyncGenerator[Container]:
    """应用生命周期上下文管理器"""
    container = get_container()
    try:
        await container.initialize()
        yield container
    finally:
        await container.cleanup()
