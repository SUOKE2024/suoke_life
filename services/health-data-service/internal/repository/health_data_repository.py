#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康数据仓库，负责健康数据的持久化操作
"""

import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_, desc
from sqlalchemy.dialects.postgresql import insert

from ..model.database import HealthDataRecord, User, TCMConstitution, HealthInsight, HealthProfile
from ..model.health_data import HealthData, HealthDataType, TCMConstitutionData, HealthInsight as HealthInsightModel


class HealthDataRepository:
    """健康数据仓库类"""
    
    def __init__(self, session: AsyncSession):
        """
        初始化健康数据仓库
        
        Args:
            session: 数据库会话
        """
        self.session = session
    
    async def get_user_by_external_id(self, external_id: str) -> Optional[User]:
        """
        根据外部ID获取用户
        
        Args:
            external_id: 外部用户ID
            
        Returns:
            用户对象，如果不存在则返回None
        """
        result = await self.session.execute(
            select(User).where(User.external_id == external_id)
        )
        return result.scalars().first()
    
    async def create_user(self, external_id: str) -> User:
        """
        创建用户
        
        Args:
            external_id: 外部用户ID
            
        Returns:
            创建的用户对象
        """
        user = User(
            external_id=external_id
        )
        self.session.add(user)
        await self.session.flush()
        return user
    
    async def get_or_create_user(self, external_id: str) -> User:
        """
        获取用户，如果不存在则创建
        
        Args:
            external_id: 外部用户ID
            
        Returns:
            用户对象
        """
        user = await self.get_user_by_external_id(external_id)
        if not user:
            user = await self.create_user(external_id)
        return user
    
    async def save_health_data(self, data: HealthData) -> HealthDataRecord:
        """
        保存健康数据
        
        Args:
            data: 健康数据对象
            
        Returns:
            保存的健康数据记录
        """
        record = HealthDataRecord(
            id=data.id,
            user_id=data.user_id,
            data_type=data.data_type.value,
            timestamp=data.timestamp,
            device_type=data.device_type.value,
            device_id=data.device_id,
            value=data.value if isinstance(data.value, dict) else {"value": data.value},
            unit=data.unit.value,
            source=data.source,
            metadata=data.metadata
        )
        
        self.session.add(record)
        await self.session.flush()
        return record
    
    async def save_health_data_batch(self, data_list: List[HealthData]) -> List[HealthDataRecord]:
        """
        批量保存健康数据
        
        Args:
            data_list: 健康数据对象列表
            
        Returns:
            保存的健康数据记录列表
        """
        records = []
        for data in data_list:
            record = HealthDataRecord(
                id=data.id,
                user_id=data.user_id,
                data_type=data.data_type.value,
                timestamp=data.timestamp,
                device_type=data.device_type.value,
                device_id=data.device_id,
                value=data.value if isinstance(data.value, dict) else {"value": data.value},
                unit=data.unit.value,
                source=data.source,
                metadata=data.metadata
            )
            records.append(record)
        
        self.session.add_all(records)
        await self.session.flush()
        return records
    
    async def get_health_data(
        self,
        user_id: Union[uuid.UUID, str],
        data_type: Optional[Union[HealthDataType, str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
        sort_desc: bool = True
    ) -> List[HealthDataRecord]:
        """
        获取健康数据
        
        Args:
            user_id: 用户ID
            data_type: 数据类型
            start_time: 开始时间
            end_time: 结束时间
            limit: 限制数量
            offset: 偏移量
            sort_desc: 是否降序排序
            
        Returns:
            健康数据记录列表
        """
        user_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        query = select(HealthDataRecord).where(HealthDataRecord.user_id == user_id)
        
        if data_type:
            data_type_str = data_type.value if isinstance(data_type, HealthDataType) else data_type
            query = query.where(HealthDataRecord.data_type == data_type_str)
        
        if start_time:
            query = query.where(HealthDataRecord.timestamp >= start_time)
        
        if end_time:
            query = query.where(HealthDataRecord.timestamp <= end_time)
        
        if sort_desc:
            query = query.order_by(desc(HealthDataRecord.timestamp))
        else:
            query = query.order_by(HealthDataRecord.timestamp)
        
        query = query.limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_latest_health_data(
        self,
        user_id: Union[uuid.UUID, str],
        data_type: Union[HealthDataType, str],
        lookback_hours: int = 24
    ) -> Optional[HealthDataRecord]:
        """
        获取最新的健康数据
        
        Args:
            user_id: 用户ID
            data_type: 数据类型
            lookback_hours: 向前查找小时数
            
        Returns:
            最新的健康数据记录
        """
        user_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        data_type_str = data_type.value if isinstance(data_type, HealthDataType) else data_type
        
        # 计算查询起始时间
        start_time = datetime.utcnow() - timedelta(hours=lookback_hours)
        
        query = (
            select(HealthDataRecord)
            .where(
                and_(
                    HealthDataRecord.user_id == user_id,
                    HealthDataRecord.data_type == data_type_str,
                    HealthDataRecord.timestamp >= start_time
                )
            )
            .order_by(desc(HealthDataRecord.timestamp))
            .limit(1)
        )
        
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_health_data_statistics(
        self,
        user_id: Union[uuid.UUID, str],
        data_type: Union[HealthDataType, str],
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """
        获取健康数据统计信息
        
        Args:
            user_id: 用户ID
            data_type: 数据类型
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            统计信息字典
        """
        user_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        data_type_str = data_type.value if isinstance(data_type, HealthDataType) else data_type
        
        # 查询平均值、最大值、最小值、记录数
        query = (
            select(
                func.avg(func.cast(HealthDataRecord.value['value'].astext, type_=sa.Float)).label("avg"),
                func.max(func.cast(HealthDataRecord.value['value'].astext, type_=sa.Float)).label("max"),
                func.min(func.cast(HealthDataRecord.value['value'].astext, type_=sa.Float)).label("min"),
                func.count().label("count")
            )
            .where(
                and_(
                    HealthDataRecord.user_id == user_id,
                    HealthDataRecord.data_type == data_type_str,
                    HealthDataRecord.timestamp >= start_time,
                    HealthDataRecord.timestamp <= end_time
                )
            )
        )
        
        result = await self.session.execute(query)
        stats = result.fetchone()
        
        return {
            "average": stats.avg if stats.avg else 0,
            "maximum": stats.max if stats.max else 0,
            "minimum": stats.min if stats.min else 0,
            "count": stats.count if stats.count else 0,
            "start_time": start_time,
            "end_time": end_time,
            "data_type": data_type_str
        }
    
    async def save_tcm_constitution(self, data: TCMConstitutionData) -> TCMConstitution:
        """
        保存中医体质数据
        
        Args:
            data: 中医体质数据对象
            
        Returns:
            保存的中医体质记录
        """
        constitution = TCMConstitution(
            id=data.id,
            user_id=data.user_id,
            timestamp=data.timestamp,
            primary_type=data.primary_type.value,
            secondary_types=[t.value for t in data.secondary_types],
            scores=data.scores,
            analysis_basis=data.analysis_basis,
            recommendations=data.recommendations,
            created_by=data.created_by
        )
        
        self.session.add(constitution)
        await self.session.flush()
        return constitution
    
    async def get_latest_tcm_constitution(
        self,
        user_id: Union[uuid.UUID, str]
    ) -> Optional[TCMConstitution]:
        """
        获取用户最新的中医体质数据
        
        Args:
            user_id: 用户ID
            
        Returns:
            最新的中医体质记录
        """
        user_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        query = (
            select(TCMConstitution)
            .where(TCMConstitution.user_id == user_id)
            .order_by(desc(TCMConstitution.timestamp))
            .limit(1)
        )
        
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_tcm_constitution_history(
        self,
        user_id: Union[uuid.UUID, str],
        limit: int = 10
    ) -> List[TCMConstitution]:
        """
        获取用户的中医体质历史记录
        
        Args:
            user_id: 用户ID
            limit: 限制数量
            
        Returns:
            中医体质记录列表
        """
        user_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        query = (
            select(TCMConstitution)
            .where(TCMConstitution.user_id == user_id)
            .order_by(desc(TCMConstitution.timestamp))
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def save_health_insight(self, insight: HealthInsightModel) -> HealthInsight:
        """
        保存健康洞察
        
        Args:
            insight: 健康洞察对象
            
        Returns:
            保存的健康洞察记录
        """
        record = HealthInsight(
            id=insight.id,
            user_id=insight.user_id,
            timestamp=insight.timestamp,
            insight_type=insight.insight_type,
            data_type=insight.data_type.value if isinstance(insight.data_type, HealthDataType) else insight.data_type,
            time_range=insight.time_range,
            description=insight.description,
            details=insight.details,
            severity=insight.severity,
            relevance_score=insight.relevance_score
        )
        
        self.session.add(record)
        await self.session.flush()
        return record
    
    async def get_health_insights(
        self,
        user_id: Union[uuid.UUID, str],
        insight_type: Optional[str] = None,
        severity: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 20
    ) -> List[HealthInsight]:
        """
        获取健康洞察
        
        Args:
            user_id: 用户ID
            insight_type: 洞察类型
            severity: 严重程度
            start_time: 开始时间
            end_time: 结束时间
            limit: 限制数量
            
        Returns:
            健康洞察记录列表
        """
        user_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        query = select(HealthInsight).where(HealthInsight.user_id == user_id)
        
        if insight_type:
            query = query.where(HealthInsight.insight_type == insight_type)
        
        if severity:
            query = query.where(HealthInsight.severity == severity)
        
        if start_time:
            query = query.where(HealthInsight.timestamp >= start_time)
        
        if end_time:
            query = query.where(HealthInsight.timestamp <= end_time)
        
        query = query.order_by(desc(HealthInsight.timestamp)).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def save_health_profile(self, profile: HealthProfile) -> HealthProfile:
        """
        保存健康档案
        
        Args:
            profile: 健康档案对象
            
        Returns:
            保存的健康档案记录
        """
        self.session.add(profile)
        await self.session.flush()
        return profile
    
    async def get_latest_health_profile(
        self,
        user_id: Union[uuid.UUID, str]
    ) -> Optional[HealthProfile]:
        """
        获取用户最新的健康档案
        
        Args:
            user_id: 用户ID
            
        Returns:
            最新的健康档案记录
        """
        user_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        query = (
            select(HealthProfile)
            .where(HealthProfile.user_id == user_id)
            .order_by(desc(HealthProfile.timestamp))
            .limit(1)
        )
        
        result = await self.session.execute(query)
        return result.scalars().first() 