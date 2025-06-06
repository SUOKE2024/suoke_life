"""
db_optimization - 索克生活项目模块
"""

from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
import asyncio
import asyncpg
import contextlib
import json
import logging
import time

#!/usr/bin/env python3
"""
数据库查询优化模块
提供查询分析、批量处理、索引建议等功能
"""



logger = logging.getLogger(__name__)


@dataclass
class QueryPlan:
    """查询计划"""

    query: str
    execution_time: float
    planning_time: float
    total_cost: float
    rows: int
    width: int
    plan_details: dict[str, Any]

    @property
    def is_slow(self) -> bool:
        """是否为慢查询"""
        return self.execution_time > 100  # 超过100ms认为是慢查询

    @property
    def needs_index(self) -> bool:
        """是否需要索引"""
        # 检查是否有全表扫描
        plan_str = json.dumps(self.plan_details)
        return "Seq Scan" in plan_str and self.rows > 1000


class QueryOptimizer:
    """SQL 查询优化器"""

    def __init__(self, slow_query_threshold: int = 100):
        self.slow_query_threshold = slow_query_threshold
        self.query_stats: dict[str, list[float]] = {}
        self.slow_queries: list[dict[str, Any]] = []

    async def explain_analyze(
        self,
        conn: asyncpg.Connection | AsyncSession,
        query: str,
        params: list[Any] | None = None,
    ) -> QueryPlan:
        """分析查询性能"""
        explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"

        try:
            if isinstance(conn, asyncpg.Connection):
                result = await conn.fetchval(explain_query, *(params or []))
            else:
                # SQLAlchemy AsyncSession
                result = await conn.execute(
                    text(explain_query).bindparams(*(params or []))
                )
                result = result.scalar()

            plan_data = json.loads(result)[0]

            # 提取关键信息
            plan = QueryPlan(
                query=query,
                execution_time=plan_data.get("Execution Time", 0),
                planning_time=plan_data.get("Planning Time", 0),
                total_cost=plan_data["Plan"].get("Total Cost", 0),
                rows=plan_data["Plan"].get("Plan Rows", 0),
                width=plan_data["Plan"].get("Plan Width", 0),
                plan_details=plan_data,
            )

            # 记录慢查询
            if plan.is_slow:
                self._record_slow_query(query, plan)

            return plan

        except Exception as e:
            logger.error(f"查询分析失败: {e}")
            raise

        @cache(timeout=300)  # 5分钟缓存
def _record_slow_query(self, query: str, plan: QueryPlan):
        """记录慢查询"""
        self.slow_queries.append(
            {
                "query": query,
                "execution_time": plan.execution_time,
                "planning_time": plan.planning_time,
                "total_cost": plan.total_cost,
                "timestamp": time.time(),
                "plan": plan.plan_details,
            }
        )

        # 限制记录数量
        if len(self.slow_queries) > 100:
            self.slow_queries = self.slow_queries[-100:]

    async def suggest_indexes(
        self, conn: asyncpg.Connection, table: str, schema: str = "public"
    ) -> list[str]:
        """建议索引"""
        suggestions = []

        # 分析表的统计信息
        stats_query = """
        SELECT
            attname,
            n_distinct,
            null_frac,
            avg_width,
            correlation
        FROM pg_stats
        WHERE schemaname = $1 AND tablename = $2
        """
        stats = await conn.fetch(stats_query, schema, table)

        # 分析缺失的索引
        missing_indexes_query = """
        SELECT
            schemaname,
            tablename,
            attname,
            index_ratio,
            avg_seq_tup_read,
            avg_idx_tup_read
        FROM (
            SELECT
                schemaname,
                tablename,
                attname,
                CASE WHEN idx_scan > 0
                    THEN CAST(idx_scan AS FLOAT) / (seq_scan + idx_scan)
                    ELSE 0
                END AS index_ratio,
                CASE WHEN seq_scan > 0
                    THEN seq_tup_read / seq_scan
                    ELSE 0
                END AS avg_seq_tup_read,
                CASE WHEN idx_scan > 0
                    THEN idx_tup_fetch / idx_scan
                    ELSE 0
                END AS avg_idx_tup_read
            FROM pg_stat_user_tables t
            JOIN pg_attribute a ON a.attrelid = t.relid
            WHERE schemaname = $1 AND tablename = $2
                AND attnum > 0 AND NOT attisdropped
        ) sub
        WHERE index_ratio < 0.95 AND avg_seq_tup_read > 1000
        """

        try:
            missing = await conn.fetch(missing_indexes_query, schema, table)

            for row in missing:
                if row["avg_seq_tup_read"] > 5000:
                    suggestions.append(
                        f"CREATE INDEX idx_{table}_{row['attname']} "
                        f"ON {schema}.{table}({row['attname']});"
                    )
        except Exception as e:
            logger.error(f"索引分析失败: {e}")

        # 基于统计信息的建议
        for stat in stats:
            # 高基数列适合建索引
            if stat["n_distinct"] > 100 and stat["null_frac"] < 0.5:
                col_name = stat["attname"]
                suggestions.append(
                    f"-- 建议: 列 {col_name} 有高基数 ({stat['n_distinct']}), "
                    f"适合建立索引\n"
                    f"CREATE INDEX idx_{table}_{col_name} ON {schema}.{table}({col_name});"
                )

            # 相关性高的列适合建索引
            if abs(stat["correlation"]) > 0.8:
                col_name = stat["attname"]
                suggestions.append(
                    f"-- 建议: 列 {col_name} 有高相关性 ({stat['correlation']:.2f}), "
                    f"适合建立索引\n"
                    f"CREATE INDEX idx_{table}_{col_name} ON {schema}.{table}({col_name});"
                )

        return list(set(suggestions))  # 去重

    async def analyze_table_usage(
        self, conn: asyncpg.Connection, schema: str = "public"
    ) -> dict[str, Any]:
        """分析表使用情况"""
        usage_query = """
        SELECT
            schemaname,
            tablename,
            seq_scan,
            seq_tup_read,
            idx_scan,
            idx_tup_fetch,
            n_tup_ins,
            n_tup_upd,
            n_tup_del,
            n_live_tup,
            n_dead_tup,
            last_vacuum,
            last_autovacuum
        FROM pg_stat_user_tables
        WHERE schemaname = $1
        ORDER BY seq_tup_read DESC
        """

        tables = await conn.fetch(usage_query, schema)

        analysis = {"tables": [], "recommendations": []}

        for table in tables:
            table_info = dict(table)

            # 计算索引使用率
            total_scans = table["seq_scan"] + table["idx_scan"]
            if total_scans > 0:
                index_usage_ratio = table["idx_scan"] / total_scans
                table_info["index_usage_ratio"] = index_usage_ratio

                # 建议
                if index_usage_ratio < 0.5 and table["seq_scan"] > 1000:
                    analysis["recommendations"].append(
                        {
                            "table": table["tablename"],
                            "issue": "索引使用率低",
                            "suggestion": f"表 {table['tablename']} 的索引使用率仅为 "
                            f"{index_usage_ratio:.2%}，建议优化查询或添加索引",
                        }
                    )

            # 死元组比例
            if table["n_live_tup"] > 0:
                dead_tuple_ratio = table["n_dead_tup"] / table["n_live_tup"]
                table_info["dead_tuple_ratio"] = dead_tuple_ratio

                if dead_tuple_ratio > 0.2:
                    analysis["recommendations"].append(
                        {
                            "table": table["tablename"],
                            "issue": "死元组过多",
                            "suggestion": f"表 {table['tablename']} 的死元组比例为 "
                            f"{dead_tuple_ratio:.2%}，建议执行 VACUUM",
                        }
                    )

            analysis["tables"].append(table_info)

        return analysis


class QueryBatcher:
    """批量查询处理器"""

    def __init__(self, batch_size: int = 100, timeout: float = 0.1):
        self.batch_size = batch_size
        self.timeout = timeout
        self.pending_queries: list[tuple] = []
        self.lock = asyncio.Lock()
        self._process_task = None
        self._pool = None

    def set_pool(self, pool: asyncpg.Pool):
        """设置连接池"""
        self._pool = pool

    async def start(self):
        """启动批处理器"""
        if not self._process_task:
            self._process_task = asyncio.create_task(self._process_loop())

    async def stop(self):
        """停止批处理器"""
        if self._process_task:
            self._process_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._process_task

        # 处理剩余查询
        if self.pending_queries:
            await self._execute_batch()

    async def _process_loop(self):
        """处理循环"""
        while True:
            try:
                await asyncio.sleep(self.timeout)

                async with self.lock:
                    if self.pending_queries:
                        await self._execute_batch()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"批处理循环错误: {e}")

    async def add_query(self, query: str, params: list[Any] | None = None) -> Any:
        """添加查询到批处理"""
        future = asyncio.Future()

        async with self.lock:
            self.pending_queries.append((query, params or [], future))

            if len(self.pending_queries) >= self.batch_size:
                await self._execute_batch()

        return await future

    async def _execute_batch(self):
        """批量执行查询"""
        if not self.pending_queries or not self._pool:
            return

        batch = self.pending_queries[: self.batch_size]
        self.pending_queries = self.pending_queries[self.batch_size :]

        # 使用事务批量执行
        async with self._pool.acquire() as conn, conn.transaction():
            for query, params, future in batch:
                try:
                    result = await conn.fetch(query, *params)
                    future.set_result(result)
                except Exception as e:
                    future.set_exception(e)


class PreparedStatementCache:
    """预处理语句缓存"""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: dict[str, asyncpg.PreparedStatement] = {}
        self.usage_count: dict[str, int] = {}

    async def get_or_prepare(
        self, conn: asyncpg.Connection, query: str
    ) -> asyncpg.PreparedStatement:
        """获取或准备语句"""
        if query in self.cache:
            self.usage_count[query] += 1
            return self.cache[query]

        # 缓存满了，移除最少使用的
        if len(self.cache) >= self.max_size:
            least_used = min(self.usage_count, key=self.usage_count.get)
            del self.cache[least_used]
            del self.usage_count[least_used]

        # 准备新语句
        stmt = await conn.prepare(query)
        self.cache[query] = stmt
        self.usage_count[query] = 1

        return stmt

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        return {
            "cache_size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": sum(c > 1 for c in self.usage_count.values())
            / len(self.usage_count)
            if self.usage_count
            else 0,
            "most_used": sorted(
                self.usage_count.items(), key=lambda x: x[1], reverse=True
              @cache(timeout=300)  # 5分钟缓存
  )[:10],
        }


# 装饰器：查询优化
def optimize_query(optimizer: QueryOptimizer):
    """
    查询优化装饰器

    自动分析查询性能并记录慢查询
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取连接对象（假设第一个参数是连接）
            conn = args[0] if args else kwargs.get("conn")

            if not conn:
                return await func(*args, **kwargs)

            # 获取查询语句（假设第二个参数是查询）
            query = args[1] if len(args) > 1 else kwargs.get("query", "")

            # 执行查询并分析
            start_time = time.time()
            result = await func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000  # 毫秒

            # 记录慢查询
            if execution_time > optimizer.slow_query_threshold:
                optimizer._record_slow_query(
                    query,
                    QueryPlan(
                        query=query,
                        execution_time=execution_time,
                        planning_time=0,
                        total_cost=0,
                        rows=0,
                        width=0,
                        plan_details={},
                    ),
                )

            return result

        return wrapper

    return decorator
