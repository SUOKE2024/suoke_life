"""数据库管理服务

管理PostgreSQL、MongoDB、Redis等数据库连接，提供统一的数据库访问接口。
"""

from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from xiaoke_service.core.config import settings
from xiaoke_service.core.exceptions import DatabaseError
from xiaoke_service.core.logging import get_logger
import redis.asyncio as redis
from typing import Optional, AsyncGenerator
import asyncio

logger = get_logger(__name__)


class DatabaseManager:
    """数据库管理器
    
    统一管理所有数据库连接，包括PostgreSQL、MongoDB和Redis。
    提供连接池管理、健康检查和事务支持。
    """

    def __init__(self) -> None:
        """初始化数据库管理器"""
        self.postgres_engine: Optional[AsyncEngine] = None
        self.postgres_session_factory: Optional[sessionmaker] = None
        self.mongodb_client: Optional[AsyncIOMotorClient] = None
        self.mongodb_db: Optional[AsyncIOMotorDatabase] = None
        self.redis_client: Optional[redis.Redis] = None
        self._initialized = False

    async def initialize(self) -> None:
        """初始化所有数据库连接

        采用优雅降级策略，即使某些数据库不可用也能继续运行。
        只有当所有数据库都不可用时才会抛出异常。

        Raises:
            DatabaseError: 当所有数据库连接都失败时抛出
        """
        if self._initialized:
            logger.warning("数据库已经初始化")
            return

        # 并行初始化所有数据库连接，允许部分失败
        results = await asyncio.gather(
            self._init_postgres(),
            self._init_mongodb(),
            self._init_redis(),
            return_exceptions=True
        )

        # 检查初始化结果
        postgres_ok = not isinstance(results[0], Exception)
        mongodb_ok = not isinstance(results[1], Exception)
        redis_ok = not isinstance(results[2], Exception)

        # 记录初始化状态
        success_count = sum([postgres_ok, mongodb_ok, redis_ok])
        total_count = 3

        if success_count == 0:
            logger.error("所有数据库连接初始化失败")
            raise DatabaseError("所有数据库连接初始化失败")
        elif success_count < total_count:
            logger.warning(
                f"部分数据库连接初始化失败 ({success_count}/{total_count})",
                postgres=postgres_ok,
                mongodb=mongodb_ok,
                redis=redis_ok
            )
        else:
            logger.info("所有数据库连接初始化成功")

        self._initialized = True

    async def _init_postgres(self) -> None:
        """初始化PostgreSQL连接
        
        配置连接池、事务管理和性能优化参数。
        """
        try:
            # 创建异步引擎
            self.postgres_engine = create_async_engine(
                settings.database.postgres_url,
                echo=settings.service.debug,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,  # 1小时回收连接
                connect_args={
                    "server_settings": {
                        "application_name": "xiaoke-service",
                        "jit": "off",  # 禁用JIT以提高启动速度
                    }
                },
            )

            # 创建会话工厂
            self.postgres_session_factory = sessionmaker(
                self.postgres_engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            # 测试连接
            async with self.postgres_engine.begin() as conn:
                result = await conn.execute("SELECT version()")
                version = result.scalar()
                logger.info("PostgreSQL连接建立成功", version=version)

        except Exception as e:
            logger.error("PostgreSQL初始化失败", error=str(e))
            raise

    async def _init_mongodb(self) -> None:
        """初始化MongoDB连接
        
        配置连接池、读写分离和索引优化。
        """
        try:
            # 创建MongoDB客户端
            self.mongodb_client = AsyncIOMotorClient(
                settings.database.mongodb_url,
                maxPoolSize=50,
                minPoolSize=5,
                maxIdleTimeMS=30000,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=20000,
            )
            
            # 获取数据库实例
            self.mongodb_db = self.mongodb_client[settings.database.mongodb_db]

            # 测试连接
            server_info = await self.mongodb_client.server_info()
            logger.info(
                "MongoDB连接建立成功",
                version=server_info.get("version"),
                database=settings.database.mongodb_db
            )

        except Exception as e:
            logger.error("MongoDB初始化失败", error=str(e))
            raise

    async def _init_redis(self) -> None:
        """初始化Redis连接
        
        配置连接池、超时设置和重连策略。
        """
        try:
            # 创建Redis客户端
            self.redis_client = redis.from_url(
                settings.database.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=10,
                health_check_interval=30,
            )

            # 测试连接
            pong = await self.redis_client.ping()
            redis_info = await self.redis_client.info("server")
            logger.info(
                "Redis连接建立成功",
                ping=pong,
                version=redis_info.get("redis_version")
            )

        except Exception as e:
            logger.error("Redis初始化失败", error=str(e))
            raise

    @asynccontextmanager
    async def get_postgres_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取PostgreSQL会话上下文管理器
        
        Yields:
            AsyncSession: PostgreSQL异步会话
            
        Raises:
            DatabaseError: 当PostgreSQL未初始化时抛出
        """
        if not self.postgres_session_factory:
            raise DatabaseError("PostgreSQL未初始化")
            
        session = self.postgres_session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    def get_mongodb_db(self) -> AsyncIOMotorDatabase:
        """获取MongoDB数据库实例
        
        Returns:
            AsyncIOMotorDatabase: MongoDB数据库实例
            
        Raises:
            DatabaseError: 当MongoDB未初始化时抛出
        """
        if not self.mongodb_db:
            raise DatabaseError("MongoDB未初始化")
        return self.mongodb_db

    def get_redis_client(self) -> redis.Redis:
        """获取Redis客户端
        
        Returns:
            redis.Redis: Redis客户端实例
            
        Raises:
            DatabaseError: 当Redis未初始化时抛出
        """
        if not self.redis_client:
            raise DatabaseError("Redis未初始化")
        return self.redis_client

    async def health_check(self) -> dict[str, bool]:
        """数据库健康检查
        
        Returns:
            dict: 各数据库的健康状态
        """
        health_status = {
            "postgres": False,
            "mongodb": False,
            "redis": False,
        }

        # 检查PostgreSQL
        try:
            if self.postgres_engine:
                async with self.postgres_engine.begin() as conn:
                    await conn.execute("SELECT 1")
                health_status["postgres"] = True
        except Exception as e:
            logger.warning("PostgreSQL健康检查失败", error=str(e))

        # 检查MongoDB
        try:
            if self.mongodb_client:
                await self.mongodb_client.admin.command("ping")
                health_status["mongodb"] = True
        except Exception as e:
            logger.warning("MongoDB健康检查失败", error=str(e))

        # 检查Redis
        try:
            if self.redis_client:
                await self.redis_client.ping()
                health_status["redis"] = True
        except Exception as e:
            logger.warning("Redis健康检查失败", error=str(e))

        return health_status

    async def close(self) -> None:
        """关闭所有数据库连接
        
        优雅地关闭所有数据库连接，确保资源正确释放。
        """
        close_tasks = []
        
        # PostgreSQL
        if self.postgres_engine:
            close_tasks.append(self._close_postgres())
            
        # MongoDB
        if self.mongodb_client:
            close_tasks.append(self._close_mongodb())
            
        # Redis
        if self.redis_client:
            close_tasks.append(self._close_redis())

        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)
            
        self._initialized = False
        logger.info("所有数据库连接已关闭")

    async def _close_postgres(self) -> None:
        """关闭PostgreSQL连接"""
        try:
            if self.postgres_engine:
                await self.postgres_engine.dispose()
                self.postgres_engine = None
                self.postgres_session_factory = None
                logger.info("PostgreSQL连接已关闭")
        except Exception as e:
            logger.error("PostgreSQL关闭错误", error=str(e))

    async def _close_mongodb(self) -> None:
        """关闭MongoDB连接"""
        try:
            if self.mongodb_client:
                self.mongodb_client.close()
                self.mongodb_client = None
                self.mongodb_db = None
                logger.info("MongoDB连接已关闭")
        except Exception as e:
            logger.error("MongoDB关闭错误", error=str(e))

    async def _close_redis(self) -> None:
        """关闭Redis连接"""
        try:
            if self.redis_client:
                await self.redis_client.close()
                self.redis_client = None
                logger.info("Redis连接已关闭")
        except Exception as e:
            logger.error("Redis关闭错误", error=str(e))