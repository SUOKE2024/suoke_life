"""
数据库连接管理器
支持PostgreSQL、Redis和MongoDB的统一连接管理
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
import asyncpg
import aioredis
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData

logger = logging.getLogger(__name__)

# SQLAlchemy基类
Base = declarative_base()
metadata = MetaData()

class DatabaseManager:
    """数据库连接管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # PostgreSQL
        self.pg_engine = None
        self.pg_session_factory = None
        
        # Redis
        self.redis_pool = None
        
        # MongoDB
        self.mongo_client = None
        self.mongo_db = None
        
        # 连接状态
        self.is_connected = False
        
    async def initialize(self):
        """初始化所有数据库连接"""
        try:
            await self._init_postgresql()
            await self._init_redis()
            await self._init_mongodb()
            
            self.is_connected = True
            logger.info("数据库连接管理器初始化完成")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    async def _init_postgresql(self):
        """初始化PostgreSQL连接"""
        try:
            pg_config = self.config.get("postgres", {})
            
            # 构建连接URL
            db_url = (
                f"postgresql+asyncpg://"
                f"{pg_config.get('username', 'postgres')}:"
                f"{pg_config.get('password', 'password')}@"
                f"{pg_config.get('host', 'localhost')}:"
                f"{pg_config.get('port', 5432)}/"
                f"{pg_config.get('database', 'medical_resources')}"
            )
            
            # 创建异步引擎
            self.pg_engine = create_async_engine(
                db_url,
                pool_size=pg_config.get("pool_size", 20),
                max_overflow=pg_config.get("max_overflow", 30),
                pool_timeout=pg_config.get("pool_timeout", 30),
                echo=False
            )
            
            # 创建会话工厂
            self.pg_session_factory = async_sessionmaker(
                self.pg_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # 测试连接
            async with self.pg_engine.begin() as conn:
                await conn.execute("SELECT 1")
            
            logger.info("PostgreSQL连接初始化成功")
            
        except Exception as e:
            logger.error(f"PostgreSQL连接初始化失败: {e}")
            raise
    
    async def _init_redis(self):
        """初始化Redis连接"""
        try:
            redis_config = self.config.get("redis", {})
            
            # 创建Redis连接池
            self.redis_pool = aioredis.ConnectionPool.from_url(
                f"redis://{redis_config.get('host', 'localhost')}:"
                f"{redis_config.get('port', 6379)}/"
                f"{redis_config.get('database', 0)}",
                password=redis_config.get('password'),
                max_connections=redis_config.get('max_connections', 20),
                retry_on_timeout=True
            )
            
            # 测试连接
            redis = aioredis.Redis(connection_pool=self.redis_pool)
            await redis.ping()
            await redis.close()
            
            logger.info("Redis连接初始化成功")
            
        except Exception as e:
            logger.error(f"Redis连接初始化失败: {e}")
            raise
    
    async def _init_mongodb(self):
        """初始化MongoDB连接"""
        try:
            mongo_config = self.config.get("mongodb", {})
            
            # 构建连接URL
            if mongo_config.get('username') and mongo_config.get('password'):
                mongo_url = (
                    f"mongodb://"
                    f"{mongo_config.get('username')}:"
                    f"{mongo_config.get('password')}@"
                    f"{mongo_config.get('host', 'localhost')}:"
                    f"{mongo_config.get('port', 27017)}/"
                    f"{mongo_config.get('database', 'medical_analytics')}"
                )
            else:
                mongo_url = (
                    f"mongodb://"
                    f"{mongo_config.get('host', 'localhost')}:"
                    f"{mongo_config.get('port', 27017)}/"
                )
            
            # 创建MongoDB客户端
            self.mongo_client = AsyncIOMotorClient(mongo_url)
            self.mongo_db = self.mongo_client[mongo_config.get('database', 'medical_analytics')]
            
            # 测试连接
            await self.mongo_client.admin.command('ping')
            
            logger.info("MongoDB连接初始化成功")
            
        except Exception as e:
            logger.error(f"MongoDB连接初始化失败: {e}")
            raise
    
    @asynccontextmanager
    async def get_pg_session(self):
        """获取PostgreSQL会话"""
        if not self.pg_session_factory:
            raise RuntimeError("PostgreSQL未初始化")
        
        async with self.pg_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @asynccontextmanager
    async def get_redis(self):
        """获取Redis连接"""
        if not self.redis_pool:
            raise RuntimeError("Redis未初始化")
        
        redis = aioredis.Redis(connection_pool=self.redis_pool)
        try:
            yield redis
        finally:
            await redis.close()
    
    def get_mongo_db(self):
        """获取MongoDB数据库"""
        if not self.mongo_db:
            raise RuntimeError("MongoDB未初始化")
        return self.mongo_db
    
    async def health_check(self) -> Dict[str, bool]:
        """健康检查"""
        health_status = {
            "postgresql": False,
            "redis": False,
            "mongodb": False
        }
        
        # 检查PostgreSQL
        try:
            async with self.get_pg_session() as session:
                await session.execute("SELECT 1")
            health_status["postgresql"] = True
        except Exception as e:
            logger.error(f"PostgreSQL健康检查失败: {e}")
        
        # 检查Redis
        try:
            async with self.get_redis() as redis:
                await redis.ping()
            health_status["redis"] = True
        except Exception as e:
            logger.error(f"Redis健康检查失败: {e}")
        
        # 检查MongoDB
        try:
            await self.mongo_client.admin.command('ping')
            health_status["mongodb"] = True
        except Exception as e:
            logger.error(f"MongoDB健康检查失败: {e}")
        
        return health_status
    
    async def close(self):
        """关闭所有连接"""
        try:
            # 关闭PostgreSQL
            if self.pg_engine:
                await self.pg_engine.dispose()
            
            # 关闭Redis
            if self.redis_pool:
                await self.redis_pool.disconnect()
            
            # 关闭MongoDB
            if self.mongo_client:
                self.mongo_client.close()
            
            self.is_connected = False
            logger.info("数据库连接已关闭")
            
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {e}")


# 全局数据库管理器实例
db_manager: Optional[DatabaseManager] = None

async def init_database(config: Dict[str, Any]) -> DatabaseManager:
    """初始化数据库管理器"""
    global db_manager
    db_manager = DatabaseManager(config)
    await db_manager.initialize()
    return db_manager

def get_database_manager() -> DatabaseManager:
    """获取数据库管理器实例"""
    if not db_manager:
        raise RuntimeError("数据库管理器未初始化")
    return db_manager 