"""
事件存储实现
提供事件持久化、查询和溯源功能
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import asyncpg
import structlog
from .event_bus import Event

logger = structlog.get_logger(__name__)


class EventStore:
    """事件存储器"""
    
    def __init__(self, database_url: Optional[str] = None):
        """初始化事件存储"""
        self.database_url = database_url or "postgresql://suoke:suoke123@localhost:5432/suoke_db"
        self.pool: Optional[asyncpg.Pool] = None
        
    async def initialize(self) -> None:
        """初始化数据库连接池"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            
            # 创建事件表
            await self._create_tables()
            
            logger.info("事件存储初始化成功")
            
        except Exception as e:
            logger.error("事件存储初始化失败", error=str(e))
            raise
    
    async def close(self) -> None:
        """关闭连接池"""
        if self.pool:
            await self.pool.close()
            logger.info("事件存储连接已关闭")
    
    async def _create_tables(self) -> None:
        """创建事件存储表"""
        create_events_table = """
        CREATE TABLE IF NOT EXISTS events (
            id UUID PRIMARY KEY,
            type VARCHAR(255) NOT NULL,
            data JSONB NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            source VARCHAR(255) NOT NULL,
            correlation_id UUID,
            version VARCHAR(50) NOT NULL DEFAULT '1.0',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_events_type ON events(type);
        CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
        CREATE INDEX IF NOT EXISTS idx_events_source ON events(source);
        CREATE INDEX IF NOT EXISTS idx_events_correlation_id ON events(correlation_id);
        CREATE INDEX IF NOT EXISTS idx_events_data_gin ON events USING GIN(data);
        """
        
        create_event_snapshots_table = """
        CREATE TABLE IF NOT EXISTS event_snapshots (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            aggregate_id VARCHAR(255) NOT NULL,
            aggregate_type VARCHAR(255) NOT NULL,
            version INTEGER NOT NULL,
            data JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(aggregate_id, version)
        );
        
        CREATE INDEX IF NOT EXISTS idx_snapshots_aggregate ON event_snapshots(aggregate_id, aggregate_type);
        """
        
        async with self.pool.acquire() as conn:
            await conn.execute(create_events_table)
            await conn.execute(create_event_snapshots_table)
    
    async def save_event(self, event: Event) -> None:
        """保存事件"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO events (id, type, data, timestamp, source, correlation_id, version)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    event.id,
                    event.type,
                    json.dumps(event.data),
                    datetime.fromisoformat(event.timestamp.replace('Z', '+00:00')),
                    event.source,
                    event.correlation_id,
                    event.version
                )
            
            logger.debug("事件保存成功", event_id=event.id, event_type=event.type)
            
        except Exception as e:
            logger.error("事件保存失败", 
                        event_id=event.id,
                        event_type=event.type,
                        error=str(e))
            raise
    
    async def get_events(self, 
                        event_type: Optional[str] = None,
                        source: Optional[str] = None,
                        correlation_id: Optional[str] = None,
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None,
                        limit: int = 100,
                        offset: int = 0) -> List[Event]:
        """查询事件"""
        try:
            conditions = []
            params = []
            param_count = 0
            
            if event_type:
                param_count += 1
                conditions.append(f"type = ${param_count}")
                params.append(event_type)
            
            if source:
                param_count += 1
                conditions.append(f"source = ${param_count}")
                params.append(source)
            
            if correlation_id:
                param_count += 1
                conditions.append(f"correlation_id = ${param_count}")
                params.append(correlation_id)
            
            if start_time:
                param_count += 1
                conditions.append(f"timestamp >= ${param_count}")
                params.append(start_time)
            
            if end_time:
                param_count += 1
                conditions.append(f"timestamp <= ${param_count}")
                params.append(end_time)
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
            
            param_count += 1
            limit_clause = f"LIMIT ${param_count}"
            params.append(limit)
            
            param_count += 1
            offset_clause = f"OFFSET ${param_count}"
            params.append(offset)
            
            query = f"""
            SELECT id, type, data, timestamp, source, correlation_id, version
            FROM events
            {where_clause}
            ORDER BY timestamp DESC
            {limit_clause} {offset_clause}
            """
            
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
            
            events = []
            for row in rows:
                event = Event(
                    id=str(row['id']),
                    type=row['type'],
                    data=json.loads(row['data']),
                    timestamp=row['timestamp'].isoformat(),
                    source=row['source'],
                    correlation_id=str(row['correlation_id']) if row['correlation_id'] else None,
                    version=row['version']
                )
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error("事件查询失败", error=str(e))
            raise
    
    async def get_event_stream(self, correlation_id: str) -> List[Event]:
        """获取事件流（按关联ID）"""
        return await self.get_events(correlation_id=correlation_id, limit=1000)
    
    async def save_snapshot(self, aggregate_id: str, aggregate_type: str, 
                           version: int, data: Dict[str, Any]) -> None:
        """保存聚合快照"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO event_snapshots (aggregate_id, aggregate_type, version, data)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (aggregate_id, version) 
                    DO UPDATE SET data = EXCLUDED.data, created_at = NOW()
                    """,
                    aggregate_id,
                    aggregate_type,
                    version,
                    json.dumps(data)
                )
            
            logger.debug("快照保存成功", 
                        aggregate_id=aggregate_id,
                        aggregate_type=aggregate_type,
                        version=version)
            
        except Exception as e:
            logger.error("快照保存失败", 
                        aggregate_id=aggregate_id,
                        error=str(e))
            raise
    
    async def get_latest_snapshot(self, aggregate_id: str) -> Optional[Dict[str, Any]]:
        """获取最新快照"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT aggregate_type, version, data, created_at
                    FROM event_snapshots
                    WHERE aggregate_id = $1
                    ORDER BY version DESC
                    LIMIT 1
                    """,
                    aggregate_id
                )
            
            if row:
                return {
                    'aggregate_id': aggregate_id,
                    'aggregate_type': row['aggregate_type'],
                    'version': row['version'],
                    'data': json.loads(row['data']),
                    'created_at': row['created_at'].isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.error("快照查询失败", 
                        aggregate_id=aggregate_id,
                        error=str(e))
            raise
    
    async def cleanup_old_events(self, days: int = 90) -> int:
        """清理旧事件"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            async with self.pool.acquire() as conn:
                result = await conn.execute(
                    "DELETE FROM events WHERE timestamp < $1",
                    cutoff_date
                )
            
            deleted_count = int(result.split()[-1])
            
            logger.info("旧事件清理完成", 
                       deleted_count=deleted_count,
                       cutoff_date=cutoff_date.isoformat())
            
            return deleted_count
            
        except Exception as e:
            logger.error("事件清理失败", error=str(e))
            raise
    
    async def get_event_statistics(self) -> Dict[str, Any]:
        """获取事件统计信息"""
        try:
            async with self.pool.acquire() as conn:
                # 总事件数
                total_events = await conn.fetchval("SELECT COUNT(*) FROM events")
                
                # 按类型统计
                type_stats = await conn.fetch(
                    """
                    SELECT type, COUNT(*) as count
                    FROM events
                    GROUP BY type
                    ORDER BY count DESC
                    LIMIT 10
                    """
                )
                
                # 按来源统计
                source_stats = await conn.fetch(
                    """
                    SELECT source, COUNT(*) as count
                    FROM events
                    GROUP BY source
                    ORDER BY count DESC
                    LIMIT 10
                    """
                )
                
                # 最近24小时事件数
                recent_events = await conn.fetchval(
                    """
                    SELECT COUNT(*) FROM events
                    WHERE timestamp >= NOW() - INTERVAL '24 hours'
                    """
                )
            
            return {
                'total_events': total_events,
                'recent_24h_events': recent_events,
                'top_event_types': [dict(row) for row in type_stats],
                'top_sources': [dict(row) for row in source_stats]
            }
            
        except Exception as e:
            logger.error("事件统计查询失败", error=str(e))
            raise


# 全局事件存储实例
_global_event_store: Optional[EventStore] = None


def get_event_store() -> EventStore:
    """获取全局事件存储实例"""
    global _global_event_store
    if _global_event_store is None:
        _global_event_store = EventStore()
    return _global_event_store


async def initialize_event_store(database_url: Optional[str] = None) -> EventStore:
    """初始化全局事件存储"""
    global _global_event_store
    _global_event_store = EventStore(database_url)
    await _global_event_store.initialize()
    return _global_event_store 