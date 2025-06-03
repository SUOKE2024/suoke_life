#!/usr/bin/env python3
"""
数据库连接和操作模块

提供数据库连接池、会话管理、事务处理等功能。
"""

import asyncio
import contextlib
from typing import AsyncGenerator, Optional, Any, Dict, List
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, JSON, Float, Boolean, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from datetime import datetime
import logging

from .config import get_settings

logger = logging.getLogger(__name__)

# 数据库基类
Base = declarative_base()

# 元数据
metadata = MetaData()

# 健康数据表定义
health_data_table = Table(
    'health_data',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, nullable=False, index=True),
    Column('data_type', String(50), nullable=False, index=True),
    Column('data_source', String(50), nullable=False),
    Column('raw_data', JSON, nullable=False),
    Column('processed_data', JSON, nullable=True),
    Column('device_id', String(100), nullable=True),
    Column('location', JSON, nullable=True),
    Column('tags', JSON, nullable=True),
    Column('quality_score', Float, nullable=True),
    Column('confidence_score', Float, nullable=True),
    Column('is_validated', Boolean, default=False),
    Column('is_anomaly', Boolean, default=False),
    Column('recorded_at', DateTime, nullable=False),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
    Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
)

# 生命体征表定义
vital_signs_table = Table(
    'vital_signs',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, nullable=False, index=True),
    Column('systolic_bp', Integer, nullable=True),
    Column('diastolic_bp', Integer, nullable=True),
    Column('heart_rate', Integer, nullable=True),
    Column('temperature', Float, nullable=True),
    Column('respiratory_rate', Integer, nullable=True),
    Column('oxygen_saturation', Float, nullable=True),
    Column('weight', Float, nullable=True),
    Column('height', Float, nullable=True),
    Column('bmi', Float, nullable=True),
    Column('device_id', String(100), nullable=True),
    Column('location', JSON, nullable=True),
    Column('notes', Text, nullable=True),
    Column('recorded_at', DateTime, nullable=False),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
    Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
)

# 中医五诊数据表定义
tcm_diagnosis_table = Table(
    'tcm_diagnosis',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, nullable=False, index=True),
    Column('diagnosis_type', String(20), nullable=False, index=True),  # look, listen, inquiry, palpation, calculation
    Column('diagnosis_data', JSON, nullable=False),
    Column('standardized_data', JSON, nullable=True),
    Column('quality_score', Float, nullable=True),
    Column('practitioner_id', Integer, nullable=True),
    Column('clinic_id', Integer, nullable=True),
    Column('session_id', String(100), nullable=True),
    Column('notes', Text, nullable=True),
    Column('recorded_at', DateTime, nullable=False),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
    Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
)

# 数据处理记录表
processing_records_table = Table(
    'processing_records',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('pipeline_id', String(100), nullable=False, unique=True, index=True),
    Column('user_id', Integer, nullable=False, index=True),
    Column('data_type', String(50), nullable=False),
    Column('stage', String(50), nullable=False),
    Column('status', String(20), nullable=False),
    Column('original_data', JSON, nullable=False),
    Column('processed_data', JSON, nullable=True),
    Column('privacy_proof', JSON, nullable=True),
    Column('errors', JSON, nullable=True),
    Column('warnings', JSON, nullable=True),
    Column('metadata', JSON, nullable=True),
    Column('processing_time', Float, nullable=True),
    Column('created_at', DateTime, default=datetime.utcnow, nullable=False),
    Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.settings = get_settings()
        self._async_engine = None
        self._sync_engine = None
        self._async_session_factory = None
        self._sync_session_factory = None
        
    async def initialize(self):
        """初始化数据库连接"""
        try:
            # 创建异步引擎
            self._async_engine = create_async_engine(
                self.settings.database.postgres_url,
                poolclass=QueuePool,
                pool_size=self.settings.database.pool_size,
                max_overflow=self.settings.database.max_overflow,
                pool_timeout=self.settings.database.pool_timeout,
                pool_recycle=self.settings.database.pool_recycle,
                echo=self.settings.debug,
            )
            
            # 创建同步引擎
            self._sync_engine = create_engine(
                self.settings.database.postgres_sync_url,
                poolclass=QueuePool,
                pool_size=self.settings.database.pool_size,
                max_overflow=self.settings.database.max_overflow,
                pool_timeout=self.settings.database.pool_timeout,
                pool_recycle=self.settings.database.pool_recycle,
                echo=self.settings.debug,
            )
            
            # 创建会话工厂
            self._async_session_factory = async_sessionmaker(
                self._async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            self._sync_session_factory = sessionmaker(
                self._sync_engine,
                class_=Session,
                expire_on_commit=False
            )
            
            logger.info("数据库连接初始化成功")
            
        except Exception as e:
            logger.error(f"数据库连接初始化失败: {e}")
            raise
    
    async def create_tables(self):
        """创建数据库表"""
        try:
            async with self._async_engine.begin() as conn:
                await conn.run_sync(metadata.create_all)
            logger.info("数据库表创建成功")
        except Exception as e:
            logger.error(f"数据库表创建失败: {e}")
            raise
    
    async def drop_tables(self):
        """删除数据库表"""
        try:
            async with self._async_engine.begin() as conn:
                await conn.run_sync(metadata.drop_all)
            logger.info("数据库表删除成功")
        except Exception as e:
            logger.error(f"数据库表删除失败: {e}")
            raise
    
    @contextlib.asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取异步数据库会话"""
        if not self._async_session_factory:
            await self.initialize()
        
        async with self._async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @contextlib.contextmanager
    def get_sync_session(self):
        """获取同步数据库会话"""
        if not self._sync_session_factory:
            # 同步初始化
            self._sync_engine = create_engine(
                self.settings.database.postgres_sync_url,
                poolclass=QueuePool,
                pool_size=self.settings.database.pool_size,
                max_overflow=self.settings.database.max_overflow,
                pool_timeout=self.settings.database.pool_timeout,
                pool_recycle=self.settings.database.pool_recycle,
                echo=self.settings.debug,
            )
            
            self._sync_session_factory = sessionmaker(
                self._sync_engine,
                class_=Session,
                expire_on_commit=False
            )
        
        with self._sync_session_factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()
    
    async def health_check(self) -> bool:
        """数据库健康检查"""
        try:
            async with self.get_async_session() as session:
                result = await session.execute("SELECT 1")
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return False
    
    async def close(self):
        """关闭数据库连接"""
        if self._async_engine:
            await self._async_engine.dispose()
        if self._sync_engine:
            self._sync_engine.dispose()
        logger.info("数据库连接已关闭")


class HealthDataRepository:
    """健康数据仓库"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def create_health_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建健康数据记录"""
        async with self.db_manager.get_async_session() as session:
            # 插入数据
            result = await session.execute(
                health_data_table.insert().values(**data).returning(health_data_table)
            )
            record = result.fetchone()
            return dict(record._mapping) if record else None
    
    async def get_health_data_by_id(self, data_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取健康数据"""
        async with self.db_manager.get_async_session() as session:
            result = await session.execute(
                health_data_table.select().where(health_data_table.c.id == data_id)
            )
            record = result.fetchone()
            return dict(record._mapping) if record else None
    
    async def get_health_data_by_user(
        self, 
        user_id: int, 
        data_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """根据用户ID获取健康数据列表"""
        async with self.db_manager.get_async_session() as session:
            query = health_data_table.select().where(health_data_table.c.user_id == user_id)
            
            if data_type:
                query = query.where(health_data_table.c.data_type == data_type)
            
            query = query.order_by(health_data_table.c.recorded_at.desc()).limit(limit).offset(offset)
            
            result = await session.execute(query)
            records = result.fetchall()
            return [dict(record._mapping) for record in records]
    
    async def update_health_data(self, data_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新健康数据"""
        data['updated_at'] = datetime.utcnow()
        
        async with self.db_manager.get_async_session() as session:
            result = await session.execute(
                health_data_table.update()
                .where(health_data_table.c.id == data_id)
                .values(**data)
                .returning(health_data_table)
            )
            record = result.fetchone()
            return dict(record._mapping) if record else None
    
    async def delete_health_data(self, data_id: int) -> bool:
        """删除健康数据"""
        async with self.db_manager.get_async_session() as session:
            result = await session.execute(
                health_data_table.delete().where(health_data_table.c.id == data_id)
            )
            return result.rowcount > 0


class VitalSignsRepository:
    """生命体征数据仓库"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def create_vital_signs(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建生命体征记录"""
        async with self.db_manager.get_async_session() as session:
            result = await session.execute(
                vital_signs_table.insert().values(**data).returning(vital_signs_table)
            )
            record = result.fetchone()
            return dict(record._mapping) if record else None
    
    async def get_vital_signs_by_user(
        self, 
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """根据用户ID获取生命体征列表"""
        async with self.db_manager.get_async_session() as session:
            query = (
                vital_signs_table.select()
                .where(vital_signs_table.c.user_id == user_id)
                .order_by(vital_signs_table.c.recorded_at.desc())
                .limit(limit)
                .offset(offset)
            )
            
            result = await session.execute(query)
            records = result.fetchall()
            return [dict(record._mapping) for record in records]


class TCMDiagnosisRepository:
    """中医诊断数据仓库"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def create_tcm_diagnosis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建中医诊断记录"""
        async with self.db_manager.get_async_session() as session:
            result = await session.execute(
                tcm_diagnosis_table.insert().values(**data).returning(tcm_diagnosis_table)
            )
            record = result.fetchone()
            return dict(record._mapping) if record else None
    
    async def get_tcm_diagnosis_by_user(
        self, 
        user_id: int,
        diagnosis_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """根据用户ID获取中医诊断列表"""
        async with self.db_manager.get_async_session() as session:
            query = tcm_diagnosis_table.select().where(tcm_diagnosis_table.c.user_id == user_id)
            
            if diagnosis_type:
                query = query.where(tcm_diagnosis_table.c.diagnosis_type == diagnosis_type)
            
            query = query.order_by(tcm_diagnosis_table.c.recorded_at.desc()).limit(limit).offset(offset)
            
            result = await session.execute(query)
            records = result.fetchall()
            return [dict(record._mapping) for record in records]


class ProcessingRecordsRepository:
    """数据处理记录仓库"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def create_processing_record(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建处理记录"""
        async with self.db_manager.get_async_session() as session:
            result = await session.execute(
                processing_records_table.insert().values(**data).returning(processing_records_table)
            )
            record = result.fetchone()
            return dict(record._mapping) if record else None
    
    async def get_processing_record_by_pipeline_id(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """根据流水线ID获取处理记录"""
        async with self.db_manager.get_async_session() as session:
            result = await session.execute(
                processing_records_table.select()
                .where(processing_records_table.c.pipeline_id == pipeline_id)
            )
            record = result.fetchone()
            return dict(record._mapping) if record else None
    
    async def update_processing_record(self, pipeline_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新处理记录"""
        data['updated_at'] = datetime.utcnow()
        
        async with self.db_manager.get_async_session() as session:
            result = await session.execute(
                processing_records_table.update()
                .where(processing_records_table.c.pipeline_id == pipeline_id)
                .values(**data)
                .returning(processing_records_table)
            )
            record = result.fetchone()
            return dict(record._mapping) if record else None


# 全局数据库管理器实例
db_manager = DatabaseManager()

# 仓库实例
health_data_repo = HealthDataRepository(db_manager)
vital_signs_repo = VitalSignsRepository(db_manager)
tcm_diagnosis_repo = TCMDiagnosisRepository(db_manager)
processing_records_repo = ProcessingRecordsRepository(db_manager)


async def get_database() -> DatabaseManager:
    """获取数据库管理器"""
    return db_manager


async def init_database():
    """初始化数据库"""
    await db_manager.initialize()
    await db_manager.create_tables()


async def close_database():
    """关闭数据库连接"""
    await db_manager.close()
