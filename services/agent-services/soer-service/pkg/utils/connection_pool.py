"""
connection_pool - 索克生活项目模块
"""

from contextlib import asynccontextmanager
from pkg.utils.dependency_injection import ServiceLifecycle
from pkg.utils.enhanced_config import CacheConfig, DatabaseConfig
from pkg.utils.error_handling import DatabaseException, RetryConfig, retry_async
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import QueuePool
from typing import Any, AsyncContextManager
import logging

"""
连接池管理器
提供数据库、Redis等连接的统一管理和优化
"""



logger = logging.getLogger(__name__)

class DatabaseConnectionPool(ServiceLifecycle):
    """数据库连接池"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = None
        self.session_factory = None
        self._pool = None

    async def start(self) -> None:
        """启动数据库连接池"""
        try:
            # 构建数据库URL
            if self.config.type == "postgresql":
                db_url = (
                    f"postgresql+asyncpg://{self.config.user}:{self.config.password}"
                    f"@{self.config.host}:{self.config.port}/{self.config.name}"
                )
            else:
                raise ValueError(f"不支持的数据库类型: {self.config.type}")

            # 创建异步引擎
            self.engine = create_async_engine(
                db_url,
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.pool_size * 2,
                pool_timeout=self.config.timeout,
                pool_recycle=3600,  # 1小时回收连接
                pool_pre_ping=True,  # 连接前检查
                echo=False  # 生产环境关闭SQL日志
            )

            # 创建会话工厂
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            # 测试连接
            async with self.engine.begin() as conn:
                await conn.execute("SELECT 1")

            logger.info(f"数据库连接池启动成功: {self.config.host}:{self.config.port}")

        except Exception as e:
            logger.error(f"数据库连接池启动失败: {e}")
            raise DatabaseException(f"数据库连接池启动失败: {e}")

    async def stop(self) -> None:
        """停止数据库连接池"""
        if self.engine:
            await self.engine.dispose()
            logger.info("数据库连接池已关闭")

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if not self.engine:
                return False

            async with self.engine.begin() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return False

    @asynccontextmanager
    async def get_session(self) -> AsyncContextManager[AsyncSession]:
        """获取数据库会话"""
        if not self.session_factory:
            raise DatabaseException("数据库连接池未初始化")

        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    @retry_async(RetryConfig(max_attempts=3, base_delay=1.0))
    async def execute_query(self, query: str, params: dict[str, Any] = None) -> Any:
        """执行查询"""
        async with self.get_session() as session:
            result = await session.execute(query, params or {})
            await session.commit()
            return result

class RedisConnectionPool(ServiceLifecycle):
    """Redis连接池"""

    def __init__(self, config: CacheConfig):
        self.config = config
        self.pool = None
        self.redis = None

    async def start(self) -> None:
        """启动Redis连接池"""
        try:
            # 创建连接池
            self.pool = redis.ConnectionPool.from_url(
                f"redis://{self.config.host}:{self.config.port}/{self.config.db}",
                password=self.config.password,
                max_connections=20,
                retry_on_timeout=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )

            # 创建Redis客户端
            self.redis = redis.Redis(connection_pool=self.pool)

            # 测试连接
            await self.redis.ping()

            logger.info(f"Redis连接池启动成功: {self.config.host}:{self.config.port}")

        except Exception as e:
            logger.error(f"Redis连接池启动失败: {e}")
            raise DatabaseException(f"Redis连接池启动失败: {e}")

    async def stop(self) -> None:
        """停止Redis连接池"""
        if self.redis:
            await self.redis.close()
        if self.pool:
            await self.pool.disconnect()
        logger.info("Redis连接池已关闭")

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if not self.redis:
                return False

            await self.redis.ping()
            return True
        except Exception as e:
            logger.error(f"Redis健康检查失败: {e}")
            return False

    @retry_async(RetryConfig(max_attempts=3, base_delay=0.5))
    async def get(self, key: str) -> str | None:
        """获取缓存值"""
        if not self.redis:
            raise DatabaseException("Redis连接池未初始化")

        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Redis GET操作失败: {e}")
            raise

    @retry_async(RetryConfig(max_attempts=3, base_delay=0.5))
    async def set(self, key: str, value: str, ttl: int | None = None) -> bool:
        """设置缓存值"""
        if not self.redis:
            raise DatabaseException("Redis连接池未初始化")

        try:
            if ttl is None:
                ttl = self.config.ttl

            return await self.redis.set(key, value, ex=ttl)
        except Exception as e:
            logger.error(f"Redis SET操作失败: {e}")
            raise

    @retry_async(RetryConfig(max_attempts=3, base_delay=0.5))
    async def delete(self, key: str) -> int:
        """删除缓存值"""
        if not self.redis:
            raise DatabaseException("Redis连接池未初始化")

        try:
            return await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Redis DELETE操作失败: {e}")
            raise

    @retry_async(RetryConfig(max_attempts=3, base_delay=0.5))
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.redis:
            raise DatabaseException("Redis连接池未初始化")

        try:
            return bool(await self.redis.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS操作失败: {e}")
            raise

    @retry_async(RetryConfig(max_attempts=3, base_delay=0.5))
    async def hget(self, name: str, key: str) -> str | None:
        """获取哈希字段值"""
        if not self.redis:
            raise DatabaseException("Redis连接池未初始化")

        try:
            return await self.redis.hget(name, key)
        except Exception as e:
            logger.error(f"Redis HGET操作失败: {e}")
            raise

    @retry_async(RetryConfig(max_attempts=3, base_delay=0.5))
    async def hset(self, name: str, key: str, value: str) -> int:
        """设置哈希字段值"""
        if not self.redis:
            raise DatabaseException("Redis连接池未初始化")

        try:
            return await self.redis.hset(name, key, value)
        except Exception as e:
            logger.error(f"Redis HSET操作失败: {e}")
            raise

class MongoConnectionPool(ServiceLifecycle):
    """MongoDB连接池"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.client = None
        self.database = None

    async def start(self) -> None:
        """启动MongoDB连接池"""
        try:
            # 构建连接URL
            mongo_url = f"mongodb://{self.config['host']}:{self.config['port']}"

            # 创建客户端
            self.client = motor.motor_asyncio.AsyncIOMotorClient(
                mongo_url,
                maxPoolSize=self.config.get('pool_size', 10),
                minPoolSize=1,
                maxIdleTimeMS=30000,
                waitQueueTimeoutMS=5000,
                serverSelectionTimeoutMS=5000
            )

            # 获取数据库
            self.database = self.client[self.config['database']]

            # 测试连接
            await self.client.admin.command('ping')

            logger.info(f"MongoDB连接池启动成功: {self.config['host']}:{self.config['port']}")

        except Exception as e:
            logger.error(f"MongoDB连接池启动失败: {e}")
            raise DatabaseException(f"MongoDB连接池启动失败: {e}")

    async def stop(self) -> None:
        """停止MongoDB连接池"""
        if self.client:
            self.client.close()
            logger.info("MongoDB连接池已关闭")

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if not self.client:
                return False

            await self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"MongoDB健康检查失败: {e}")
            return False

        @cache(timeout=300)  # 5分钟缓存
def get_collection(self, collection_name: str):
        """获取集合"""
        if not self.database:
            raise DatabaseException("MongoDB连接池未初始化")

        return self.database[collection_name]

class ConnectionPoolManager(ServiceLifecycle):
    """连接池管理器"""

    def __init__(self):
        self.pools: dict[str, ServiceLifecycle] = {}

    def register_pool(self, name: str, pool: ServiceLifecycle) -> None:
        """注册连接池"""
        self.pools[name] = pool
        logger.debug(f"注册连接池: {name}")

    def get_pool(self, name: str) -> ServiceLifecycle:
        """获取连接池"""
        if name not in self.pools:
            raise ValueError(f"连接池未注册: {name}")
        return self.pools[name]

    async def start(self) -> None:
        """启动所有连接池"""
        logger.info("启动所有连接池...")

        for name, pool in self.pools.items():
            try:
                await pool.start()
                logger.info(f"连接池 {name} 启动成功")
            except Exception as e:
                logger.error(f"连接池 {name} 启动失败: {e}")
                raise

        logger.info("所有连接池启动完成")

    async def stop(self) -> None:
        """停止所有连接池"""
        logger.info("停止所有连接池...")

        for name, pool in reversed(list(self.pools.items())):
            try:
                await pool.stop()
                logger.info(f"连接池 {name} 停止成功")
            except Exception as e:
                logger.error(f"连接池 {name} 停止失败: {e}")

        logger.info("所有连接池停止完成")

    async def health_check(self) -> dict[str, bool]:
        """检查所有连接池健康状态"""
        results = {}

        for name, pool in self.pools.items():
            try:
                results[name] = await pool.health_check()
            except Exception as e:
                logger.error(f"连接池 {name} 健康检查失败: {e}")
                results[name] = False

        return results

# 全局连接池管理器实例
_pool_manager: ConnectionPoolManager | None = None

def get_pool_manager() -> ConnectionPoolManager:
    """获取全局连接池管理器"""
    global _pool_manager
    if _pool_manager is None:
        _pool_manager = ConnectionPoolManager()
    return _pool_manager

def setup_pool_manager(manager: ConnectionPoolManager) -> None:
    """设置全局连接池管理器"""
    global _pool_manager
    _pool_manager = manager
