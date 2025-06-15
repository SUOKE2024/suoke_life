"""
数据库查询优化器

提供查询优化、索引管理和性能监控功能。
"""
import hashlib
import logging
import time
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

from internal.database.connection_manager import get_connection_manager
from internal.cache.redis_cache import get_redis_cache
from internal.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class QueryPlan:
    """查询执行计划"""
    query_hash: str
    sql: str
    execution_time: float
    rows_examined: int
    rows_returned: int
    index_used: bool
    cost_estimate: float
    plan_details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IndexRecommendation:
    """索引推荐"""
    table_name: str
    columns: List[str]
    index_type: str  # btree, hash, gin, gist
    reason: str
    estimated_benefit: float
    query_examples: List[str] = field(default_factory=list)


class QueryOptimizer:
    """查询优化器"""
    
    def __init__(self):
        self.db_manager = get_connection_manager()
        self.cache = get_redis_cache()
        self.query_plans: Dict[str, QueryPlan] = {}
        self.slow_queries: List[QueryPlan] = []
        self.index_recommendations: List[IndexRecommendation] = []
        self.query_cache_enabled = True
        self.slow_query_threshold = 1.0  # 1秒
        
        # 预定义的优化查询
        self.OPTIMIZED_QUERIES = {
            "get_user_by_username": """
                SELECT u.*, r.name as role_name 
                FROM users u 
                LEFT JOIN user_roles ur ON u.id = ur.user_id 
                LEFT JOIN roles r ON ur.role_id = r.id 
                WHERE u.username = $1 AND u.is_active = true
            """,
            "get_user_by_email": """
                SELECT u.*, r.name as role_name 
                FROM users u 
                LEFT JOIN user_roles ur ON u.id = ur.user_id 
                LEFT JOIN roles r ON ur.role_id = r.id 
                WHERE u.email = $1 AND u.is_active = true
            """,
            "get_user_permissions": """
                SELECT DISTINCT p.name 
                FROM users u
                JOIN user_roles ur ON u.id = ur.user_id
                JOIN roles r ON ur.role_id = r.id
                JOIN role_permissions rp ON r.id = rp.role_id
                JOIN permissions p ON rp.permission_id = p.id
                WHERE u.id = $1 AND u.is_active = true
            """,
            "get_active_sessions": """
                SELECT s.*, u.username 
                FROM user_sessions s 
                JOIN users u ON s.user_id = u.id 
                WHERE s.expires_at > NOW() 
                ORDER BY s.created_at DESC
            """,
            "get_login_attempts": """
                SELECT COUNT(*) as attempt_count, MAX(created_at) as last_attempt
                FROM login_attempts 
                WHERE identifier = $1 
                AND created_at > NOW() - INTERVAL '15 minutes'
            """
        }
        
        # 推荐的数据库索引
        self.RECOMMENDED_INDEXES = [
            {
                "name": "idx_users_username_active",
                "table": "users",
                "columns": ["username", "is_active"],
                "type": "btree",
                "sql": "CREATE INDEX CONCURRENTLY idx_users_username_active ON users (username, is_active) WHERE is_active = true;"
            },
            {
                "name": "idx_users_email_active", 
                "table": "users",
                "columns": ["email", "is_active"],
                "type": "btree",
                "sql": "CREATE INDEX CONCURRENTLY idx_users_email_active ON users (email, is_active) WHERE is_active = true;"
            },
            {
                "name": "idx_user_sessions_expires",
                "table": "user_sessions",
                "columns": ["expires_at"],
                "type": "btree",
                "sql": "CREATE INDEX CONCURRENTLY idx_user_sessions_expires ON user_sessions (expires_at) WHERE expires_at > NOW();"
            },
            {
                "name": "idx_user_sessions_user_id",
                "table": "user_sessions", 
                "columns": ["user_id"],
                "type": "btree",
                "sql": "CREATE INDEX CONCURRENTLY idx_user_sessions_user_id ON user_sessions (user_id);"
            },
            {
                "name": "idx_login_attempts_identifier_time",
                "table": "login_attempts",
                "columns": ["identifier", "created_at"],
                "type": "btree", 
                "sql": "CREATE INDEX CONCURRENTLY idx_login_attempts_identifier_time ON login_attempts (identifier, created_at);"
            },
            {
                "name": "idx_user_roles_user_id",
                "table": "user_roles",
                "columns": ["user_id"],
                "type": "btree",
                "sql": "CREATE INDEX CONCURRENTLY idx_user_roles_user_id ON user_roles (user_id);"
            },
            {
                "name": "idx_role_permissions_role_id",
                "table": "role_permissions", 
                "columns": ["role_id"],
                "type": "btree",
                "sql": "CREATE INDEX CONCURRENTLY idx_role_permissions_role_id ON role_permissions (role_id);"
            }
        ]
    
    async def execute_optimized_query(
        self,
        query_name: str,
        *args,
        use_cache: bool = True,
        cache_ttl: int = 300
    ) -> Any:
        """执行优化的查询"""
        if query_name not in self.OPTIMIZED_QUERIES:
            raise ValueError(f"未找到优化查询: {query_name}")
        
        sql = self.OPTIMIZED_QUERIES[query_name]
        query_hash = self._generate_query_hash(sql, args)
        
        # 尝试从缓存获取
        if use_cache and self.query_cache_enabled:
            cached_result = await self.cache.get_query_cache(query_hash)
            if cached_result is not None:
                logger.debug(f"查询缓存命中: {query_name}")
                return cached_result
        
        # 执行查询并记录性能
        start_time = time.time()
        
        try:
            result = await self.db_manager.execute_query(
                sql, *args, fetch_mode='all'
            )
            
            execution_time = time.time() - start_time
            
            # 记录查询计划
            await self._record_query_plan(query_hash, sql, execution_time, len(result) if result else 0)
            
            # 缓存结果
            if use_cache and self.query_cache_enabled:
                await self.cache.set_query_cache(query_hash, result, cache_ttl)
            
            logger.debug(f"查询执行完成: {query_name}, 耗时: {execution_time:.3f}秒")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"查询执行失败: {query_name}, 耗时: {execution_time:.3f}秒, 错误: {str(e)}")
            raise
    
    async def analyze_query_performance(self, sql: str, *args) -> QueryPlan:
        """分析查询性能"""
        query_hash = self._generate_query_hash(sql, args)
        
        try:
            # 获取查询执行计划
            explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {sql}"
            plan_result = await self.db_manager.execute_query(
                explain_sql, *args, fetch_mode='val'
            )
            
            if plan_result:
                plan_data = plan_result[0] if isinstance(plan_result, list) else plan_result
                
                # 解析执行计划
                execution_time = plan_data.get('Execution Time', 0) / 1000.0  # 转换为秒
                planning_time = plan_data.get('Planning Time', 0) / 1000.0
                total_time = execution_time + planning_time
                
                # 提取更多信息
                plan_node = plan_data.get('Plan', {})
                rows_examined = plan_node.get('Actual Rows', 0)
                cost_estimate = plan_node.get('Total Cost', 0)
                
                # 检查是否使用了索引
                index_used = self._check_index_usage(plan_node)
                
                query_plan = QueryPlan(
                    query_hash=query_hash,
                    sql=sql,
                    execution_time=total_time,
                    rows_examined=rows_examined,
                    rows_returned=rows_examined,  # 简化处理
                    index_used=index_used,
                    cost_estimate=cost_estimate,
                    plan_details=plan_data
                )
                
                # 记录慢查询
                if total_time > self.slow_query_threshold:
                    self.slow_queries.append(query_plan)
                    logger.warning(f"检测到慢查询: {total_time:.3f}秒, SQL: {sql[:100]}...")
                
                return query_plan
                
        except Exception as e:
            logger.error(f"查询性能分析失败: {str(e)}")
            # 返回基本的查询计划
            return QueryPlan(
                query_hash=query_hash,
                sql=sql,
                execution_time=0,
                rows_examined=0,
                rows_returned=0,
                index_used=False,
                cost_estimate=0
            )
    
    async def create_recommended_indexes(self, dry_run: bool = True) -> List[Dict[str, Any]]:
        """创建推荐的索引"""
        results = []
        
        for index_config in self.RECOMMENDED_INDEXES:
            try:
                # 检查索引是否已存在
                check_sql = """
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE tablename = $1 AND indexname = $2
                """
                existing = await self.db_manager.execute_query(
                    check_sql, 
                    index_config["table"], 
                    index_config["name"],
                    fetch_mode='one'
                )
                
                if existing:
                    results.append({
                        "index": index_config["name"],
                        "status": "already_exists",
                        "table": index_config["table"]
                    })
                    continue
                
                if not dry_run:
                    # 创建索引
                    await self.db_manager.execute_query(
                        index_config["sql"],
                        fetch_mode='execute'
                    )
                    
                    results.append({
                        "index": index_config["name"],
                        "status": "created",
                        "table": index_config["table"],
                        "sql": index_config["sql"]
                    })
                    
                    logger.info(f"创建索引成功: {index_config['name']}")
                else:
                    results.append({
                        "index": index_config["name"],
                        "status": "would_create",
                        "table": index_config["table"],
                        "sql": index_config["sql"]
                    })
                    
            except Exception as e:
                results.append({
                    "index": index_config["name"],
                    "status": "error",
                    "error": str(e),
                    "table": index_config["table"]
                })
                logger.error(f"创建索引失败 {index_config['name']}: {str(e)}")
        
        return results
    
    async def get_table_statistics(self) -> Dict[str, Any]:
        """获取表统计信息"""
        try:
            stats_sql = """
                SELECT 
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    n_live_tup as live_rows,
                    n_dead_tup as dead_rows,
                    last_vacuum,
                    last_autovacuum,
                    last_analyze,
                    last_autoanalyze
                FROM pg_stat_user_tables
                WHERE schemaname = 'public'
                ORDER BY n_live_tup DESC
            """
            
            tables = await self.db_manager.execute_query(stats_sql, fetch_mode='all')
            
            # 获取表大小信息
            size_sql = """
                SELECT 
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
                    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
                FROM pg_tables 
                WHERE schemaname = 'public'
            """
            
            sizes = await self.db_manager.execute_query(size_sql, fetch_mode='all')
            size_dict = {row['tablename']: row for row in sizes}
            
            # 合并统计信息
            result = {}
            for table in tables:
                table_name = table['tablename']
                result[table_name] = {
                    **dict(table),
                    **size_dict.get(table_name, {})
                }
            
            return result
            
        except Exception as e:
            logger.error(f"获取表统计信息失败: {str(e)}")
            return {}
    
    async def get_index_usage_stats(self) -> List[Dict[str, Any]]:
        """获取索引使用统计"""
        try:
            index_sql = """
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_tup_read,
                    idx_tup_fetch,
                    idx_scan,
                    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
                FROM pg_stat_user_indexes
                WHERE schemaname = 'public'
                ORDER BY idx_scan DESC
            """
            
            indexes = await self.db_manager.execute_query(index_sql, fetch_mode='all')
            return [dict(idx) for idx in indexes]
            
        except Exception as e:
            logger.error(f"获取索引使用统计失败: {str(e)}")
            return []
    
    async def optimize_table_maintenance(self) -> Dict[str, Any]:
        """优化表维护"""
        results = {
            "vacuum_recommendations": [],
            "analyze_recommendations": [],
            "reindex_recommendations": []
        }
        
        try:
            # 获取表统计信息
            table_stats = await self.get_table_statistics()
            
            for table_name, stats in table_stats.items():
                dead_rows = stats.get('dead_rows', 0)
                live_rows = stats.get('live_rows', 0)
                
                # VACUUM推荐
                if dead_rows > 0 and live_rows > 0:
                    dead_ratio = dead_rows / (live_rows + dead_rows)
                    if dead_ratio > 0.1:  # 超过10%的死行
                        results["vacuum_recommendations"].append({
                            "table": table_name,
                            "dead_rows": dead_rows,
                            "dead_ratio": round(dead_ratio * 100, 2),
                            "command": f"VACUUM ANALYZE {table_name};"
                        })
                
                # ANALYZE推荐
                last_analyze = stats.get('last_analyze') or stats.get('last_autoanalyze')
                if not last_analyze or (datetime.now() - last_analyze).days > 7:
                    results["analyze_recommendations"].append({
                        "table": table_name,
                        "last_analyze": last_analyze.isoformat() if last_analyze else None,
                        "command": f"ANALYZE {table_name};"
                    })
            
            # 检查需要重建的索引
            index_stats = await self.get_index_usage_stats()
            for index in index_stats:
                if index['idx_scan'] == 0 and index['indexname'] != f"{index['tablename']}_pkey":
                    results["reindex_recommendations"].append({
                        "index": index['indexname'],
                        "table": index['tablename'],
                        "reason": "未使用的索引",
                        "command": f"DROP INDEX {index['indexname']};"
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"表维护优化失败: {str(e)}")
            return results
    
    def _generate_query_hash(self, sql: str, args: tuple) -> str:
        """生成查询哈希"""
        query_string = f"{sql}:{':'.join(str(arg) for arg in args)}"
        return hashlib.md5(query_string.encode()).hexdigest()
    
    def _check_index_usage(self, plan_node: Dict[str, Any]) -> bool:
        """检查是否使用了索引"""
        node_type = plan_node.get('Node Type', '')
        
        # 检查当前节点
        if 'Index' in node_type:
            return True
        
        # 递归检查子节点
        plans = plan_node.get('Plans', [])
        for child_plan in plans:
            if self._check_index_usage(child_plan):
                return True
        
        return False
    
    async def _record_query_plan(
        self, 
        query_hash: str, 
        sql: str, 
        execution_time: float, 
        rows_returned: int
    ) -> None:
        """记录查询计划"""
        query_plan = QueryPlan(
            query_hash=query_hash,
            sql=sql,
            execution_time=execution_time,
            rows_examined=rows_returned,
            rows_returned=rows_returned,
            index_used=True,  # 简化处理
            cost_estimate=0
        )
        
        self.query_plans[query_hash] = query_plan
        
        # 记录慢查询
        if execution_time > self.slow_query_threshold:
            self.slow_queries.append(query_plan)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        total_queries = len(self.query_plans)
        slow_query_count = len(self.slow_queries)
        
        if total_queries == 0:
            return {
                "total_queries": 0,
                "slow_queries": 0,
                "slow_query_ratio": 0,
                "avg_execution_time": 0,
                "recommendations": []
            }
        
        avg_time = sum(plan.execution_time for plan in self.query_plans.values()) / total_queries
        slow_ratio = (slow_query_count / total_queries) * 100
        
        # 生成推荐
        recommendations = []
        if slow_query_count > 0:
            recommendations.append("考虑为慢查询添加索引")
        if slow_ratio > 10:
            recommendations.append("慢查询比例过高，需要优化查询")
        
        return {
            "total_queries": total_queries,
            "slow_queries": slow_query_count,
            "slow_query_ratio": round(slow_ratio, 2),
            "avg_execution_time": round(avg_time, 3),
            "slowest_queries": [
                {
                    "sql": plan.sql[:100] + "..." if len(plan.sql) > 100 else plan.sql,
                    "execution_time": round(plan.execution_time, 3),
                    "rows_examined": plan.rows_examined
                }
                for plan in sorted(self.slow_queries, key=lambda x: x.execution_time, reverse=True)[:5]
            ],
            "recommendations": recommendations
        }


# 全局查询优化器实例
_query_optimizer: Optional[QueryOptimizer] = None


def get_query_optimizer() -> QueryOptimizer:
    """获取查询优化器实例"""
    global _query_optimizer
    if _query_optimizer is None:
        _query_optimizer = QueryOptimizer()
    return _query_optimizer 