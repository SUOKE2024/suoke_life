#!/usr/bin/env python3
"""
索克生活无障碍服务 - 数据库连接池优化器

提供高性能的数据库连接池管理、查询优化和监控功能。
"""

import asyncio
import hashlib
import json
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """数据库类型"""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    REDIS = "redis"


class ConnectionStatus(Enum):
    """连接状态"""

    IDLE = "idle"
    ACTIVE = "active"
    CLOSED = "closed"
    ERROR = "error"


@dataclass
class DatabaseConfig:
    """数据库配置"""

    db_id: str
    db_type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    password: str
    min_connections: int = 5
    max_connections: int = 20
    connection_timeout: float = 30.0
    idle_timeout: float = 300.0
    max_lifetime: float = 3600.0
    retry_attempts: int = 3
    retry_delay: float = 1.0
    ssl_enabled: bool = False
    pool_recycle: int = 3600
    echo: bool = False


@dataclass
class QueryMetrics:
    """查询指标"""

    query_id: str
    sql: str
    execution_time: float
    rows_affected: int
    timestamp: datetime
    connection_id: str
    success: bool
    error: Optional[str] = None


class DatabaseConnection:
    """数据库连接包装器"""

    def __init__(self, connection_id: str, config: DatabaseConfig):
        self.connection_id = connection_id
        self.config = config
        self.connection = None
        self.status = ConnectionStatus.CLOSED
        self.created_at = time.time()
        self.last_used = time.time()
        self.query_count = 0
        self.total_query_time = 0.0
        self.error_count = 0
        self.lock = threading.Lock()

    async def connect(self) -> bool:
        """建立数据库连接"""
        try:
            with self.lock:
                if self.status == ConnectionStatus.ACTIVE:
                    return True

                # 模拟数据库连接（实际应用中应该使用真实的数据库驱动）
                await asyncio.sleep(0.1)  # 模拟连接时间

                self.connection = {
                    "db_type": self.config.db_type.value,
                    "host": self.config.host,
                    "port": self.config.port,
                    "database": self.config.database,
                    "connected_at": datetime.now().isoformat(),
                }

                self.status = ConnectionStatus.IDLE
                self.last_used = time.time()

                logger.debug(f"数据库连接建立成功: {self.connection_id}")
                return True

        except Exception as e:
            self.status = ConnectionStatus.ERROR
            logger.error(f"数据库连接失败: {self.connection_id} - {e}")
            return False

    async def disconnect(self) -> bool:
        """断开数据库连接"""
        try:
            with self.lock:
                if self.connection:
                    # 模拟断开连接
                    self.connection = None

                self.status = ConnectionStatus.CLOSED
                logger.debug(f"数据库连接断开: {self.connection_id}")
                return True

        except Exception as e:
            logger.error(f"数据库连接断开失败: {self.connection_id} - {e}")
            return False

    async def execute_query(
        self, sql: str, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """执行查询"""
        if self.status != ConnectionStatus.IDLE:
            raise RuntimeError(f"连接不可用: {self.connection_id}")

        start_time = time.time()
        query_id = hashlib.sha256(f"{sql}:{time.time()}".encode()).hexdigest()[:8]

        try:
            with self.lock:
                self.status = ConnectionStatus.ACTIVE
                self.last_used = time.time()

            # 模拟查询执行
            execution_time = 0.01 + (hash(sql) % 100) / 10000  # 0.01-0.02秒
            await asyncio.sleep(execution_time)

            # 模拟查询结果
            if sql.strip().upper().startswith("SELECT"):
                result = {
                    "rows": [
                        {
                            "id": 1,
                            "name": "测试数据1",
                            "created_at": datetime.now().isoformat(),
                        },
                        {
                            "id": 2,
                            "name": "测试数据2",
                            "created_at": datetime.now().isoformat(),
                        },
                    ],
                    "row_count": 2,
                }
            elif sql.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                result = {"rows_affected": 1, "last_insert_id": 123}
            else:
                result = {"status": "executed"}

            execution_time = time.time() - start_time

            with self.lock:
                self.status = ConnectionStatus.IDLE
                self.query_count += 1
                self.total_query_time += execution_time

            return {
                "query_id": query_id,
                "result": result,
                "execution_time": execution_time,
                "success": True,
            }

        except Exception as e:
            execution_time = time.time() - start_time

            with self.lock:
                self.status = ConnectionStatus.IDLE
                self.error_count += 1

            return {
                "query_id": query_id,
                "result": None,
                "execution_time": execution_time,
                "success": False,
                "error": str(e),
            }

    def is_expired(self) -> bool:
        """检查连接是否过期"""
        current_time = time.time()

        # 检查空闲超时
        if current_time - self.last_used > self.config.idle_timeout:
            return True

        # 检查最大生命周期
        if current_time - self.created_at > self.config.max_lifetime:
            return True

        return False

    def get_stats(self) -> Dict[str, Any]:
        """获取连接统计信息"""
        current_time = time.time()
        avg_query_time = (
            self.total_query_time / self.query_count if self.query_count > 0 else 0.0
        )

        return {
            "connection_id": self.connection_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "last_used": self.last_used,
            "age_seconds": current_time - self.created_at,
            "idle_seconds": current_time - self.last_used,
            "query_count": self.query_count,
            "error_count": self.error_count,
            "avg_query_time": avg_query_time,
            "error_rate": self.error_count / max(self.query_count, 1) * 100,
        }


class ConnectionPool:
    """数据库连接池"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connections: Dict[str, DatabaseConnection] = {}
        self.available_connections: deque = deque()
        self.connection_counter = 0
        self.pool_lock = threading.Lock()

        # 统计信息
        self.stats = {
            "total_connections_created": 0,
            "total_connections_destroyed": 0,
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "total_query_time": 0.0,
            "pool_hits": 0,
            "pool_misses": 0,
        }

        # 监控任务
        self.cleanup_task = None
        self.is_running = False

    async def initialize(self) -> bool:
        """初始化连接池"""
        try:
            # 创建最小连接数
            for _ in range(self.config.min_connections):
                connection = await self._create_connection()
                if connection:
                    self.available_connections.append(connection.connection_id)

            # 启动清理任务
            self.is_running = True
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())

            logger.info(f"连接池初始化完成: {self.config.db_id}")
            return True

        except Exception as e:
            logger.error(f"连接池初始化失败: {e}")
            return False

    async def _create_connection(self) -> Optional[DatabaseConnection]:
        """创建新连接"""
        try:
            with self.pool_lock:
                if len(self.connections) >= self.config.max_connections:
                    return None

                self.connection_counter += 1
                connection_id = f"{self.config.db_id}_conn_{self.connection_counter}"

            connection = DatabaseConnection(connection_id, self.config)
            success = await connection.connect()

            if success:
                with self.pool_lock:
                    self.connections[connection_id] = connection
                    self.stats["total_connections_created"] += 1

                logger.debug(f"新连接创建成功: {connection_id}")
                return connection
            else:
                return None

        except Exception as e:
            logger.error(f"创建连接失败: {e}")
            return None

    async def get_connection(
        self, timeout: float = None
    ) -> Optional[DatabaseConnection]:
        """获取连接"""
        timeout = timeout or self.config.connection_timeout
        start_time = time.time()

        while time.time() - start_time < timeout:
            # 尝试从可用连接中获取
            with self.pool_lock:
                if self.available_connections:
                    connection_id = self.available_connections.popleft()
                    connection = self.connections.get(connection_id)

                    if connection and not connection.is_expired():
                        self.stats["pool_hits"] += 1
                        return connection
                    elif connection:
                        # 连接已过期，移除它
                        await self._destroy_connection(connection_id)

            # 尝试创建新连接
            connection = await self._create_connection()
            if connection:
                self.stats["pool_misses"] += 1
                return connection

            # 等待一段时间后重试
            await asyncio.sleep(0.1)

        logger.warning(f"获取连接超时: {self.config.db_id}")
        return None

    async def return_connection(self, connection: DatabaseConnection):
        """归还连接"""
        if connection.connection_id not in self.connections:
            return

        if connection.is_expired() or connection.status == ConnectionStatus.ERROR:
            await self._destroy_connection(connection.connection_id)
        else:
            with self.pool_lock:
                if connection.connection_id not in self.available_connections:
                    self.available_connections.append(connection.connection_id)

    async def _destroy_connection(self, connection_id: str):
        """销毁连接"""
        with self.pool_lock:
            connection = self.connections.pop(connection_id, None)

            # 从可用连接中移除
            try:
                self.available_connections.remove(connection_id)
            except ValueError:
                pass

        if connection:
            await connection.disconnect()
            self.stats["total_connections_destroyed"] += 1
            logger.debug(f"连接已销毁: {connection_id}")

    async def _cleanup_loop(self) -> None:
        """清理循环"""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # 每分钟清理一次

                # 清理过期连接
                expired_connections = []
                with self.pool_lock:
                    for connection_id, connection in self.connections.items():
                        if connection.is_expired():
                            expired_connections.append(connection_id)

                for connection_id in expired_connections:
                    await self._destroy_connection(connection_id)

                # 确保最小连接数
                current_count = len(self.connections)
                if current_count < self.config.min_connections:
                    needed = self.config.min_connections - current_count
                    for _ in range(needed):
                        connection = await self._create_connection()
                        if connection:
                            self.available_connections.append(connection.connection_id)

            except Exception as e:
                logger.error(f"连接池清理失败: {e}")

    async def execute_query(
        self, sql: str, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """执行查询"""
        connection = await self.get_connection()
        if not connection:
            raise RuntimeError("无法获取数据库连接")

        try:
            result = await connection.execute_query(sql, parameters)

            # 更新统计信息
            self.stats["total_queries"] += 1
            if result["success"]:
                self.stats["successful_queries"] += 1
            else:
                self.stats["failed_queries"] += 1

            self.stats["total_query_time"] += result["execution_time"]

            return result

        finally:
            await self.return_connection(connection)

    def get_pool_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息"""
        with self.pool_lock:
            total_connections = len(self.connections)
            available_connections = len(self.available_connections)
            active_connections = total_connections - available_connections

        avg_query_time = self.stats["total_query_time"] / max(
            self.stats["total_queries"], 1
        )

        success_rate = (
            self.stats["successful_queries"] / max(self.stats["total_queries"], 1) * 100
        )

        pool_hit_rate = (
            self.stats["pool_hits"]
            / max(self.stats["pool_hits"] + self.stats["pool_misses"], 1)
            * 100
        )

        return {
            "db_id": self.config.db_id,
            "total_connections": total_connections,
            "available_connections": available_connections,
            "active_connections": active_connections,
            "min_connections": self.config.min_connections,
            "max_connections": self.config.max_connections,
            "avg_query_time": avg_query_time,
            "success_rate_percent": success_rate,
            "pool_hit_rate_percent": pool_hit_rate,
            **self.stats,
        }

    async def shutdown(self) -> None:
        """关闭连接池"""
        self.is_running = False

        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass

        # 关闭所有连接
        connection_ids = list(self.connections.keys())
        for connection_id in connection_ids:
            await self._destroy_connection(connection_id)

        logger.info(f"连接池已关闭: {self.config.db_id}")


class QueryOptimizer:
    """查询优化器"""

    def __init__(self) -> None:
        self.query_cache: Dict[str, Any] = {}
        self.query_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "count": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "min_time": float("inf"),
                "max_time": 0.0,
                "error_count": 0,
            }
        )
        self.slow_queries: deque = deque(maxlen=100)
        self.cache_hit_count = 0
        self.cache_miss_count = 0

    def _normalize_query(self, sql: str) -> str:
        """标准化查询语句"""
        # 简单的查询标准化（实际应用中可以更复杂）
        normalized = sql.strip().upper()
        # 移除多余空格
        normalized = " ".join(normalized.split())
        return normalized

    def _generate_cache_key(self, sql: str, parameters: Dict[str, Any] = None) -> str:
        """生成缓存键"""
        normalized_sql = self._normalize_query(sql)
        param_str = json.dumps(parameters or {}, sort_keys=True)
        combined = f"{normalized_sql}:{param_str}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def should_cache_query(self, sql: str) -> bool:
        """判断是否应该缓存查询"""
        normalized = self._normalize_query(sql)

        # 只缓存SELECT查询
        if not normalized.startswith("SELECT"):
            return False

        # 不缓存包含随机函数的查询
        if any(
            func in normalized
            for func in ["RAND()", "RANDOM()", "NOW()", "CURRENT_TIMESTAMP"]
        ):
            return False

        return True

    def get_cached_result(
        self, sql: str, parameters: Dict[str, Any] = None
    ) -> Optional[Any]:
        """获取缓存的查询结果"""
        if not self.should_cache_query(sql):
            return None

        cache_key = self._generate_cache_key(sql, parameters)

        if cache_key in self.query_cache:
            result, timestamp = self.query_cache[cache_key]

            # 检查缓存是否过期（5分钟）
            if time.time() - timestamp < 300:
                self.cache_hit_count += 1
                return result
            else:
                del self.query_cache[cache_key]

        self.cache_miss_count += 1
        return None

    def cache_query_result(
        self, sql: str, result: Any, parameters: Dict[str, Any] = None
    ):
        """缓存查询结果"""
        if not self.should_cache_query(sql):
            return

        cache_key = self._generate_cache_key(sql, parameters)
        self.query_cache[cache_key] = (result, time.time())

        # 限制缓存大小
        if len(self.query_cache) > 1000:
            # 删除最旧的缓存项
            oldest_key = min(
                self.query_cache.keys(), key=lambda k: self.query_cache[k][1]
            )
            del self.query_cache[oldest_key]

    def record_query_metrics(self, sql: str, execution_time: float, success: bool):
        """记录查询指标"""
        normalized_sql = self._normalize_query(sql)
        stats = self.query_stats[normalized_sql]

        stats["count"] += 1

        if success:
            stats["total_time"] += execution_time
            stats["avg_time"] = stats["total_time"] / stats["count"]
            stats["min_time"] = min(stats["min_time"], execution_time)
            stats["max_time"] = max(stats["max_time"], execution_time)

            # 记录慢查询（超过1秒）
            if execution_time > 1.0:
                self.slow_queries.append(
                    {
                        "sql": sql,
                        "execution_time": execution_time,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
        else:
            stats["error_count"] += 1

    def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """获取优化建议"""
        suggestions = []

        # 分析慢查询
        if self.slow_queries:
            avg_slow_time = sum(q["execution_time"] for q in self.slow_queries) / len(
                self.slow_queries
            )
            suggestions.append(
                {
                    "type": "slow_queries",
                    "description": f"发现 {len(self.slow_queries)} 个慢查询，平均执行时间 {avg_slow_time:.2f}秒",
                    "recommendation": "考虑添加索引或优化查询语句",
                    "priority": "high",
                }
            )

        # 分析缓存命中率
        total_cache_requests = self.cache_hit_count + self.cache_miss_count
        if total_cache_requests > 0:
            hit_rate = self.cache_hit_count / total_cache_requests * 100
            if hit_rate < 50:
                suggestions.append(
                    {
                        "type": "cache_optimization",
                        "description": f"查询缓存命中率较低: {hit_rate:.1f}%",
                        "recommendation": "考虑调整缓存策略或增加缓存时间",
                        "priority": "medium",
                    }
                )

        # 分析高频查询
        frequent_queries = sorted(
            self.query_stats.items(), key=lambda x: x[1]["count"], reverse=True
        )[:5]

        for sql, stats in frequent_queries:
            if stats["count"] > 100 and stats["avg_time"] > 0.1:
                suggestions.append(
                    {
                        "type": "frequent_query_optimization",
                        "description": f"高频查询需要优化: 执行 {stats['count']} 次，平均 {stats['avg_time']:.3f}秒",
                        "recommendation": "考虑添加索引或重写查询",
                        "priority": "medium",
                        "query": sql[:100] + "..." if len(sql) > 100 else sql,
                    }
                )

        return suggestions

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self.cache_hit_count + self.cache_miss_count
        hit_rate = (
            (self.cache_hit_count / total_requests * 100) if total_requests > 0 else 0
        )

        return {
            "cache_size": len(self.query_cache),
            "cache_hit_count": self.cache_hit_count,
            "cache_miss_count": self.cache_miss_count,
            "hit_rate_percent": hit_rate,
            "slow_queries_count": len(self.slow_queries),
        }


class DatabasePoolManager:
    """数据库连接池管理器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pools: Dict[str, ConnectionPool] = {}
        self.query_optimizer = QueryOptimizer()
        self.global_stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "total_query_time": 0.0,
        }

        logger.info("数据库连接池管理器初始化完成")

    async def add_database(self, config: DatabaseConfig) -> bool:
        """添加数据库"""
        try:
            pool = ConnectionPool(config)
            success = await pool.initialize()

            if success:
                self.pools[config.db_id] = pool
                logger.info(f"数据库添加成功: {config.db_id}")
                return True
            else:
                logger.error(f"数据库添加失败: {config.db_id}")
                return False

        except Exception as e:
            logger.error(f"添加数据库失败: {config.db_id} - {e}")
            return False

    async def execute_query(
        self, db_id: str, sql: str, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """执行查询"""
        if db_id not in self.pools:
            raise ValueError(f"数据库不存在: {db_id}")

        # 尝试从缓存获取结果
        cached_result = self.query_optimizer.get_cached_result(sql, parameters)
        if cached_result is not None:
            return {
                "result": cached_result,
                "execution_time": 0.0,
                "success": True,
                "cached": True,
            }

        # 执行查询
        pool = self.pools[db_id]
        result = await pool.execute_query(sql, parameters)

        # 更新全局统计
        self.global_stats["total_queries"] += 1
        if result["success"]:
            self.global_stats["successful_queries"] += 1
        else:
            self.global_stats["failed_queries"] += 1

        self.global_stats["total_query_time"] += result["execution_time"]

        # 记录查询指标
        self.query_optimizer.record_query_metrics(
            sql, result["execution_time"], result["success"]
        )

        # 缓存成功的查询结果
        if result["success"] and result.get("result"):
            self.query_optimizer.cache_query_result(sql, result["result"], parameters)

        result["cached"] = False
        return result

    def get_database_stats(self, db_id: str = None) -> Dict[str, Any]:
        """获取数据库统计信息"""
        if db_id:
            if db_id in self.pools:
                return self.pools[db_id].get_pool_stats()
            else:
                return {}

        # 返回所有数据库的统计信息
        return {db_id: pool.get_pool_stats() for db_id, pool in self.pools.items()}

    def get_global_stats(self) -> Dict[str, Any]:
        """获取全局统计信息"""
        avg_query_time = self.global_stats["total_query_time"] / max(
            self.global_stats["total_queries"], 1
        )

        success_rate = (
            self.global_stats["successful_queries"]
            / max(self.global_stats["total_queries"], 1)
            * 100
        )

        return {
            **self.global_stats,
            "avg_query_time": avg_query_time,
            "success_rate_percent": success_rate,
            "active_databases": len(self.pools),
            "cache_stats": self.query_optimizer.get_cache_stats(),
            "optimization_suggestions": self.query_optimizer.get_optimization_suggestions(),
        }

    async def optimize_pools(self) -> Dict[str, Any]:
        """优化连接池"""
        optimization_results = {}

        for db_id, pool in self.pools.items():
            try:
                stats = pool.get_pool_stats()

                # 如果成功率低，重新创建一些连接
                if stats["success_rate_percent"] < 95:
                    # 清理错误连接
                    error_connections = []
                    for conn_id, conn in pool.connections.items():
                        if conn.status == ConnectionStatus.ERROR:
                            error_connections.append(conn_id)

                    for conn_id in error_connections:
                        await pool._destroy_connection(conn_id)

                    optimization_results[db_id] = (
                        f"清理了 {len(error_connections)} 个错误连接"
                    )

                # 如果池命中率低，调整连接数
                elif stats["pool_hit_rate_percent"] < 80:
                    # 增加最小连接数
                    pool.config.min_connections = min(
                        pool.config.min_connections + 2, pool.config.max_connections
                    )
                    optimization_results[db_id] = (
                        f"增加最小连接数到 {pool.config.min_connections}"
                    )

                else:
                    optimization_results[db_id] = "连接池状态良好"

            except Exception as e:
                optimization_results[db_id] = f"优化失败: {e}"

        return optimization_results

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        issues = []
        healthy_pools = 0

        for db_id, pool in self.pools.items():
            stats = pool.get_pool_stats()

            # 检查连接池状态
            if stats["total_connections"] == 0:
                issues.append(f"数据库 {db_id} 无可用连接")
            elif stats["success_rate_percent"] < 95:
                issues.append(
                    f"数据库 {db_id} 成功率过低: {stats['success_rate_percent']:.1f}%"
                )
            else:
                healthy_pools += 1

        # 检查全局指标
        global_stats = self.get_global_stats()
        if global_stats["success_rate_percent"] < 95:
            issues.append(
                f"全局查询成功率过低: {global_stats['success_rate_percent']:.1f}%"
            )

        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "healthy_pools": healthy_pools,
            "total_pools": len(self.pools),
            "global_success_rate": global_stats["success_rate_percent"],
        }

    async def shutdown(self) -> None:
        """关闭所有连接池"""
        logger.info("正在关闭所有数据库连接池...")

        for db_id, pool in self.pools.items():
            await pool.shutdown()

        self.pools.clear()
        logger.info("所有数据库连接池已关闭")


# 全局数据库管理器实例
db_manager = None


def get_database_manager(config: Dict[str, Any] = None) -> DatabasePoolManager:
    """获取数据库管理器实例"""
    global db_manager
    if db_manager is None:
        db_manager = DatabasePoolManager(config or {})
    return db_manager


# 示例配置
EXAMPLE_CONFIG = {
    "databases": [
        {
            "db_id": "main_db",
            "db_type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "suoke_life",
            "username": "suoke_user",
            "password": "suoke_pass",
            "min_connections": 5,
            "max_connections": 20,
        },
        {
            "db_id": "cache_db",
            "db_type": "redis",
            "host": "localhost",
            "port": 6379,
            "database": "0",
            "username": "",
            "password": "",
            "min_connections": 2,
            "max_connections": 10,
        },
    ]
}


async def initialize_database_pools(config: Dict[str, Any]) -> DatabasePoolManager:
    """初始化数据库连接池"""
    manager = get_database_manager(config)

    # 添加数据库
    databases_config = config.get("databases", [])
    for db_config in databases_config:
        db_cfg = DatabaseConfig(
            db_id=db_config["db_id"],
            db_type=DatabaseType(db_config["db_type"]),
            host=db_config["host"],
            port=db_config["port"],
            database=db_config["database"],
            username=db_config["username"],
            password=db_config["password"],
            min_connections=db_config.get("min_connections", 5),
            max_connections=db_config.get("max_connections", 20),
        )

        await manager.add_database(db_cfg)

    logger.info("数据库连接池初始化完成")
    return manager


if __name__ == "__main__":
    # 测试代码
    async def test_database_pools() -> None:
        manager = await initialize_database_pools(EXAMPLE_CONFIG)

        # 测试查询
        result = await manager.execute_query(
            "main_db", "SELECT * FROM users WHERE active = true", {"limit": 10}
        )
        print(f"查询结果: {result}")

        # 获取统计信息
        stats = manager.get_global_stats()
        print(f"全局统计: {stats}")

        await manager.shutdown()

    asyncio.run(test_database_pools())
