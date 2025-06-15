"""
数据库连接管理器

提供高效的数据库连接池管理、查询优化和监控功能。
"""
import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, AsyncGenerator, List
from dataclasses import dataclass
from datetime import datetime, timedelta

import asyncpg
from asyncpg import Pool, Connection
from internal.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ConnectionStats:
    """连接统计信息"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    total_queries: int = 0
    slow_queries: int = 0
    avg_query_time: float = 0.0
    last_reset: datetime = None


@dataclass
class QueryMetrics:
    """查询指标"""
    query_hash: str
    sql: str
    execution_count: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    max_time: float = 0.0
    min_time: float = float('inf')
    error_count: int = 0
    last_executed: Optional[datetime] = None


class DatabaseConnectionManager:
    """数据库连接管理器"""
    
    def __init__(self):
        self._pool: Optional[Pool] = None
        self._stats = ConnectionStats()
        self._query_metrics: Dict[str, QueryMetrics] = {}
        self._slow_query_threshold = 1.0  # 1秒
        self._is_initialized = False
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """初始化连接池"""
        if self._is_initialized:
            return
        
        async with self._lock:
            if self._is_initialized:
                return
            
            try:
                # 构建数据库URL
                database_url = self._build_database_url()
                
                # 创建连接池
                self._pool = await asyncpg.create_pool(
                    database_url,
                    min_size=settings.db_pool_min_size,
                    max_size=settings.db_pool_max_size,
                    max_queries=settings.db_pool_max_queries,
                    max_inactive_connection_lifetime=settings.db_pool_max_inactive_time,
                    command_timeout=settings.db_command_timeout,
                    server_settings={
                        'application_name': 'suoke-auth-service',
                        'timezone': 'UTC',
                    },
                    init=self._init_connection
                )
                
                self._stats.last_reset = datetime.utcnow()
                self._is_initialized = True
                
                # 启动连接池监控
                asyncio.create_task(self._monitor_pool_health())
                
                logger.info(f"数据库连接池初始化成功: min={settings.db_pool_min_size}, max={settings.db_pool_max_size}")
                
            except Exception as e:
                logger.error(f"数据库连接池初始化失败: {str(e)}")
                raise
    
    async def close(self) -> None:
        """关闭连接池"""
        if self._pool:
            await self._pool.close()
            self._pool = None
            self._is_initialized = False
            logger.info("数据库连接池已关闭")
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[Connection, None]:
        """获取数据库连接"""
        if not self._is_initialized:
            await self.initialize()
        
        connection = None
        start_time = time.time()
        
        try:
            connection = await self._pool.acquire()
            self._stats.active_connections += 1
            self._stats.total_connections += 1
            
            yield connection
            
        except Exception as e:
            self._stats.failed_connections += 1
            logger.error(f"获取数据库连接失败: {str(e)}")
            raise
        finally:
            if connection:
                try:
                    await self._pool.release(connection)
                    self._stats.active_connections -= 1
                except Exception as e:
                    logger.error(f"释放数据库连接失败: {str(e)}")
            
            # 记录连接时间
            connection_time = time.time() - start_time
            if connection_time > 5.0:  # 连接时间超过5秒
                logger.warning(f"数据库连接获取耗时过长: {connection_time:.2f}秒")
    
    async def execute_query(
        self, 
        sql: str, 
        *args, 
        fetch_mode: str = 'all',
        timeout: Optional[float] = None
    ) -> Any:
        """执行查询"""
        query_hash = str(hash(sql))
        start_time = time.time()
        
        try:
            async with self.get_connection() as conn:
                # 设置查询超时
                if timeout:
                    conn = conn.with_timeout(timeout)
                
                # 执行查询
                if fetch_mode == 'all':
                    result = await conn.fetch(sql, *args)
                elif fetch_mode == 'one':
                    result = await conn.fetchrow(sql, *args)
                elif fetch_mode == 'val':
                    result = await conn.fetchval(sql, *args)
                elif fetch_mode == 'execute':
                    result = await conn.execute(sql, *args)
                else:
                    raise ValueError(f"不支持的fetch_mode: {fetch_mode}")
                
                # 记录查询指标
                execution_time = time.time() - start_time
                self._record_query_metrics(query_hash, sql, execution_time, success=True)
                
                return result
                
        except Exception as e:
            execution_time = time.time() - start_time
            self._record_query_metrics(query_hash, sql, execution_time, success=False)
            
            logger.error(f"查询执行失败: {str(e)}, SQL: {sql[:100]}...")
            raise
    
    async def execute_transaction(self, queries: List[tuple]) -> List[Any]:
        """执行事务"""
        results = []
        start_time = time.time()
        
        try:
            async with self.get_connection() as conn:
                async with conn.transaction():
                    for sql, args, fetch_mode in queries:
                        if fetch_mode == 'all':
                            result = await conn.fetch(sql, *args)
                        elif fetch_mode == 'one':
                            result = await conn.fetchrow(sql, *args)
                        elif fetch_mode == 'val':
                            result = await conn.fetchval(sql, *args)
                        elif fetch_mode == 'execute':
                            result = await conn.execute(sql, *args)
                        else:
                            raise ValueError(f"不支持的fetch_mode: {fetch_mode}")
                        
                        results.append(result)
            
            transaction_time = time.time() - start_time
            logger.info(f"事务执行成功，耗时: {transaction_time:.3f}秒，查询数: {len(queries)}")
            
            return results
            
        except Exception as e:
            transaction_time = time.time() - start_time
            logger.error(f"事务执行失败，耗时: {transaction_time:.3f}秒: {str(e)}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            start_time = time.time()
            
            async with self.get_connection() as conn:
                await conn.fetchval("SELECT 1")
            
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "pool_size": self._pool.get_size() if self._pool else 0,
                "pool_free": self._pool.get_idle_size() if self._pool else 0,
                "stats": {
                    "total_connections": self._stats.total_connections,
                    "active_connections": self._stats.active_connections,
                    "failed_connections": self._stats.failed_connections,
                    "total_queries": self._stats.total_queries,
                    "slow_queries": self._stats.slow_queries,
                    "avg_query_time": self._stats.avg_query_time
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "pool_size": self._pool.get_size() if self._pool else 0,
                "pool_free": self._pool.get_idle_size() if self._pool else 0
            }
    
    def get_query_metrics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取查询指标"""
        # 按平均执行时间排序
        sorted_metrics = sorted(
            self._query_metrics.values(),
            key=lambda x: x.avg_time,
            reverse=True
        )
        
        return [
            {
                "sql": metric.sql[:100] + "..." if len(metric.sql) > 100 else metric.sql,
                "execution_count": metric.execution_count,
                "avg_time": round(metric.avg_time, 3),
                "max_time": round(metric.max_time, 3),
                "min_time": round(metric.min_time, 3),
                "total_time": round(metric.total_time, 3),
                "error_count": metric.error_count,
                "last_executed": metric.last_executed.isoformat() if metric.last_executed else None
            }
            for metric in sorted_metrics[:limit]
        ]
    
    def reset_stats(self) -> None:
        """重置统计信息"""
        self._stats = ConnectionStats()
        self._query_metrics.clear()
        self._stats.last_reset = datetime.utcnow()
        logger.info("数据库统计信息已重置")
    
    def _build_database_url(self) -> str:
        """构建数据库URL"""
        return (
            f"postgresql://{settings.db_user}:{settings.db_password}"
            f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
        )
    
    async def _init_connection(self, conn: Connection) -> None:
        """初始化连接"""
        try:
            # 设置连接参数
            await conn.execute("SET timezone = 'UTC'")
            await conn.execute("SET statement_timeout = '30s'")
            await conn.execute("SET lock_timeout = '10s'")
            
            # 注册自定义类型（如果需要）
            # await conn.set_type_codec(...)
            
        except Exception as e:
            logger.error(f"连接初始化失败: {str(e)}")
            raise
    
    def _record_query_metrics(
        self, 
        query_hash: str, 
        sql: str, 
        execution_time: float, 
        success: bool
    ) -> None:
        """记录查询指标"""
        self._stats.total_queries += 1
        
        if execution_time > self._slow_query_threshold:
            self._stats.slow_queries += 1
            logger.warning(f"慢查询检测: {execution_time:.3f}秒, SQL: {sql[:100]}...")
        
        # 更新平均查询时间
        if self._stats.total_queries == 1:
            self._stats.avg_query_time = execution_time
        else:
            self._stats.avg_query_time = (
                (self._stats.avg_query_time * (self._stats.total_queries - 1) + execution_time) 
                / self._stats.total_queries
            )
        
        # 更新查询指标
        if query_hash not in self._query_metrics:
            self._query_metrics[query_hash] = QueryMetrics(
                query_hash=query_hash,
                sql=sql
            )
        
        metric = self._query_metrics[query_hash]
        metric.execution_count += 1
        metric.total_time += execution_time
        metric.avg_time = metric.total_time / metric.execution_count
        metric.max_time = max(metric.max_time, execution_time)
        metric.min_time = min(metric.min_time, execution_time)
        metric.last_executed = datetime.utcnow()
        
        if not success:
            metric.error_count += 1
    
    async def _monitor_pool_health(self) -> None:
        """监控连接池健康状态"""
        while self._is_initialized and self._pool:
            try:
                await asyncio.sleep(30)  # 每30秒检查一次
                
                if not self._pool:
                    break
                
                # 获取连接池状态
                pool_size = self._pool.get_size()
                pool_free = self._pool.get_idle_size()
                pool_usage = (pool_size - pool_free) / pool_size if pool_size > 0 else 0
                
                logger.debug(f"连接池状态: 总数={pool_size}, 空闲={pool_free}, 使用率={pool_usage:.2%}")
                
                # 动态调整连接池大小
                await self._adjust_pool_size(pool_usage)
                
                # 检查连接健康
                await self._check_connections_health()
                
            except Exception as e:
                logger.error(f"连接池监控失败: {str(e)}")
                await asyncio.sleep(60)  # 出错时延长检查间隔
    
    async def _adjust_pool_size(self, usage_rate: float) -> None:
        """动态调整连接池大小"""
        try:
            current_size = self._pool.get_size()
            
            # 如果使用率过高，尝试增加连接
            if usage_rate > 0.8 and current_size < settings.db_pool_max_size:
                # 这里asyncpg不支持动态调整，只记录建议
                logger.info(f"连接池使用率过高 ({usage_rate:.2%})，建议增加连接数")
            
            # 如果使用率过低，记录建议减少连接
            elif usage_rate < 0.3 and current_size > settings.db_pool_min_size:
                logger.info(f"连接池使用率较低 ({usage_rate:.2%})，可考虑减少连接数")
                
        except Exception as e:
            logger.error(f"调整连接池大小失败: {str(e)}")
    
    async def _check_connections_health(self) -> None:
        """检查连接健康状态"""
        try:
            # 简单的健康检查
            async with self.get_connection() as conn:
                await conn.fetchval("SELECT 1")
                
        except Exception as e:
            logger.warning(f"连接健康检查失败: {str(e)}")
            # 可以在这里实现故障转移逻辑
    
    async def get_pool_metrics(self) -> Dict[str, Any]:
        """获取连接池详细指标"""
        if not self._pool:
            return {"status": "not_initialized"}
        
        try:
            pool_size = self._pool.get_size()
            pool_free = self._pool.get_idle_size()
            pool_used = pool_size - pool_free
            
            return {
                "pool_size": pool_size,
                "free_connections": pool_free,
                "used_connections": pool_used,
                "usage_rate": (pool_used / pool_size * 100) if pool_size > 0 else 0,
                "min_size": settings.db_pool_min_size,
                "max_size": settings.db_pool_max_size,
                "max_queries_per_connection": settings.db_pool_max_queries,
                "max_inactive_time": settings.db_pool_max_inactive_time,
                "command_timeout": settings.db_command_timeout,
                "stats": {
                    "total_connections": self._stats.total_connections,
                    "active_connections": self._stats.active_connections,
                    "failed_connections": self._stats.failed_connections,
                    "total_queries": self._stats.total_queries,
                    "slow_queries": self._stats.slow_queries,
                    "avg_query_time": self._stats.avg_query_time
                }
            }
            
        except Exception as e:
            logger.error(f"获取连接池指标失败: {str(e)}")
            return {"status": "error", "error": str(e)}


# 全局连接管理器实例
_connection_manager: Optional[DatabaseConnectionManager] = None


def get_connection_manager() -> DatabaseConnectionManager:
    """获取连接管理器实例"""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = DatabaseConnectionManager()
    return _connection_manager


async def init_database() -> None:
    """初始化数据库"""
    manager = get_connection_manager()
    await manager.initialize()


async def close_database() -> None:
    """关闭数据库"""
    global _connection_manager
    if _connection_manager:
        await _connection_manager.close()
        _connection_manager = None


# 便捷函数
async def execute_query(sql: str, *args, **kwargs) -> Any:
    """执行查询的便捷函数"""
    manager = get_connection_manager()
    return await manager.execute_query(sql, *args, **kwargs)


async def execute_transaction(queries: List[tuple]) -> List[Any]:
    """执行事务的便捷函数"""
    manager = get_connection_manager()
    return await manager.execute_transaction(queries) 