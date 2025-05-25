"""
高级数据库连接池管理模块
支持多数据库、连接池监控、故障转移等功能
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, AsyncContextManager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import time

import asyncpg
import aioredis
from motor.motor_asyncio import AsyncIOMotorClient
import structlog

logger = structlog.get_logger(__name__)


class DatabaseType(Enum):
    """数据库类型"""
    POSTGRESQL = "postgresql"
    REDIS = "redis"
    MONGODB = "mongodb"


class ConnectionStatus(Enum):
    """连接状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DISCONNECTED = "disconnected"


@dataclass
class ConnectionMetrics:
    """连接指标"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    average_response_time: float = 0.0
    last_health_check: datetime = field(default_factory=datetime.now)
    status: ConnectionStatus = ConnectionStatus.DISCONNECTED


@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str
    port: int
    database: str
    username: str
    password: str
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    health_check_interval: int = 60
    connection_timeout: int = 10


class DatabaseConnection(ABC):
    """数据库连接抽象基类"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.metrics = ConnectionMetrics()
        self.pool = None
        self.is_connected = False
        self.last_error: Optional[Exception] = None
    
    @abstractmethod
    async def connect(self) -> bool:
        """建立连接"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """断开连接"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass
    
    @abstractmethod
    async def get_connection(self) -> AsyncContextManager:
        """获取连接"""
        pass
    
    @abstractmethod
    async def execute_query(self, query: str, *args) -> Any:
        """执行查询"""
        pass


class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL连接"""
    
    async def connect(self) -> bool:
        """建立PostgreSQL连接池"""
        try:
            dsn = f"postgresql://{self.config.username}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}"
            
            self.pool = await asyncpg.create_pool(
                dsn,
                min_size=1,
                max_size=self.config.pool_size,
                command_timeout=self.config.connection_timeout,
                server_settings={
                    'application_name': 'medical_resource_service',
                    'jit': 'off'
                }
            )
            
            # 测试连接
            async with self.pool.acquire() as conn:
                await conn.execute('SELECT 1')
            
            self.is_connected = True
            self.metrics.status = ConnectionStatus.HEALTHY
            self.metrics.total_connections = self.config.pool_size
            
            logger.info(f"PostgreSQL连接池创建成功: {self.config.host}:{self.config.port}")
            return True
            
        except Exception as e:
            self.last_error = e
            self.metrics.status = ConnectionStatus.UNHEALTHY
            logger.error(f"PostgreSQL连接失败: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """断开PostgreSQL连接池"""
        try:
            if self.pool:
                await self.pool.close()
                self.pool = None
            
            self.is_connected = False
            self.metrics.status = ConnectionStatus.DISCONNECTED
            
            logger.info("PostgreSQL连接池已关闭")
            return True
            
        except Exception as e:
            self.last_error = e
            logger.error(f"PostgreSQL断开连接失败: {e}")
            return False
    
    async def health_check(self) -> bool:
        """PostgreSQL健康检查"""
        if not self.pool:
            return False
        
        try:
            start_time = time.time()
            
            async with self.pool.acquire() as conn:
                await conn.execute('SELECT 1')
            
            response_time = time.time() - start_time
            self.metrics.average_response_time = response_time
            self.metrics.last_health_check = datetime.now()
            
            # 更新连接池状态
            pool_stats = self.pool.get_stats()
            self.metrics.active_connections = pool_stats.open_connections
            self.metrics.idle_connections = pool_stats.idle_connections
            
            # 判断健康状态
            if response_time > 5.0:
                self.metrics.status = ConnectionStatus.DEGRADED
            else:
                self.metrics.status = ConnectionStatus.HEALTHY
            
            return True
            
        except Exception as e:
            self.last_error = e
            self.metrics.status = ConnectionStatus.UNHEALTHY
            self.metrics.failed_connections += 1
            logger.error(f"PostgreSQL健康检查失败: {e}")
            return False
    
    async def get_connection(self):
        """获取PostgreSQL连接"""
        if not self.pool:
            raise RuntimeError("数据库连接池未初始化")
        
        return self.pool.acquire()
    
    async def execute_query(self, query: str, *args) -> Any:
        """执行PostgreSQL查询"""
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args)


class RedisConnection(DatabaseConnection):
    """Redis连接"""
    
    async def connect(self) -> bool:
        """建立Redis连接池"""
        try:
            redis_url = f"redis://{self.config.host}:{self.config.port}/{self.config.database}"
            
            self.pool = aioredis.ConnectionPool.from_url(
                redis_url,
                max_connections=self.config.pool_size,
                retry_on_timeout=True,
                socket_timeout=self.config.connection_timeout,
                socket_connect_timeout=self.config.connection_timeout
            )
            
            # 测试连接
            redis_client = aioredis.Redis(connection_pool=self.pool)
            await redis_client.ping()
            await redis_client.close()
            
            self.is_connected = True
            self.metrics.status = ConnectionStatus.HEALTHY
            self.metrics.total_connections = self.config.pool_size
            
            logger.info(f"Redis连接池创建成功: {self.config.host}:{self.config.port}")
            return True
            
        except Exception as e:
            self.last_error = e
            self.metrics.status = ConnectionStatus.UNHEALTHY
            logger.error(f"Redis连接失败: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """断开Redis连接池"""
        try:
            if self.pool:
                await self.pool.disconnect()
                self.pool = None
            
            self.is_connected = False
            self.metrics.status = ConnectionStatus.DISCONNECTED
            
            logger.info("Redis连接池已关闭")
            return True
            
        except Exception as e:
            self.last_error = e
            logger.error(f"Redis断开连接失败: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Redis健康检查"""
        if not self.pool:
            return False
        
        try:
            start_time = time.time()
            
            redis_client = aioredis.Redis(connection_pool=self.pool)
            await redis_client.ping()
            await redis_client.close()
            
            response_time = time.time() - start_time
            self.metrics.average_response_time = response_time
            self.metrics.last_health_check = datetime.now()
            
            # 判断健康状态
            if response_time > 2.0:
                self.metrics.status = ConnectionStatus.DEGRADED
            else:
                self.metrics.status = ConnectionStatus.HEALTHY
            
            return True
            
        except Exception as e:
            self.last_error = e
            self.metrics.status = ConnectionStatus.UNHEALTHY
            self.metrics.failed_connections += 1
            logger.error(f"Redis健康检查失败: {e}")
            return False
    
    async def get_connection(self):
        """获取Redis连接"""
        if not self.pool:
            raise RuntimeError("Redis连接池未初始化")
        
        return aioredis.Redis(connection_pool=self.pool)
    
    async def execute_query(self, query: str, *args) -> Any:
        """执行Redis命令"""
        redis_client = await self.get_connection()
        try:
            # 简化实现，实际需要根据命令类型处理
            return await redis_client.execute_command(query, *args)
        finally:
            await redis_client.close()


class MongoDBConnection(DatabaseConnection):
    """MongoDB连接"""
    
    async def connect(self) -> bool:
        """建立MongoDB连接"""
        try:
            connection_string = f"mongodb://{self.config.username}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}"
            
            self.pool = AsyncIOMotorClient(
                connection_string,
                maxPoolSize=self.config.pool_size,
                minPoolSize=1,
                maxIdleTimeMS=30000,
                serverSelectionTimeoutMS=self.config.connection_timeout * 1000
            )
            
            # 测试连接
            await self.pool.admin.command('ping')
            
            self.is_connected = True
            self.metrics.status = ConnectionStatus.HEALTHY
            self.metrics.total_connections = self.config.pool_size
            
            logger.info(f"MongoDB连接创建成功: {self.config.host}:{self.config.port}")
            return True
            
        except Exception as e:
            self.last_error = e
            self.metrics.status = ConnectionStatus.UNHEALTHY
            logger.error(f"MongoDB连接失败: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """断开MongoDB连接"""
        try:
            if self.pool:
                self.pool.close()
                self.pool = None
            
            self.is_connected = False
            self.metrics.status = ConnectionStatus.DISCONNECTED
            
            logger.info("MongoDB连接已关闭")
            return True
            
        except Exception as e:
            self.last_error = e
            logger.error(f"MongoDB断开连接失败: {e}")
            return False
    
    async def health_check(self) -> bool:
        """MongoDB健康检查"""
        if not self.pool:
            return False
        
        try:
            start_time = time.time()
            
            await self.pool.admin.command('ping')
            
            response_time = time.time() - start_time
            self.metrics.average_response_time = response_time
            self.metrics.last_health_check = datetime.now()
            
            # 判断健康状态
            if response_time > 3.0:
                self.metrics.status = ConnectionStatus.DEGRADED
            else:
                self.metrics.status = ConnectionStatus.HEALTHY
            
            return True
            
        except Exception as e:
            self.last_error = e
            self.metrics.status = ConnectionStatus.UNHEALTHY
            self.metrics.failed_connections += 1
            logger.error(f"MongoDB健康检查失败: {e}")
            return False
    
    async def get_connection(self):
        """获取MongoDB数据库实例"""
        if not self.pool:
            raise RuntimeError("MongoDB连接未初始化")
        
        return self.pool[self.config.database]
    
    async def execute_query(self, collection: str, operation: str, *args, **kwargs) -> Any:
        """执行MongoDB操作"""
        db = await self.get_connection()
        collection_obj = db[collection]
        
        # 根据操作类型执行相应方法
        if hasattr(collection_obj, operation):
            method = getattr(collection_obj, operation)
            return await method(*args, **kwargs)
        else:
            raise ValueError(f"不支持的MongoDB操作: {operation}")


class DatabasePoolManager:
    """数据库连接池管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connections: Dict[str, DatabaseConnection] = {}
        self.health_check_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        logger.info("数据库连接池管理器初始化完成")
    
    async def initialize(self):
        """初始化所有数据库连接"""
        database_configs = self.config.get("databases", {})
        
        for db_name, db_config in database_configs.items():
            await self._create_connection(db_name, db_config)
        
        # 启动健康检查
        await self._start_health_check()
        
        logger.info("数据库连接池管理器初始化完成")
    
    async def _create_connection(self, name: str, config: Dict[str, Any]):
        """创建数据库连接"""
        try:
            db_config = DatabaseConfig(**config)
            db_type = DatabaseType(config.get("type", "postgresql"))
            
            # 根据数据库类型创建连接
            if db_type == DatabaseType.POSTGRESQL:
                connection = PostgreSQLConnection(db_config)
            elif db_type == DatabaseType.REDIS:
                connection = RedisConnection(db_config)
            elif db_type == DatabaseType.MONGODB:
                connection = MongoDBConnection(db_config)
            else:
                raise ValueError(f"不支持的数据库类型: {db_type}")
            
            # 建立连接
            success = await connection.connect()
            if success:
                self.connections[name] = connection
                logger.info(f"数据库连接 {name} 创建成功")
            else:
                logger.error(f"数据库连接 {name} 创建失败")
                
        except Exception as e:
            logger.error(f"创建数据库连接 {name} 失败: {e}")
    
    async def get_connection(self, name: str) -> DatabaseConnection:
        """获取数据库连接"""
        if name not in self.connections:
            raise ValueError(f"数据库连接 {name} 不存在")
        
        connection = self.connections[name]
        if not connection.is_connected:
            # 尝试重新连接
            await connection.connect()
        
        return connection
    
    async def _start_health_check(self):
        """启动健康检查任务"""
        self.is_running = True
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("数据库健康检查任务已启动")
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while self.is_running:
            try:
                for name, connection in self.connections.items():
                    await connection.health_check()
                
                # 等待下一次检查
                await asyncio.sleep(60)  # 每分钟检查一次
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"健康检查失败: {e}")
                await asyncio.sleep(60)
    
    async def get_metrics(self) -> Dict[str, ConnectionMetrics]:
        """获取所有连接的指标"""
        return {
            name: connection.metrics
            for name, connection in self.connections.items()
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        status = {}
        
        for name, connection in self.connections.items():
            status[name] = {
                "status": connection.metrics.status.value,
                "is_connected": connection.is_connected,
                "total_connections": connection.metrics.total_connections,
                "active_connections": connection.metrics.active_connections,
                "idle_connections": connection.metrics.idle_connections,
                "failed_connections": connection.metrics.failed_connections,
                "average_response_time": connection.metrics.average_response_time,
                "last_health_check": connection.metrics.last_health_check.isoformat(),
                "last_error": str(connection.last_error) if connection.last_error else None
            }
        
        return status
    
    async def close_all(self):
        """关闭所有连接"""
        self.is_running = False
        
        # 停止健康检查任务
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        # 关闭所有连接
        for name, connection in self.connections.items():
            await connection.disconnect()
            logger.info(f"数据库连接 {name} 已关闭")
        
        self.connections.clear()
        logger.info("所有数据库连接已关闭")


# 全局数据库池管理器实例
_pool_manager: Optional[DatabasePoolManager] = None


async def init_database_pools(config: Dict[str, Any]) -> DatabasePoolManager:
    """初始化全局数据库连接池管理器"""
    global _pool_manager
    
    _pool_manager = DatabasePoolManager(config)
    await _pool_manager.initialize()
    return _pool_manager


def get_database_pool_manager() -> DatabasePoolManager:
    """获取全局数据库连接池管理器"""
    if _pool_manager is None:
        raise RuntimeError("数据库连接池管理器未初始化，请先调用 init_database_pools")
    return _pool_manager


async def get_database_connection(name: str) -> DatabaseConnection:
    """获取数据库连接的便捷函数"""
    return await get_database_pool_manager().get_connection(name) 