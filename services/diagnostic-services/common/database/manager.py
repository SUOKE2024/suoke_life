"""
数据库管理器

提供数据库连接、会话管理、事务处理、数据访问等核心功能，
支持异步操作和连接池管理。
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List, AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, event
from sqlalchemy.pool import QueuePool
import redis.asyncio as redis
from datetime import datetime, timedelta
import json
import uuid

from .models import Base, Patient, DiagnosisSession, SystemLog, PerformanceMetric
from ..config.settings import get_settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.engine = None
        self.async_session_factory = None
        self.redis_client = None
        self._initialized = False
    
    async def initialize(self):
        """初始化数据库连接"""
        if self._initialized:
            return
        
        try:
            # 创建异步数据库引擎
            database_url = self._build_database_url()
            self.engine = create_async_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=self.settings.database.echo_sql,
                future=True
            )
            
            # 创建会话工厂
            self.async_session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # 初始化Redis连接
            await self._initialize_redis()
            
            # 创建数据库表
            await self._create_tables()
            
            # 设置数据库事件监听
            self._setup_database_events()
            
            self._initialized = True
            logger.info("数据库管理器初始化完成")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def _build_database_url(self) -> str:
        """构建数据库连接URL"""
        db_config = self.settings.database
        return (
            f"postgresql+asyncpg://{db_config.username}:{db_config.password}"
            f"@{db_config.host}:{db_config.port}/{db_config.database}"
        )
    
    async def _initialize_redis(self):
        """初始化Redis连接"""
        try:
            redis_config = self.settings.redis
            self.redis_client = redis.Redis(
                host=redis_config.host,
                port=redis_config.port,
                password=redis_config.password,
                db=redis_config.database,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                max_connections=20
            )
            
            # 测试连接
            await self.redis_client.ping()
            logger.info("Redis连接初始化完成")
            
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}")
            self.redis_client = None
    
    async def _create_tables(self):
        """创建数据库表"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("数据库表创建完成")
        except Exception as e:
            logger.error(f"创建数据库表失败: {e}")
            raise
    
    def _setup_database_events(self):
        """设置数据库事件监听"""
        @event.listens_for(self.engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """设置数据库连接参数"""
            if "postgresql" in str(dbapi_connection):
                with dbapi_connection.cursor() as cursor:
                    cursor.execute("SET timezone = 'UTC'")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取数据库会话"""
        if not self._initialized:
            await self.initialize()
        
        async with self.async_session_factory() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error(f"数据库会话错误: {e}")
                raise
            finally:
                await session.close()
    
    @asynccontextmanager
    async def get_transaction(self) -> AsyncGenerator[AsyncSession, None]:
        """获取事务会话"""
        async with self.get_session() as session:
            async with session.begin():
                yield session
    
    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict]:
        """执行查询"""
        async with self.get_session() as session:
            result = await session.execute(text(query), params or {})
            return [dict(row._mapping) for row in result.fetchall()]
    
    async def execute_command(self, command: str, params: Dict[str, Any] = None) -> int:
        """执行命令"""
        async with self.get_transaction() as session:
            result = await session.execute(text(command), params or {})
            return result.rowcount
    
    async def close(self):
        """关闭数据库连接"""
        if self.engine:
            await self.engine.dispose()
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("数据库连接已关闭")

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, redis_client: redis.Redis = None):
        self.redis_client = redis_client
        self.local_cache = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    async def get(self, key: str, default: Any = None) -> Any:
        """获取缓存值"""
        try:
            # 先尝试Redis
            if self.redis_client:
                value = await self.redis_client.get(key)
                if value is not None:
                    self.cache_stats["hits"] += 1
                    return json.loads(value)
            
            # 再尝试本地缓存
            if key in self.local_cache:
                entry = self.local_cache[key]
                if entry["expires_at"] > datetime.utcnow():
                    self.cache_stats["hits"] += 1
                    return entry["value"]
                else:
                    del self.local_cache[key]
            
            self.cache_stats["misses"] += 1
            return default
            
        except Exception as e:
            logger.error(f"缓存获取失败: {e}")
            return default
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """设置缓存值"""
        try:
            serialized_value = json.dumps(value, default=str)
            
            # 设置Redis缓存
            if self.redis_client:
                await self.redis_client.setex(key, ttl, serialized_value)
            
            # 设置本地缓存
            self.local_cache[key] = {
                "value": value,
                "expires_at": datetime.utcnow() + timedelta(seconds=ttl)
            }
            
            self.cache_stats["sets"] += 1
            
        except Exception as e:
            logger.error(f"缓存设置失败: {e}")
    
    async def delete(self, key: str):
        """删除缓存"""
        try:
            # 删除Redis缓存
            if self.redis_client:
                await self.redis_client.delete(key)
            
            # 删除本地缓存
            if key in self.local_cache:
                del self.local_cache[key]
            
            self.cache_stats["deletes"] += 1
            
        except Exception as e:
            logger.error(f"缓存删除失败: {e}")
    
    async def clear(self, pattern: str = None):
        """清空缓存"""
        try:
            if self.redis_client:
                if pattern:
                    keys = await self.redis_client.keys(pattern)
                    if keys:
                        await self.redis_client.delete(*keys)
                else:
                    await self.redis_client.flushdb()
            
            # 清空本地缓存
            if pattern:
                keys_to_delete = [k for k in self.local_cache.keys() if pattern in k]
                for key in keys_to_delete:
                    del self.local_cache[key]
            else:
                self.local_cache.clear()
                
        except Exception as e:
            logger.error(f"缓存清空失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = self.cache_stats["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            **self.cache_stats,
            "hit_rate": hit_rate,
            "local_cache_size": len(self.local_cache)
        }

class DataAccessLayer:
    """数据访问层"""
    
    def __init__(self, db_manager: DatabaseManager, cache_manager: CacheManager):
        self.db = db_manager
        self.cache = cache_manager
    
    async def create_patient(self, patient_data: Dict[str, Any]) -> str:
        """创建患者"""
        async with self.db.get_transaction() as session:
            patient = Patient(**patient_data)
            session.add(patient)
            await session.flush()
            
            # 清除相关缓存
            await self.cache.delete(f"patient:{patient.id}")
            
            return str(patient.id)
    
    async def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """获取患者信息"""
        cache_key = f"patient:{patient_id}"
        
        # 尝试从缓存获取
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # 从数据库获取
        async with self.db.get_session() as session:
            patient = await session.get(Patient, patient_id)
            if patient:
                patient_data = {
                    "id": str(patient.id),
                    "name": patient.name,
                    "gender": patient.gender,
                    "age": patient.age,
                    "birth_date": patient.birth_date.isoformat() if patient.birth_date else None,
                    "constitution_type": patient.constitution_type,
                    "medical_history": patient.medical_history,
                    "created_at": patient.created_at.isoformat()
                }
                
                # 缓存结果
                await self.cache.set(cache_key, patient_data, ttl=1800)
                return patient_data
        
        return None
    
    async def create_diagnosis_session(self, session_data: Dict[str, Any]) -> str:
        """创建诊断会话"""
        async with self.db.get_transaction() as session:
            diagnosis_session = DiagnosisSession(**session_data)
            session.add(diagnosis_session)
            await session.flush()
            
            return str(diagnosis_session.id)
    
    async def get_diagnosis_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取诊断会话"""
        cache_key = f"session:{session_id}"
        
        # 尝试从缓存获取
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # 从数据库获取
        async with self.db.get_session() as session:
            diagnosis_session = await session.get(DiagnosisSession, session_id)
            if diagnosis_session:
                session_data = {
                    "id": str(diagnosis_session.id),
                    "patient_id": str(diagnosis_session.patient_id),
                    "session_type": diagnosis_session.session_type,
                    "status": diagnosis_session.status,
                    "tcm_diagnosis": diagnosis_session.tcm_diagnosis,
                    "syndrome_pattern": diagnosis_session.syndrome_pattern,
                    "confidence_score": diagnosis_session.confidence_score,
                    "created_at": diagnosis_session.created_at.isoformat()
                }
                
                # 缓存结果
                await self.cache.set(cache_key, session_data, ttl=900)
                return session_data
        
        return None
    
    async def save_analysis_result(self, analysis_type: str, result_data: Dict[str, Any]) -> str:
        """保存分析结果"""
        async with self.db.get_transaction() as session:
            # 根据分析类型选择对应的模型
            model_mapping = {
                "look": "LookAnalysis",
                "listen": "ListenAnalysis", 
                "inquiry": "InquiryAnalysis",
                "palpation": "PalpationAnalysis",
                "calculation": "CalculationAnalysis"
            }
            
            model_name = model_mapping.get(analysis_type)
            if not model_name:
                raise ValueError(f"不支持的分析类型: {analysis_type}")
            
            # 动态创建模型实例
            model_class = globals()[model_name]
            analysis = model_class(**result_data)
            session.add(analysis)
            await session.flush()
            
            # 清除相关缓存
            session_id = result_data.get("session_id")
            if session_id:
                await self.cache.delete(f"session:{session_id}")
                await self.cache.delete(f"session:{session_id}:analyses")
            
            return str(analysis.id)
    
    async def get_patient_history(self, patient_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取患者历史记录"""
        cache_key = f"patient:{patient_id}:history:{limit}"
        
        # 尝试从缓存获取
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # 从数据库查询
        query = """
        SELECT ds.id, ds.diagnosis_date, ds.tcm_diagnosis, ds.syndrome_pattern, 
               ds.confidence_score, ds.status
        FROM diagnosis_sessions ds
        WHERE ds.patient_id = :patient_id
        ORDER BY ds.diagnosis_date DESC
        LIMIT :limit
        """
        
        results = await self.db.execute_query(query, {
            "patient_id": patient_id,
            "limit": limit
        })
        
        # 缓存结果
        await self.cache.set(cache_key, results, ttl=600)
        return results
    
    async def log_system_event(self, log_data: Dict[str, Any]):
        """记录系统日志"""
        async with self.db.get_session() as session:
            log_entry = SystemLog(**log_data)
            session.add(log_entry)
            await session.commit()
    
    async def record_performance_metric(self, metric_data: Dict[str, Any]):
        """记录性能指标"""
        async with self.db.get_session() as session:
            metric = PerformanceMetric(**metric_data)
            session.add(metric)
            await session.commit()
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计"""
        cache_key = "system:stats"
        
        # 尝试从缓存获取
        cached_stats = await self.cache.get(cache_key)
        if cached_stats:
            return cached_stats
        
        # 查询统计数据
        stats_queries = {
            "total_patients": "SELECT COUNT(*) as count FROM patients WHERE is_active = true",
            "total_sessions": "SELECT COUNT(*) as count FROM diagnosis_sessions",
            "active_sessions": "SELECT COUNT(*) as count FROM diagnosis_sessions WHERE status = 'active'",
            "avg_confidence": "SELECT AVG(confidence_score) as avg_score FROM diagnosis_sessions WHERE confidence_score IS NOT NULL"
        }
        
        stats = {}
        for stat_name, query in stats_queries.items():
            result = await self.db.execute_query(query)
            stats[stat_name] = result[0] if result else {"count": 0, "avg_score": 0}
        
        # 添加缓存统计
        stats["cache_stats"] = self.cache.get_stats()
        
        # 缓存结果
        await self.cache.set(cache_key, stats, ttl=300)
        return stats

# 全局实例
_db_manager = None
_cache_manager = None
_data_access = None

async def get_database_manager() -> DatabaseManager:
    """获取数据库管理器实例"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        await _db_manager.initialize()
    return _db_manager

async def get_cache_manager() -> CacheManager:
    """获取缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        db_manager = await get_database_manager()
        _cache_manager = CacheManager(db_manager.redis_client)
    return _cache_manager

async def get_data_access() -> DataAccessLayer:
    """获取数据访问层实例"""
    global _data_access
    if _data_access is None:
        db_manager = await get_database_manager()
        cache_manager = await get_cache_manager()
        _data_access = DataAccessLayer(db_manager, cache_manager)
    return _data_access 