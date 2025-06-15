"""
优化的数据库连接池管理器
包含连接池监控、自动重连和性能优化
"""

import asyncio
import logging
from typing import Optional, Dict, Any, AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    AsyncEngine, 
    AsyncSession, 
    async_sessionmaker
)
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy import event, text
from redis.asyncio import Redis, ConnectionPool as RedisConnectionPool
import time
from datetime import datetime, timedelta

from internal.config.settings import get_settings

logger = logging.getLogger(__name__)


class DatabaseConnectionPool:
    """数据库连接池管理器"""
    
    def __init__(self):
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker] = None
        self.redis_pool: Optional[RedisConnectionPool] = None
        self.redis: Optional[Redis] = None
        self._connection_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'pool_size': 0,
            'overflow_size': 0,
            'checked_out': 0,
            'checked_in': 0,
            'invalidated': 0
        }
        
    async def initialize(self):
        """初始化连接池"""
        settings = get_settings()
        
        # 创建数据库引擎
        self.engine = create_async_engine(
            settings.database_url,
            # 连接池配置
            poolclass=QueuePool,
            pool_size=settings.db_pool_size,  # 核心连接数
            max_overflow=settings.db_max_overflow,  # 最大溢出连接数
            pool_timeout=settings.db_pool_timeout,  # 获取连接超时时间
            pool_recycle=settings.db_pool_recycle,  # 连接回收时间
            pool_pre_ping=True,  # 连接前ping检查
            
            # 性能优化配置
            echo=settings.debug,  # 开发环境下显示SQL
            echo_pool=settings.debug,  # 显示连接池日志
            future=True,
            
            # 连接参数
            connect_args={
                "server_settings": {
                    "application_name": "suoke_auth_service",
                    "jit": "off",  # 关闭JIT以提高连接速度
                },
                "command_timeout": 60,
                "prepared_statement_cache_size": 0,  # 禁用预处理语句缓存
            }
        )
        
        # 创建会话工厂
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,  # 手动控制flush时机
            autocommit=False
        )
        
        # 创建Redis连接池
        self.redis_pool = RedisConnectionPool(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            db=settings.redis_db,
            max_connections=settings.redis_max_connections,
            retry_on_timeout=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            health_check_interval=30
        )
        
        self.redis = Redis(connection_pool=self.redis_pool)
        
        # 注册事件监听器
        self._register_event_listeners()
        
        # 启动监控任务
        asyncio.create_task(self._monitor_connections())
        
        logger.info("数据库连接池初始化完成")
    
    def _register_event_listeners(self):
        """注册数据库事件监听器"""
        
        @event.listens_for(self.engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """连接时设置数据库参数"""
            if hasattr(dbapi_connection, 'execute'):
                # PostgreSQL优化设置
                dbapi_connection.execute("SET statement_timeout = '60s'")
                dbapi_connection.execute("SET lock_timeout = '30s'")
                dbapi_connection.execute("SET idle_in_transaction_session_timeout = '300s'")
        
        @event.listens_for(self.engine.sync_engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """连接检出时的处理"""
            self._connection_stats['checked_out'] += 1
            self._connection_stats['active_connections'] += 1
        
        @event.listens_for(self.engine.sync_engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """连接检入时的处理"""
            self._connection_stats['checked_in'] += 1
            self._connection_stats['active_connections'] -= 1
        
        @event.listens_for(self.engine.sync_engine, "invalidate")
        def receive_invalidate(dbapi_connection, connection_record, exception):
            """连接失效时的处理"""
            self._connection_stats['invalidated'] += 1
            logger.warning(f"数据库连接失效: {exception}")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取数据库会话（上下文管理器）"""
        if not self.session_factory:
            raise RuntimeError("连接池未初始化")
        
        session = self.session_factory()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"数据库会话错误: {e}")
            raise
        finally:
            await session.close()
    
    @asynccontextmanager
    async def get_redis(self) -> AsyncGenerator[Redis, None]:
        """获取Redis连接（上下文管理器）"""
        if not self.redis:
            raise RuntimeError("Redis连接池未初始化")
        
        try:
            yield self.redis
        except Exception as e:
            logger.error(f"Redis连接错误: {e}")
            raise
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息"""
        if not self.engine:
            return {}
        
        pool = self.engine.pool
        
        stats = {
            **self._connection_stats,
            'pool_size': pool.size(),
            'checked_out_connections': pool.checkedout(),
            'overflow_connections': pool.overflow(),
            'invalid_connections': pool.invalidated(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Redis连接统计
        if self.redis_pool:
            redis_stats = {
                'redis_created_connections': self.redis_pool.created_connections,
                'redis_available_connections': len(self.redis_pool._available_connections),
                'redis_in_use_connections': len(self.redis_pool._in_use_connections)
            }
            stats.update(redis_stats)
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health_status = {
            'database': False,
            'redis': False,
            'timestamp': datetime.now().isoformat()
        }
        
        # 数据库健康检查
        try:
            async with self.get_session() as session:
                result = await session.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    health_status['database'] = True
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            health_status['database_error'] = str(e)
        
        # Redis健康检查
        try:
            async with self.get_redis() as redis:
                await redis.ping()
                health_status['redis'] = True
        except Exception as e:
            logger.error(f"Redis健康检查失败: {e}")
            health_status['redis_error'] = str(e)
        
        return health_status
    
    async def _monitor_connections(self):
        """监控连接池状态"""
        while True:
            try:
                stats = await self.get_connection_stats()
                
                # 记录统计信息到Redis
                if self.redis:
                    await self.redis.setex(
                        "connection_pool_stats",
                        300,  # 5分钟过期
                        str(stats)
                    )
                
                # 检查连接池健康状态
                if stats.get('checked_out_connections', 0) > stats.get('pool_size', 0) * 0.8:
                    logger.warning("连接池使用率过高，可能需要调整配置")
                
                # 每30秒检查一次
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"连接池监控错误: {e}")
                await asyncio.sleep(60)  # 出错时延长检查间隔
    
    async def cleanup(self):
        """清理连接池资源"""
        if self.engine:
            await self.engine.dispose()
            logger.info("数据库连接池已关闭")
        
        if self.redis_pool:
            await self.redis_pool.disconnect()
            logger.info("Redis连接池已关闭")


# 全局连接池实例
_connection_pool: Optional[DatabaseConnectionPool] = None


async def get_connection_pool() -> DatabaseConnectionPool:
    """获取全局连接池实例"""
    global _connection_pool
    
    if _connection_pool is None:
        _connection_pool = DatabaseConnectionPool()
        await _connection_pool.initialize()
    
    return _connection_pool


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（依赖注入用）"""
    pool = await get_connection_pool()
    async with pool.get_session() as session:
        yield session


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    """获取Redis客户端（依赖注入用）"""
    pool = await get_connection_pool()
    async with pool.get_redis() as redis:
        yield redis


class ConnectionPoolMetrics:
    """连接池指标收集器"""
    
    def __init__(self, connection_pool: DatabaseConnectionPool):
        self.pool = connection_pool
    
    async def collect_metrics(self) -> Dict[str, float]:
        """收集连接池指标"""
        stats = await self.pool.get_connection_stats()
        
        metrics = {
            'db_connections_active': float(stats.get('active_connections', 0)),
            'db_connections_checked_out': float(stats.get('checked_out_connections', 0)),
            'db_connections_overflow': float(stats.get('overflow_connections', 0)),
            'db_connections_invalidated_total': float(stats.get('invalidated', 0)),
            'db_pool_size': float(stats.get('pool_size', 0)),
            'redis_connections_available': float(stats.get('redis_available_connections', 0)),
            'redis_connections_in_use': float(stats.get('redis_in_use_connections', 0)),
        }
        
        return metrics


# 连接池配置优化建议
class ConnectionPoolOptimizer:
    """连接池配置优化器"""
    
    @staticmethod
    def get_recommended_settings(concurrent_users: int = 1000) -> Dict[str, Any]:
        """根据并发用户数获取推荐的连接池配置"""
        
        # 基于并发用户数计算连接池大小
        base_pool_size = max(10, concurrent_users // 100)
        max_overflow = max(20, concurrent_users // 50)
        
        return {
            'db_pool_size': base_pool_size,
            'db_max_overflow': max_overflow,
            'db_pool_timeout': 30,
            'db_pool_recycle': 3600,  # 1小时
            'redis_max_connections': max(20, concurrent_users // 50),
            'redis_socket_timeout': 5,
            'redis_socket_connect_timeout': 5
        }
    
    @staticmethod
    async def analyze_pool_performance(
        connection_pool: DatabaseConnectionPool,
        duration_minutes: int = 60
    ) -> Dict[str, Any]:
        """分析连接池性能"""
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        samples = []
        
        while time.time() < end_time:
            stats = await connection_pool.get_connection_stats()
            samples.append({
                'timestamp': time.time(),
                'active_connections': stats.get('active_connections', 0),
                'checked_out': stats.get('checked_out_connections', 0),
                'overflow': stats.get('overflow_connections', 0)
            })
            
            await asyncio.sleep(60)  # 每分钟采样一次
        
        # 分析结果
        if not samples:
            return {}
        
        avg_active = sum(s['active_connections'] for s in samples) / len(samples)
        max_active = max(s['active_connections'] for s in samples)
        avg_overflow = sum(s['overflow'] for s in samples) / len(samples)
        
        analysis = {
            'duration_minutes': duration_minutes,
            'sample_count': len(samples),
            'avg_active_connections': avg_active,
            'max_active_connections': max_active,
            'avg_overflow_connections': avg_overflow,
            'recommendations': []
        }
        
        # 生成优化建议
        current_pool_size = samples[0].get('pool_size', 0) if samples else 0
        
        if max_active > current_pool_size * 0.8:
            analysis['recommendations'].append(
                f"建议增加连接池大小到 {int(max_active * 1.2)}"
            )
        
        if avg_overflow > 0:
            analysis['recommendations'].append(
                "检测到连接溢出，建议增加核心连接池大小"
            )
        
        return analysis