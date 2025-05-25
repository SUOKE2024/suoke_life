#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
索儿智能体服务 - 会话存储库
提供用户与智能体的会话管理和持久化
"""

import uuid
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
import json

import motor.motor_asyncio
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError

from pkg.utils.config_loader import get_config
from pkg.utils.metrics import get_metrics_collector
from pkg.utils.dependency_injection import ServiceLifecycle
from pkg.utils.connection_pool import get_pool_manager, DatabaseConnectionPool, RedisConnectionPool
from pkg.utils.error_handling import DatabaseException, retry_async, RetryConfig

logger = logging.getLogger(__name__)
metrics = get_metrics_collector()

class SessionRepository(ServiceLifecycle):
    """会话仓储"""
    
    def __init__(self):
        self.db_pool: Optional[DatabaseConnectionPool] = None
        self.cache_pool: Optional[RedisConnectionPool] = None
        self.metrics = get_metrics_collector()
    
    async def start(self) -> None:
        """启动仓储"""
        try:
            pool_manager = get_pool_manager()
            self.db_pool = pool_manager.get_pool('database')
            self.cache_pool = pool_manager.get_pool('redis')
            
            # 确保数据库表存在
            await self._ensure_tables()
            
            logger.info("会话仓储启动成功")
            
        except Exception as e:
            logger.error(f"会话仓储启动失败: {e}")
            raise DatabaseException(f"会话仓储启动失败: {e}")
    
    async def stop(self) -> None:
        """停止仓储"""
        logger.info("会话仓储已停止")
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if not self.db_pool or not self.cache_pool:
                return False
            
            # 测试数据库连接
            async with self.db_pool.get_session() as session:
                await session.execute("SELECT 1")
            
            # 测试缓存连接
            await self.cache_pool.ping()
            
            return True
            
        except Exception as e:
            logger.error(f"会话仓储健康检查失败: {e}")
            return False
    
    async def _ensure_tables(self) -> None:
        """确保数据库表存在"""
        create_sessions_table = """
        CREATE TABLE IF NOT EXISTS sessions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id VARCHAR(255) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            status VARCHAR(50) DEFAULT 'active',
            metadata JSONB DEFAULT '{}',
            message_count INTEGER DEFAULT 0,
            INDEX idx_sessions_user_id (user_id),
            INDEX idx_sessions_status (status),
            INDEX idx_sessions_last_activity (last_activity)
        );
        """
        
        create_messages_table = """
        CREATE TABLE IF NOT EXISTS messages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
            role VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            metadata JSONB DEFAULT '{}',
            INDEX idx_messages_session_id (session_id),
            INDEX idx_messages_created_at (created_at),
            INDEX idx_messages_role (role)
        );
        """
        
        try:
            async with self.db_pool.get_session() as session:
                await session.execute(create_sessions_table)
                await session.execute(create_messages_table)
                await session.commit()
                
            logger.info("数据库表检查完成")
            
        except Exception as e:
            logger.error(f"创建数据库表失败: {e}")
            raise DatabaseException(f"创建数据库表失败: {e}")
    
    @retry_async(RetryConfig(max_attempts=3, base_delay=1.0))
    async def create_session(self, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        
        try:
            # 记录指标
            self.metrics.increment_counter("soer_db_queries", {"operation": "insert", "table": "sessions"})
            
            with self.metrics.timer("soer_db_query_duration", {"operation": "insert", "table": "sessions"}):
                async with self.db_pool.get_session() as db_session:
                    query = """
                    INSERT INTO sessions (id, user_id, metadata)
                    VALUES (:session_id, :user_id, :metadata)
                    """
                    
                    await db_session.execute(query, {
                        "session_id": session_id,
                        "user_id": user_id,
                        "metadata": json.dumps(metadata or {})
                    })
                    await db_session.commit()
            
            # 缓存会话信息
            await self._cache_session_info(session_id, {
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "metadata": metadata or {}
            })
            
            logger.info(f"创建会话成功: {session_id} (用户: {user_id})")
            return session_id
            
        except Exception as e:
            logger.error(f"创建会话失败: {e}")
            raise DatabaseException(f"创建会话失败: {e}")
    
    @retry_async(RetryConfig(max_attempts=3, base_delay=1.0))
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        try:
            # 先从缓存获取
            cached_session = await self._get_cached_session_info(session_id)
            if cached_session:
                return cached_session
            
            # 从数据库获取
            self.metrics.increment_counter("soer_db_queries", {"operation": "select", "table": "sessions"})
            
            with self.metrics.timer("soer_db_query_duration", {"operation": "select", "table": "sessions"}):
                async with self.db_pool.get_session() as db_session:
                    query = """
                    SELECT id, user_id, created_at, updated_at, last_activity, 
                           status, metadata, message_count
                    FROM sessions 
                    WHERE id = :session_id
                    """
                    
                    result = await db_session.execute(query, {"session_id": session_id})
                    row = result.fetchone()
            
            if not row:
                return None
            
            session_info = {
                "id": str(row.id),
                "user_id": row.user_id,
                "created_at": row.created_at.isoformat(),
                "updated_at": row.updated_at.isoformat(),
                "last_activity": row.last_activity.isoformat(),
                "status": row.status,
                "metadata": json.loads(row.metadata) if row.metadata else {},
                "message_count": row.message_count
            }
            
            # 缓存结果
            await self._cache_session_info(session_id, session_info)
            
            return session_info
            
        except Exception as e:
            logger.error(f"获取会话失败: {e}")
            raise DatabaseException(f"获取会话失败: {e}")
    
    @retry_async(RetryConfig(max_attempts=3, base_delay=1.0))
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """更新会话信息"""
        try:
            self.metrics.increment_counter("soer_db_queries", {"operation": "update", "table": "sessions"})
            
            # 构建更新查询
            set_clauses = []
            params = {"session_id": session_id}
            
            for key, value in updates.items():
                if key in ["status", "metadata", "message_count"]:
                    set_clauses.append(f"{key} = :{key}")
                    if key == "metadata":
                        params[key] = json.dumps(value)
                    else:
                        params[key] = value
            
            if not set_clauses:
                return True
            
            set_clauses.append("updated_at = NOW()")
            set_clauses.append("last_activity = NOW()")
            
            query = f"""
            UPDATE sessions 
            SET {', '.join(set_clauses)}
            WHERE id = :session_id
            """
            
            with self.metrics.timer("soer_db_query_duration", {"operation": "update", "table": "sessions"}):
                async with self.db_pool.get_session() as db_session:
                    result = await db_session.execute(query, params)
                    await db_session.commit()
            
            # 清除缓存
            await self._clear_cached_session_info(session_id)
            
            return result.rowcount > 0
            
        except Exception as e:
            logger.error(f"更新会话失败: {e}")
            raise DatabaseException(f"更新会话失败: {e}")
    
    @retry_async(RetryConfig(max_attempts=3, base_delay=1.0))
    async def save_message(
        self, 
        session_id: str, 
        role: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """保存消息"""
        message_id = str(uuid.uuid4())
        
        try:
            self.metrics.increment_counter("soer_db_queries", {"operation": "insert", "table": "messages"})
            
            with self.metrics.timer("soer_db_query_duration", {"operation": "insert", "table": "messages"}):
                async with self.db_pool.get_session() as db_session:
                    # 插入消息
                    insert_query = """
                    INSERT INTO messages (id, session_id, role, content, metadata)
                    VALUES (:message_id, :session_id, :role, :content, :metadata)
                    """
                    
                    await db_session.execute(insert_query, {
                        "message_id": message_id,
                        "session_id": session_id,
                        "role": role,
                        "content": content,
                        "metadata": json.dumps(metadata or {})
                    })
                    
                    # 更新会话消息计数
                    update_query = """
                    UPDATE sessions 
                    SET message_count = message_count + 1, 
                        last_activity = NOW(),
                        updated_at = NOW()
                    WHERE id = :session_id
                    """
                    
                    await db_session.execute(update_query, {"session_id": session_id})
                    await db_session.commit()
            
            # 清除会话缓存
            await self._clear_cached_session_info(session_id)
            
            logger.debug(f"保存消息成功: {message_id} (会话: {session_id})")
            return message_id
            
        except Exception as e:
            logger.error(f"保存消息失败: {e}")
            raise DatabaseException(f"保存消息失败: {e}")
    
    @retry_async(RetryConfig(max_attempts=3, base_delay=1.0))
    async def get_latest_messages(
        self, 
        session_id: str, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取最新消息"""
        try:
            self.metrics.increment_counter("soer_db_queries", {"operation": "select", "table": "messages"})
            
            with self.metrics.timer("soer_db_query_duration", {"operation": "select", "table": "messages"}):
                async with self.db_pool.get_session() as db_session:
                    query = """
                    SELECT id, role, content, created_at, metadata
                    FROM messages 
                    WHERE session_id = :session_id
                    ORDER BY created_at DESC
                    LIMIT :limit
                    """
                    
                    result = await db_session.execute(query, {
                        "session_id": session_id,
                        "limit": limit
                    })
                    rows = result.fetchall()
            
            messages = []
            for row in reversed(rows):  # 反转以获得时间顺序
                messages.append({
                    "id": str(row.id),
                    "role": row.role,
                    "content": row.content,
                    "created_at": row.created_at.isoformat(),
                    "metadata": json.loads(row.metadata) if row.metadata else {}
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"获取消息失败: {e}")
            raise DatabaseException(f"获取消息失败: {e}")
    
    @retry_async(RetryConfig(max_attempts=3, base_delay=1.0))
    async def get_user_sessions(
        self, 
        user_id: str, 
        limit: int = 50,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取用户会话列表"""
        try:
            self.metrics.increment_counter("soer_db_queries", {"operation": "select", "table": "sessions"})
            
            # 构建查询
            where_clause = "WHERE user_id = :user_id"
            params = {"user_id": user_id, "limit": limit}
            
            if status:
                where_clause += " AND status = :status"
                params["status"] = status
            
            query = f"""
            SELECT id, user_id, created_at, updated_at, last_activity, 
                   status, metadata, message_count
            FROM sessions 
            {where_clause}
            ORDER BY last_activity DESC
            LIMIT :limit
            """
            
            with self.metrics.timer("soer_db_query_duration", {"operation": "select", "table": "sessions"}):
                async with self.db_pool.get_session() as db_session:
                    result = await db_session.execute(query, params)
                    rows = result.fetchall()
            
            sessions = []
            for row in rows:
                sessions.append({
                    "id": str(row.id),
                    "user_id": row.user_id,
                    "created_at": row.created_at.isoformat(),
                    "updated_at": row.updated_at.isoformat(),
                    "last_activity": row.last_activity.isoformat(),
                    "status": row.status,
                    "metadata": json.loads(row.metadata) if row.metadata else {},
                    "message_count": row.message_count
                })
            
            return sessions
            
        except Exception as e:
            logger.error(f"获取用户会话失败: {e}")
            raise DatabaseException(f"获取用户会话失败: {e}")
    
    @retry_async(RetryConfig(max_attempts=3, base_delay=1.0))
    async def delete_expired_sessions(self, days: int = 90) -> int:
        """删除过期会话"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            self.metrics.increment_counter("soer_db_queries", {"operation": "delete", "table": "sessions"})
            
            with self.metrics.timer("soer_db_query_duration", {"operation": "delete", "table": "sessions"}):
                async with self.db_pool.get_session() as db_session:
                    query = """
                    DELETE FROM sessions 
                    WHERE last_activity < :cutoff_date
                    """
                    
                    result = await db_session.execute(query, {"cutoff_date": cutoff_date})
                    await db_session.commit()
            
            deleted_count = result.rowcount
            logger.info(f"删除了{deleted_count}个过期会话")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"删除过期会话失败: {e}")
            raise DatabaseException(f"删除过期会话失败: {e}")
    
    async def get_session_count(self) -> int:
        """获取会话总数"""
        try:
            self.metrics.increment_counter("soer_db_queries", {"operation": "select", "table": "sessions"})
            
            with self.metrics.timer("soer_db_query_duration", {"operation": "select", "table": "sessions"}):
                async with self.db_pool.get_session() as db_session:
                    query = "SELECT COUNT(*) as count FROM sessions"
                    result = await db_session.execute(query)
                    row = result.fetchone()
            
            return row.count if row else 0
            
        except Exception as e:
            logger.error(f"获取会话计数失败: {e}")
            return 0
    
    # 缓存相关方法
    async def _cache_session_info(self, session_id: str, session_info: Dict[str, Any]) -> None:
        """缓存会话信息"""
        try:
            cache_key = f"session:{session_id}"
            cache_data = json.dumps(session_info, ensure_ascii=False)
            await self.cache_pool.set(cache_key, cache_data, ttl=3600)  # 缓存1小时
        except Exception as e:
            logger.warning(f"缓存会话信息失败: {e}")
    
    async def _get_cached_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取缓存的会话信息"""
        try:
            cache_key = f"session:{session_id}"
            cached_data = await self.cache_pool.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.warning(f"获取缓存会话信息失败: {e}")
            return None
    
    async def _clear_cached_session_info(self, session_id: str) -> None:
        """清除缓存的会话信息"""
        try:
            cache_key = f"session:{session_id}"
            await self.cache_pool.delete(cache_key)
        except Exception as e:
            logger.warning(f"清除缓存会话信息失败: {e}") 