"""
async_optimization - 索克生活项目模块
"""

from collections.abc import Callable, Coroutine
from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import wraps
from typing import Any, TypeVar
import aioredis
import asyncio
import asyncpg
import logging

#! / usr / bin / env python3
"""
异步处理优化模块
提供批量处理、连接池管理等异步优化功能
"""



logger = logging.getLogger(__name__)

T = TypeVar("T")

class AsyncBatcher:
    """批量处理异步请求，减少 I / O 开销"""

    def __init__(
        self,
        batch_processor: Callable[[list[Any]], Coroutine[Any, Any, list[Any]]],
        batch_size: int = 100,
        timeout: float = 0.1,
    ):
        self.batch_processor = batch_processor
        self.batch_size = batch_size
        self.timeout = timeout
        self.pending_items: list[tuple] = []
        self._lock = asyncio.Lock()
        self._process_task: asyncio.Task | None = None
        self._stopped = False

        # 统计信息
        self.stats = {
            "total_batches": 0,
            "total_items": 0,
            "average_batch_size": 0,
            "processing_errors": 0,
        }

    async def start(self) -> None:
        """启动批处理器"""
        if not self._process_task:
            self._stopped = False
            self._process_task = asyncio.create_task(self._process_loop())
            logger.info("异步批处理器已启动")

    async def stop(self) -> None:
        """停止批处理器"""
        self._stopped = True
        if self._process_task:
            await self._process_task
            self._process_task = None

        # 处理剩余的项目
        if self.pending_items:
            await self._process_batch()

        logger.info("异步批处理器已停止")

    async def add_item(self, item: Any) -> Any:
        """添加项目到批处理队列"""
        future = asyncio.Future()

        async with self._lock:
            self.pending_items.append((item, future))

            if len(self.pending_items)>=self.batch_size:
                # 立即处理满批次
                await self._process_batch()

        # 等待结果
        return await future

    async def _process_loop(self) -> None:
        """处理循环"""
        while not self._stopped:
            try:
                await asyncio.sleep(self.timeout)

                async with self._lock:
                    if self.pending_items:
                        await self._process_batch()

            except Exception as e:
                logger.error(f"批处理循环错误: {e}")
                self.stats["processing_errors"]+=1

    async def _process_batch(self) -> None:
        """处理批次"""
        if not self.pending_items:
            return

        # 取出一批项目
        batch_items = self.pending_items[: self.batch_size]
        self.pending_items = self.pending_items[self.batch_size :]

        # 提取项目和future
        items = [item for item, _ in batch_items]
        futures = [future for _, future in batch_items]

        try:
            # 批量处理
            results = await self.batch_processor(items)

            # 设置结果
            for future, result in zip(futures, results, strict = False):
                if not future.done():
                    future.set_result(result)

            # 更新统计
            self.stats["total_batches"]+=1
            self.stats["total_items"]+=len(batch_items)
            self.stats["average_batch_size"] = (
                self.stats["total_items"] / self.stats["total_batches"]
            )

        except Exception as e:
            # 设置异常
            for future in futures:
                if not future.done():
                    future.set_exception(e)

            self.stats["processing_errors"]+=1
            logger.error(f"批处理失败: {e}")

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        return {
           ***self.stats,
            "pending_items": len(self.pending_items),
            "is_running": self._process_task is not None,
        }

@dataclass
class ConnectionPoolConfig:
    """连接池配置"""

    min_size: int = 5
    max_size: int = 20
    timeout: float = 5.0
    max_queries: int = 50000
    max_inactive_connection_lifetime: float = 300.0

class ConnectionPoolManager:
    """统一管理各种连接池"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.redis_pool: aioredis.Redis | None = None
        self.pg_pool: asyncpg.Pool | None = None
        self.mysql_pool = None
        self.mongo_client: motor.motor_asyncio.AsyncIOMotorClient | None = None
        self.initialized = False
        self._pools_config: dict[str, ConnectionPoolConfig] = {}

        # 连接池统计
        self.stats = {
            "redis": {"acquired": 0, "released": 0, "errors": 0},
            "postgres": {"acquired": 0, "released": 0, "errors": 0},
            "mysql": {"acquired": 0, "released": 0, "errors": 0},
            "mongodb": {"acquired": 0, "released": 0, "errors": 0},
        }

    async def initialize(self, config: dict[str, Any]):
        """初始化所有连接池"""
        try:
            # Redis 连接池
            if "redis" in config:
                redis_config = config["redis"]
                pool_config = ConnectionPoolConfig(***redis_config.get("pool", {}))
                self._pools_config["redis"] = pool_config

                self.redis_pool = await aioredis.create_redis_pool(
                    redis_config["url"],
                    minsize = pool_config.min_size,
                    maxsize = pool_config.max_size,
                    timeout = pool_config.timeout,
                )
                logger.info("Redis连接池初始化成功")

            # PostgreSQL 连接池
            if "postgres" in config:
                pg_config = config["postgres"]
                pool_config = ConnectionPoolConfig(***pg_config.get("pool", {}))
                self._pools_config["postgres"] = pool_config

                self.pg_pool = await asyncpg.create_pool(
                    pg_config["dsn"],
                    min_size = pool_config.min_size,
                    max_size = pool_config.max_size,
                    timeout = pool_config.timeout,
                    max_queries = pool_config.max_queries,
                    max_inactive_connection_lifetime = pool_config.max_inactive_connection_lifetime,
                )
                logger.info("PostgreSQL连接池初始化成功")

            # MySQL 连接池
            if "mysql" in config:
                mysql_config = config["mysql"]
                pool_config = ConnectionPoolConfig(***mysql_config.get("pool", {}))
                self._pools_config["mysql"] = pool_config

                self.mysql_pool = await create_mysql_pool(
                    host = mysql_config["host"],
                    port = mysql_config.get("port", 3306),
                    user = mysql_config["user"],
                    password = mysql_config["password"],
                    db = mysql_config["database"],
                    minsize = pool_config.min_size,
                    maxsize = pool_config.max_size,
                    pool_recycle = pool_config.max_inactive_connection_lifetime,
                )
                logger.info("MySQL连接池初始化成功")

            # MongoDB 连接
            if "mongodb" in config:
                mongo_config = config["mongodb"]
                self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
                    mongo_config["uri"],
                    maxPoolSize = mongo_config.get("max_pool_size", 50),
                    minPoolSize = mongo_config.get("min_pool_size", 10),
                    maxIdleTimeMS = mongo_config.get("max_idle_time_ms", 60000),
                )
                logger.info("MongoDB连接初始化成功")

            self.initialized = True
            logger.info("所有连接池初始化完成")

        except Exception as e:
            logger.error(f"连接池初始化失败: {e}")
            raise

    @asynccontextmanager
    async def get_redis(self) -> None:
        """获取 Redis 连接"""
        if not self.redis_pool:
            raise RuntimeError("Redis连接池未初始化")

        try:
            self.stats["redis"]["acquired"]+=1
            async with self.redis_pool.get() as conn:
                yield conn
        except Exception:
            self.stats["redis"]["errors"]+=1
            raise
        finally:
            self.stats["redis"]["released"]+=1

    @asynccontextmanager
    async def get_postgres(self) -> None:
        """获取 PostgreSQL 连接"""
        if not self.pg_pool:
            raise RuntimeError("PostgreSQL连接池未初始化")

        try:
            self.stats["postgres"]["acquired"]+=1
            async with self.pg_pool.acquire() as conn:
                yield conn
        except Exception:
            self.stats["postgres"]["errors"]+=1
            raise
        finally:
            self.stats["postgres"]["released"]+=1

    @asynccontextmanager
    async def get_mysql(self) -> None:
        """获取 MySQL 连接"""
        if not self.mysql_pool:
            raise RuntimeError("MySQL连接池未初始化")

        try:
            self.stats["mysql"]["acquired"]+=1
            async with self.mysql_pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    yield cursor
        except Exception:
            self.stats["mysql"]["errors"]+=1
            raise
        finally:
            self.stats["mysql"]["released"]+=1

    def get_mongodb(self) -> motor.motor_asyncio.AsyncIOMotorDatabase:
        """获取 MongoDB 数据库实例"""
        if not self.mongo_client:
            raise RuntimeError("MongoDB客户端未初始化")

        self.stats["mongodb"]["acquired"]+=1
        return self.mongo_client.get_database()

    async def close_all(self) -> None:
        """关闭所有连接池"""
        if self.redis_pool:
            self.redis_pool.close()
            await self.redis_pool.wait_closed()
            logger.info("Redis连接池已关闭")

        if self.pg_pool:
            await self.pg_pool.close()
            logger.info("PostgreSQL连接池已关闭")

        if self.mysql_pool:
            self.mysql_pool.close()
            await self.mysql_pool.wait_closed()
            logger.info("MySQL连接池已关闭")

        if self.mongo_client:
            self.mongo_client.close()
            logger.info("MongoDB连接已关闭")

        self.initialized = False

    def get_stats(self) -> dict[str, Any]:
        """获取连接池统计信息"""
        stats = dict(self.stats)

        # 添加连接池状态
        if self.pg_pool:
            stats["postgres"]["pool_size"] = self.pg_pool.get_size()
            stats["postgres"]["pool_free"] = self.pg_pool.get_idle_size()

        return stats

    async def health_check(self) -> dict[str, Any]:
        """健康检查"""
        health = {"status": "healthy", "pools": {}}

        # 检查 Redis
        if self.redis_pool:
            try:
                async with self.get_redis() as conn:
                    await conn.ping()
                health["pools"]["redis"] = "healthy"
            except Exception as e:
                health["pools"]["redis"] = f"unhealthy: {e!s}"
                health["status"] = "unhealthy"

        # 检查 PostgreSQL
        if self.pg_pool:
            try:
                async with self.get_postgres() as conn:
                    await conn.fetchval("SELECT 1")
                health["pools"]["postgres"] = "healthy"
            except Exception as e:
                health["pools"]["postgres"] = f"unhealthy: {e!s}"
                health["status"] = "unhealthy"

        # 检查 MySQL
        if self.mysql_pool:
            try:
                async with self.get_mysql() as cursor:
                    await cursor.execute("SELECT 1")
                health["pools"]["mysql"] = "healthy"
            except Exception as e:
                health["pools"]["mysql"] = f"unhealthy: {e!s}"
                health["status"] = "unhealthy"

        # 检查 MongoDB
        if self.mongo_client:
            try:
                await self.mongo_client.admin.command("ping")
                health["pools"]["mongodb"] = "healthy"
            except Exception as e:
                health["pools"]["mongodb"] = f"unhealthy: {e!s}"
                health["status"] = "unhealthy"

        return health

# 全局连接池管理器
_global_pool_manager = ConnectionPoolManager()

async def get_pool_manager() -> ConnectionPoolManager:
    """获取全局连接池管理器"""
    return _global_pool_manager

# 装饰器：自动批处理
def batch_process(batch_size: int = 100, timeout: float = 0.1):
    """
    批处理装饰器

    将多个调用自动批量处理
    被装饰的函数应该接受列表参数并返回列表结果
    """

    def decorator(func: Callable[[list[Any]], Coroutine[Any, Any, list[Any]]]):
        """TODO: 添加文档字符串"""
        # 为每个被装饰的函数创建独立的批处理器
        batcher = AsyncBatcher(func, batch_size, timeout)

        @wraps(func)
        async def wrapper(item: Any) -> Any:
            # 确保批处理器已启动
            if not batcher._process_task:
                await batcher.start()

            return await batcher.add_item(item)

        # 添加控制方法
        wrapper.start_batcher = batcher.start
        wrapper.stop_batcher = batcher.stop
        wrapper.get_batcher_stats = batcher.get_stats

        return wrapper

    return decorator
