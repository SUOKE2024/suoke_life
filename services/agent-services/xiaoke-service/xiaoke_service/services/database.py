"""
数据库管理服务

管理PostgreSQL、MongoDB、Redis等数据库连接。
"""

from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from xiaoke_service.core.config import settings
from xiaoke_service.core.exceptions import DatabaseError
from xiaoke_service.core.logging import get_logger

logger = get_logger(__name__)

class DatabaseManager:
    """数据库管理器"""

    def __init__(self):
        self.postgres_engine = None
        self.postgres_session_factory = None
        self.mongodb_client = None
        self.mongodb_db = None
        self.redis_client = None

    async def initialize(self) -> None:
        """初始化所有数据库连接"""
        try:
            await self._init_postgres()
            await self._init_mongodb()
            await self._init_redis()
            logger.info("Database connections initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize database connections", error=str(e))
            raise DatabaseError(f"Database initialization failed: {e}") from e

    async def _init_postgres(self) -> None:
        """初始化PostgreSQL连接"""
        try:
            self.postgres_engine = create_async_engine(
                settings.database.postgres_url,
                echo=settings.service.debug,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
            )

            self.postgres_session_factory = sessionmaker(
                self.postgres_engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            # 测试连接
            async with self.postgres_engine.begin() as conn:
                await conn.execute("SELECT 1")

            logger.info("PostgreSQL connection established")

        except Exception as e:
            logger.error("Failed to initialize PostgreSQL", error=str(e))
            raise

    async def _init_mongodb(self) -> None:
        """初始化MongoDB连接"""
        try:
            self.mongodb_client = AsyncIOMotorClient(settings.database.mongodb_url)
            self.mongodb_db = self.mongodb_client[settings.database.mongodb_db]

            # 测试连接
            await self.mongodb_client.admin.command("ping")

            logger.info("MongoDB connection established")

        except Exception as e:
            logger.error("Failed to initialize MongoDB", error=str(e))
            raise

    async def _init_redis(self) -> None:
        """初始化Redis连接"""
        try:
            self.redis_client = redis.from_url(
                settings.database.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )

            # 测试连接
            await self.redis_client.ping()

            logger.info("Redis connection established")

        except Exception as e:
            logger.error("Failed to initialize Redis", error=str(e))
            raise

    async def get_postgres_session(self) -> AsyncSession:
        """获取PostgreSQL会话"""
        if not self.postgres_session_factory:
            raise DatabaseError("PostgreSQL not initialized")
        return self.postgres_session_factory()

    def get_mongodb_db(self):
        """获取MongoDB数据库"""
        if not self.mongodb_db:
            raise DatabaseError("MongoDB not initialized")
        return self.mongodb_db

    def get_redis_client(self):
        """获取Redis客户端"""
        if not self.redis_client:
            raise DatabaseError("Redis not initialized")
        return self.redis_client

    async def close(self) -> None:
        """关闭所有数据库连接"""
        try:
            if self.postgres_engine:
                await self.postgres_engine.dispose()
                logger.info("PostgreSQL connection closed")

            if self.mongodb_client:
                self.mongodb_client.close()
                logger.info("MongoDB connection closed")

            if self.redis_client:
                await self.redis_client.close()
                logger.info("Redis connection closed")

        except Exception as e:
            logger.error("Error closing database connections", error=str(e))
