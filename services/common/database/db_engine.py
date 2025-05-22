"""
索克生活APP数据库引擎模块

提供统一的数据库连接和操作接口，支持：
1. 连接池管理
2. 读写分离
3. 慢查询监控
4. 分布式追踪集成
5. 数据库健康检查
"""

import asyncio
import logging
import random
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union, Callable

import yaml
from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.engine import Engine, Connection, Row
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    AsyncEngine, 
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool
from opentelemetry import trace
from opentelemetry.trace import Span

# 支持的数据库类型
class DatabaseType:
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"

# 读写分离模式
class ReplicaStrategy:
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    LEAST_CONNECTIONS = "least_connections"

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

class DatabaseEngine:
    """数据库引擎，管理连接池和提供数据库操作接口"""
    
    def __init__(self, config_path: str):
        """
        初始化数据库引擎
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.primary_engine = None  # 主数据库引擎
        self.replica_engines = []   # 只读副本引擎
        self.current_replica = 0    # 当前使用的副本索引（轮询策略）
        self._setup_engines()
        self.connection_counts = {}  # 各引擎的连接数记录
        self.slow_queries = []      # 慢查询记录
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            return config.get("database", {})
        except Exception as e:
            logger.error(f"加载数据库配置文件失败: {str(e)}")
            # 返回默认配置
            return {
                "primary": {
                    "type": "postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "username": "postgres",
                    "password": "postgres",
                    "database": "app_db",
                    "pool": {"max_size": 10}
                }
            }
    
    def _setup_engines(self):
        """设置数据库引擎"""
        # 主数据库引擎
        primary_config = self.config.get("primary", {})
        db_type = primary_config.get("type", DatabaseType.POSTGRESQL)
        
        # 构建连接URL
        if db_type == DatabaseType.SQLITE:
            db_path = primary_config.get("path", "app.db")
            sync_url = f"sqlite:///{db_path}"
            async_url = f"sqlite+aiosqlite:///{db_path}"
        else:
            host = primary_config.get("host", "localhost")
            port = primary_config.get("port", 5432 if db_type == DatabaseType.POSTGRESQL else 3306)
            username = primary_config.get("username", "postgres")
            password = primary_config.get("password", "postgres")
            database = primary_config.get("database", "app_db")
            
            if db_type == DatabaseType.POSTGRESQL:
                sync_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
                async_url = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
            elif db_type == DatabaseType.MYSQL:
                sync_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
                async_url = f"mysql+aiomysql://{username}:{password}@{host}:{port}/{database}"
        
        # 获取连接池配置
        pool_config = primary_config.get("pool", {})
        pool_size = pool_config.get("max_size", 20)
        max_overflow = pool_config.get("max_overflow", 10)
        pool_timeout = pool_config.get("timeout", 30)
        pool_recycle = pool_config.get("recycle", 3600)
        
        # 设置引擎参数
        engine_options = {
            "pool_size": pool_size,
            "max_overflow": max_overflow,
            "pool_timeout": pool_timeout,
            "pool_recycle": pool_recycle,
            "pool_pre_ping": True,
            "echo": pool_config.get("echo", False),
        }
        
        # 性能优化参数
        optimization = primary_config.get("optimization", {})
        connect_args = {}
        
        if db_type == DatabaseType.POSTGRESQL:
            connect_args = {
                "statement_timeout": optimization.get("statement_timeout", 30000),
                "application_name": primary_config.get("options", {}).get("application_name", "suoke_app"),
                "client_encoding": primary_config.get("options", {}).get("client_encoding", "UTF8"),
                "connect_timeout": primary_config.get("options", {}).get("connect_timeout", 10),
                "options": "-c statement_timeout=30s -c idle_in_transaction_session_timeout=60s",
            }
        elif db_type == DatabaseType.SQLITE:
            sqlite_config = self.config.get("sqlite", {})
            connect_args = {
                "timeout": sqlite_config.get("busy_timeout", 5000) / 1000,  # 转换为秒
                "isolation_level": None,  # 允许控制事务
                "check_same_thread": False,
            }
        
        engine_options["connect_args"] = connect_args
        
        # 创建同步引擎
        self.primary_engine = create_engine(sync_url, **engine_options)
        
        # 创建异步引擎
        self.async_primary_engine = create_async_engine(async_url, **engine_options)
        
        # 创建会话工厂
        self.session_factory = sessionmaker(
            bind=self.primary_engine, 
            expire_on_commit=False,
            autoflush=False,
        )
        
        self.async_session_factory = async_sessionmaker(
            bind=self.async_primary_engine,
            expire_on_commit=False,
            autoflush=False,
        )
        
        # 设置只读副本引擎
        replica_config = self.config.get("replicas", {})
        if replica_config.get("enabled", False):
            self.replica_strategy = replica_config.get("strategy", ReplicaStrategy.ROUND_ROBIN)
            replica_nodes = replica_config.get("nodes", [])
            
            for node in replica_nodes:
                if not node.get("host"):
                    continue
                    
                host = node.get("host")
                port = node.get("port", 5432 if db_type == DatabaseType.POSTGRESQL else 3306)
                username = node.get("username", "postgres")
                password = node.get("password", "postgres")
                database = node.get("database", "app_db")
                
                # 复制主数据库的连接池配置，但使用节点特定的设置
                node_pool = node.get("pool", {})
                node_pool_size = node_pool.get("max_size", pool_size // 2)
                node_max_overflow = node_pool.get("max_overflow", max_overflow // 2)
                node_pool_timeout = node_pool.get("timeout", pool_timeout)
                
                node_engine_options = {
                    "pool_size": node_pool_size,
                    "max_overflow": node_max_overflow,
                    "pool_timeout": node_pool_timeout,
                    "pool_recycle": pool_recycle,
                    "pool_pre_ping": True,
                    "echo": pool_config.get("echo", False),
                    "connect_args": connect_args.copy()
                }
                
                # 为只读连接设置只读模式
                if db_type == DatabaseType.POSTGRESQL:
                    node_engine_options["connect_args"]["options"] += " -c default_transaction_read_only=on"
                
                # 构建只读副本URL
                if db_type == DatabaseType.POSTGRESQL:
                    replica_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
                    async_replica_url = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
                elif db_type == DatabaseType.MYSQL:
                    replica_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
                    async_replica_url = f"mysql+aiomysql://{username}:{password}@{host}:{port}/{database}"
                else:
                    # SQLite不支持只读副本
                    continue
                
                # 创建同步引擎
                replica_engine = create_engine(replica_url, **node_engine_options)
                
                # 创建异步引擎
                async_replica_engine = create_async_engine(async_replica_url, **node_engine_options)
                
                # 添加到副本列表
                self.replica_engines.append({
                    "sync": replica_engine,
                    "async": async_replica_engine,
                    "connections": 0
                })
    
    def get_session(self) -> Session:
        """获取主数据库会话（写操作）"""
        return self.session_factory()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncSession:
        """获取异步主数据库会话（写操作）"""
        session = self.async_session_factory()
        try:
            yield session
        finally:
            await session.close()
    
    def get_read_engine(self) -> Engine:
        """获取只读数据库引擎（读操作）"""
        if not self.replica_engines:
            return self.primary_engine
            
        # 根据策略选择副本
        if self.replica_strategy == ReplicaStrategy.RANDOM:
            # 随机策略
            idx = random.randint(0, len(self.replica_engines) - 1)
            replica = self.replica_engines[idx]
            replica["connections"] += 1
            return replica["sync"]
            
        elif self.replica_strategy == ReplicaStrategy.LEAST_CONNECTIONS:
            # 最少连接策略
            min_connections = float('inf')
            selected_idx = 0
            
            for i, replica in enumerate(self.replica_engines):
                if replica["connections"] < min_connections:
                    min_connections = replica["connections"]
                    selected_idx = i
            
            self.replica_engines[selected_idx]["connections"] += 1
            return self.replica_engines[selected_idx]["sync"]
            
        else:
            # 默认轮询策略
            idx = self.current_replica
            self.current_replica = (self.current_replica + 1) % len(self.replica_engines)
            self.replica_engines[idx]["connections"] += 1
            return self.replica_engines[idx]["sync"]
    
    async def get_async_read_engine(self) -> AsyncEngine:
        """获取异步只读数据库引擎（读操作）"""
        if not self.replica_engines:
            return self.async_primary_engine
            
        # 与同步版本相同的选择逻辑
        if self.replica_strategy == ReplicaStrategy.RANDOM:
            idx = random.randint(0, len(self.replica_engines) - 1)
            replica = self.replica_engines[idx]
            replica["connections"] += 1
            return replica["async"]
            
        elif self.replica_strategy == ReplicaStrategy.LEAST_CONNECTIONS:
            min_connections = float('inf')
            selected_idx = 0
            
            for i, replica in enumerate(self.replica_engines):
                if replica["connections"] < min_connections:
                    min_connections = replica["connections"]
                    selected_idx = i
            
            self.replica_engines[selected_idx]["connections"] += 1
            return self.replica_engines[selected_idx]["async"]
            
        else:
            idx = self.current_replica
            self.current_replica = (self.current_replica + 1) % len(self.replica_engines)
            self.replica_engines[idx]["connections"] += 1
            return self.replica_engines[idx]["async"]
    
    @asynccontextmanager
    async def get_read_session(self) -> AsyncSession:
        """获取只读会话"""
        read_engine = await self.get_async_read_engine()
        session_factory = async_sessionmaker(bind=read_engine, expire_on_commit=False, autoflush=False)
        session = session_factory()
        try:
            yield session
        finally:
            await session.close()
    
    @tracer.start_as_current_span("db_execute_query")
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None, 
                           is_read_query: bool = True) -> List[Dict[str, Any]]:
        """
        执行SQL查询，自动选择读/写引擎
        
        Args:
            query: SQL查询语句
            params: 查询参数
            is_read_query: 是否为只读查询
        
        Returns:
            查询结果列表
        """
        start_time = time.time()
        span = trace.get_current_span()
        
        span.set_attribute("db.statement", query)
        span.set_attribute("db.operation", "read" if is_read_query else "write")
        
        if params:
            span.set_attribute("db.params", str(params))
        
        try:
            if is_read_query:
                engine = await self.get_async_read_engine()
            else:
                engine = self.async_primary_engine
                
            async with engine.connect() as conn:
                result = await conn.execute(text(query), params or {})
                rows = result.fetchall()
                
                # 转换为字典列表
                result_dicts = [dict(row._mapping) for row in rows]
                
                # 记录查询时间
                query_time = (time.time() - start_time) * 1000  # 毫秒
                span.set_attribute("db.query.time_ms", query_time)
                
                # 检查是否为慢查询
                slow_threshold = self.config.get("monitoring", {}).get("slow_query_threshold", 500)
                if query_time > slow_threshold:
                    self._record_slow_query(query, params, query_time)
                
                return result_dicts
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            logger.error(f"执行查询失败: {str(e)}")
            raise
    
    def _record_slow_query(self, query: str, params: Optional[Dict[str, Any]], query_time: float):
        """记录慢查询"""
        slow_query = {
            "query": query,
            "params": params,
            "time_ms": query_time,
            "timestamp": time.time()
        }
        
        self.slow_queries.append(slow_query)
        logger.warning(f"检测到慢查询: {query_time:.2f}ms, SQL: {query}")
        
        # 限制慢查询记录数量
        max_slow_queries = self.config.get("monitoring", {}).get("max_slow_queries", 100)
        if len(self.slow_queries) > max_slow_queries:
            self.slow_queries = self.slow_queries[-max_slow_queries:]
    
    async def get_slow_queries(self) -> List[Dict[str, Any]]:
        """获取慢查询记录"""
        return self.slow_queries
    
    async def check_health(self) -> Dict[str, Any]:
        """检查数据库健康状态"""
        result = {
            "status": "UP",
            "details": {
                "primary": {
                    "status": "UNKNOWN",
                    "response_time_ms": 0
                },
                "replicas": []
            }
        }
        
        # 检查主数据库
        try:
            start_time = time.time()
            async with self.async_primary_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                primary_response_time = (time.time() - start_time) * 1000
                
                result["details"]["primary"] = {
                    "status": "UP",
                    "response_time_ms": primary_response_time
                }
        except Exception as e:
            result["status"] = "DOWN"
            result["details"]["primary"] = {
                "status": "DOWN",
                "error": str(e)
            }
        
        # 检查副本数据库
        replica_statuses = []
        for i, replica in enumerate(self.replica_engines):
            replica_status = {"id": i, "status": "UNKNOWN"}
            
            try:
                start_time = time.time()
                async with replica["async"].connect() as conn:
                    await conn.execute(text("SELECT 1"))
                    replica_response_time = (time.time() - start_time) * 1000
                    
                    replica_status = {
                        "id": i,
                        "status": "UP",
                        "response_time_ms": replica_response_time
                    }
            except Exception as e:
                replica_status = {
                    "id": i,
                    "status": "DOWN",
                    "error": str(e)
                }
                # 如果所有副本都故障，仍然允许系统运行（降级到主库）
            
            replica_statuses.append(replica_status)
        
        result["details"]["replicas"] = replica_statuses
        
        # 如果主数据库故障，整体状态标记为DOWN
        if result["details"]["primary"]["status"] == "DOWN":
            result["status"] = "DOWN"
        
        return result
    
    def close(self):
        """关闭所有数据库连接"""
        if self.primary_engine:
            self.primary_engine.dispose()
        
        for replica in self.replica_engines:
            replica["sync"].dispose()
    
    async def close_async(self):
        """关闭所有异步数据库连接"""
        if self.async_primary_engine:
            await self.async_primary_engine.dispose()
        
        for replica in self.replica_engines:
            await replica["async"].dispose() 