#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康数据仓库 - 优化版
提供高性能的健康数据访问和查询功能
"""

import uuid
import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from loguru import logger

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, func, and_, or_, text
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from ..model.database import (
    HealthDataRecord, User, SystemMetrics, AuditLog,
    HealthInsightRecord, HealthProfileRecord
)
from ..model.health_data import HealthData, HealthDataType, DeviceType, MeasurementUnit
from ...pkg.utils.error_handler import DatabaseError, ValidationError, with_retry, with_timeout


class HealthDataRepositoryOptimized:
    """优化版健康数据仓库"""
    
    def __init__(self, session: AsyncSession):
        """
        初始化数据仓库
        
        Args:
            session: 数据库会话
        """
        self.session = session
        self.batch_size = 1000
        self.query_timeout = 30
    
    @with_retry(max_attempts=3, retry_exceptions=(DatabaseError,))
    @with_timeout(30.0)
    async def get_health_data(
        self,
        user_id: Union[uuid.UUID, str],
        data_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "timestamp",
        order_desc: bool = True,
        include_metadata: bool = True
    ) -> List[HealthDataRecord]:
        """
        获取健康数据
        
        Args:
            user_id: 用户ID
            data_type: 数据类型
            start_time: 开始时间
            end_time: 结束时间
            limit: 结果限制
            offset: 结果偏移
            order_by: 排序字段
            order_desc: 是否降序
            include_metadata: 是否包含元数据
            
        Returns:
            健康数据记录列表
        """
        try:
            # 构建查询
            query = select(HealthDataRecord).where(
                HealthDataRecord.user_id == str(user_id)
            )
            
            # 添加数据类型过滤
            if data_type:
                query = query.where(HealthDataRecord.data_type == data_type)
            
            # 添加时间范围过滤
            if start_time:
                query = query.where(HealthDataRecord.timestamp >= start_time)
            if end_time:
                query = query.where(HealthDataRecord.timestamp <= end_time)
            
            # 添加排序
            if order_by == "timestamp":
                if order_desc:
                    query = query.order_by(HealthDataRecord.timestamp.desc())
                else:
                    query = query.order_by(HealthDataRecord.timestamp.asc())
            elif order_by == "created_at":
                if order_desc:
                    query = query.order_by(HealthDataRecord.created_at.desc())
                else:
                    query = query.order_by(HealthDataRecord.created_at.asc())
            
            # 添加分页
            query = query.offset(offset).limit(limit)
            
            # 执行查询
            result = await self.session.execute(query)
            records = result.scalars().all()
            
            logger.debug(f"获取到 {len(records)} 条健康数据记录")
            return records
            
        except Exception as e:
            logger.error(f"获取健康数据失败: {e}")
            raise DatabaseError(f"获取健康数据失败: {str(e)}")
    
    @with_retry(max_attempts=3, retry_exceptions=(DatabaseError,))
    @with_timeout(30.0)
    async def save_health_data_record(self, record: HealthDataRecord) -> uuid.UUID:
        """
        保存健康数据记录
        
        Args:
            record: 健康数据记录
            
        Returns:
            记录ID
        """
        try:
            # 设置创建时间
            if not record.created_at:
                record.created_at = datetime.utcnow()
            if not record.updated_at:
                record.updated_at = datetime.utcnow()
            
            # 添加到会话
            self.session.add(record)
            await self.session.commit()
            await self.session.refresh(record)
            
            logger.debug(f"保存健康数据记录成功: {record.id}")
            return record.id
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"保存健康数据记录失败: {e}")
            raise DatabaseError(f"保存健康数据记录失败: {str(e)}")
    
    @with_retry(max_attempts=3, retry_exceptions=(DatabaseError,))
    @with_timeout(60.0)
    async def save_health_data_batch(self, records: List[HealthDataRecord]) -> List[uuid.UUID]:
        """
        批量保存健康数据记录
        
        Args:
            records: 健康数据记录列表
            
        Returns:
            记录ID列表
        """
        try:
            if not records:
                return []
            
            # 设置时间戳
            now = datetime.utcnow()
            for record in records:
                if not record.created_at:
                    record.created_at = now
                if not record.updated_at:
                    record.updated_at = now
            
            # 分批处理
            record_ids = []
            for i in range(0, len(records), self.batch_size):
                batch = records[i:i + self.batch_size]
                
                # 批量插入
                self.session.add_all(batch)
                await self.session.flush()
                
                # 收集ID
                batch_ids = [record.id for record in batch]
                record_ids.extend(batch_ids)
            
            await self.session.commit()
            
            logger.info(f"批量保存 {len(records)} 条健康数据记录成功")
            return record_ids
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"批量保存健康数据记录失败: {e}")
            raise DatabaseError(f"批量保存健康数据记录失败: {str(e)}")
    
    @with_retry(max_attempts=3, retry_exceptions=(DatabaseError,))
    @with_timeout(30.0)
    async def update_health_data_record(
        self, 
        record_id: uuid.UUID, 
        updates: Dict[str, Any]
    ) -> bool:
        """
        更新健康数据记录
        
        Args:
            record_id: 记录ID
            updates: 更新字段
            
        Returns:
            是否更新成功
        """
        try:
            # 添加更新时间
            updates['updated_at'] = datetime.utcnow()
            
            # 执行更新
            query = update(HealthDataRecord).where(
                HealthDataRecord.id == record_id
            ).values(**updates)
            
            result = await self.session.execute(query)
            await self.session.commit()
            
            success = result.rowcount > 0
            if success:
                logger.debug(f"更新健康数据记录成功: {record_id}")
            else:
                logger.warning(f"健康数据记录不存在: {record_id}")
            
            return success
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"更新健康数据记录失败: {e}")
            raise DatabaseError(f"更新健康数据记录失败: {str(e)}")
    
    @with_retry(max_attempts=3, retry_exceptions=(DatabaseError,))
    @with_timeout(30.0)
    async def delete_health_data_record(self, record_id: uuid.UUID) -> bool:
        """
        删除健康数据记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            是否删除成功
        """
        try:
            query = delete(HealthDataRecord).where(
                HealthDataRecord.id == record_id
            )
            
            result = await self.session.execute(query)
            await self.session.commit()
            
            success = result.rowcount > 0
            if success:
                logger.debug(f"删除健康数据记录成功: {record_id}")
            else:
                logger.warning(f"健康数据记录不存在: {record_id}")
            
            return success
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"删除健康数据记录失败: {e}")
            raise DatabaseError(f"删除健康数据记录失败: {str(e)}")
    
    @with_retry(max_attempts=3, retry_exceptions=(DatabaseError,))
    @with_timeout(30.0)
    async def get_health_data_statistics(
        self,
        user_id: Union[uuid.UUID, str],
        data_type: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        获取健康数据统计信息
        
        Args:
            user_id: 用户ID
            data_type: 数据类型
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            统计信息
        """
        try:
            # 构建基础查询
            base_query = select(HealthDataRecord).where(
                and_(
                    HealthDataRecord.user_id == str(user_id),
                    HealthDataRecord.data_type == data_type
                )
            )
            
            # 添加时间范围
            if start_time:
                base_query = base_query.where(HealthDataRecord.timestamp >= start_time)
            if end_time:
                base_query = base_query.where(HealthDataRecord.timestamp <= end_time)
            
            # 计算统计信息
            stats_query = select(
                func.count(HealthDataRecord.id).label('count'),
                func.min(HealthDataRecord.timestamp).label('earliest'),
                func.max(HealthDataRecord.timestamp).label('latest'),
                func.avg(HealthDataRecord.quality_score).label('avg_quality')
            ).where(
                and_(
                    HealthDataRecord.user_id == str(user_id),
                    HealthDataRecord.data_type == data_type
                )
            )
            
            if start_time:
                stats_query = stats_query.where(HealthDataRecord.timestamp >= start_time)
            if end_time:
                stats_query = stats_query.where(HealthDataRecord.timestamp <= end_time)
            
            result = await self.session.execute(stats_query)
            stats = result.first()
            
            return {
                'count': stats.count if stats else 0,
                'earliest_timestamp': stats.earliest if stats else None,
                'latest_timestamp': stats.latest if stats else None,
                'average_quality_score': float(stats.avg_quality) if stats and stats.avg_quality else 0.0
            }
            
        except Exception as e:
            logger.error(f"获取健康数据统计信息失败: {e}")
            raise DatabaseError(f"获取健康数据统计信息失败: {str(e)}")
    
    @with_retry(max_attempts=3, retry_exceptions=(DatabaseError,))
    @with_timeout(30.0)
    async def get_data_quality_metrics(
        self,
        user_id: Optional[Union[uuid.UUID, str]] = None,
        data_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        获取数据质量指标
        
        Args:
            user_id: 用户ID（可选）
            data_type: 数据类型（可选）
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            数据质量指标
        """
        try:
            # 构建查询
            query = select(
                func.count(HealthDataRecord.id).label('total_count'),
                func.count(HealthDataRecord.id).filter(
                    HealthDataRecord.is_validated == True
                ).label('validated_count'),
                func.avg(HealthDataRecord.quality_score).label('avg_quality_score'),
                func.min(HealthDataRecord.quality_score).label('min_quality_score'),
                func.max(HealthDataRecord.quality_score).label('max_quality_score'),
                func.count(HealthDataRecord.id).filter(
                    HealthDataRecord.quality_score >= 0.8
                ).label('high_quality_count'),
                func.count(HealthDataRecord.id).filter(
                    and_(
                        HealthDataRecord.quality_score >= 0.5,
                        HealthDataRecord.quality_score < 0.8
                    )
                ).label('medium_quality_count'),
                func.count(HealthDataRecord.id).filter(
                    HealthDataRecord.quality_score < 0.5
                ).label('low_quality_count')
            )
            
            # 添加过滤条件
            conditions = []
            if user_id:
                conditions.append(HealthDataRecord.user_id == str(user_id))
            if data_type:
                conditions.append(HealthDataRecord.data_type == data_type)
            if start_time:
                conditions.append(HealthDataRecord.timestamp >= start_time)
            if end_time:
                conditions.append(HealthDataRecord.timestamp <= end_time)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            result = await self.session.execute(query)
            metrics = result.first()
            
            if not metrics or metrics.total_count == 0:
                return {
                    'total_count': 0,
                    'validated_count': 0,
                    'validation_rate': 0.0,
                    'average_quality_score': 0.0,
                    'min_quality_score': 0.0,
                    'max_quality_score': 0.0,
                    'high_quality_count': 0,
                    'medium_quality_count': 0,
                    'low_quality_count': 0,
                    'high_quality_rate': 0.0,
                    'medium_quality_rate': 0.0,
                    'low_quality_rate': 0.0
                }
            
            total = metrics.total_count
            return {
                'total_count': total,
                'validated_count': metrics.validated_count,
                'validation_rate': metrics.validated_count / total,
                'average_quality_score': float(metrics.avg_quality_score or 0),
                'min_quality_score': float(metrics.min_quality_score or 0),
                'max_quality_score': float(metrics.max_quality_score or 0),
                'high_quality_count': metrics.high_quality_count,
                'medium_quality_count': metrics.medium_quality_count,
                'low_quality_count': metrics.low_quality_count,
                'high_quality_rate': metrics.high_quality_count / total,
                'medium_quality_rate': metrics.medium_quality_count / total,
                'low_quality_rate': metrics.low_quality_count / total
            }
            
        except Exception as e:
            logger.error(f"获取数据质量指标失败: {e}")
            raise DatabaseError(f"获取数据质量指标失败: {str(e)}")
    
    @with_retry(max_attempts=3, retry_exceptions=(DatabaseError,))
    @with_timeout(30.0)
    async def get_user_data_summary(
        self,
        user_id: Union[uuid.UUID, str],
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取用户数据摘要
        
        Args:
            user_id: 用户ID
            days: 统计天数
            
        Returns:
            用户数据摘要
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # 按数据类型统计
            query = select(
                HealthDataRecord.data_type,
                func.count(HealthDataRecord.id).label('count'),
                func.min(HealthDataRecord.timestamp).label('earliest'),
                func.max(HealthDataRecord.timestamp).label('latest'),
                func.avg(HealthDataRecord.quality_score).label('avg_quality')
            ).where(
                and_(
                    HealthDataRecord.user_id == str(user_id),
                    HealthDataRecord.timestamp >= start_time,
                    HealthDataRecord.timestamp <= end_time
                )
            ).group_by(HealthDataRecord.data_type)
            
            result = await self.session.execute(query)
            type_stats = result.all()
            
            # 整理结果
            summary = {
                'user_id': str(user_id),
                'period_days': days,
                'start_time': start_time,
                'end_time': end_time,
                'total_records': 0,
                'data_types': {},
                'overall_quality': 0.0
            }
            
            total_records = 0
            total_quality = 0.0
            
            for stat in type_stats:
                total_records += stat.count
                total_quality += stat.avg_quality * stat.count
                
                summary['data_types'][stat.data_type] = {
                    'count': stat.count,
                    'earliest_timestamp': stat.earliest,
                    'latest_timestamp': stat.latest,
                    'average_quality': float(stat.avg_quality or 0)
                }
            
            summary['total_records'] = total_records
            if total_records > 0:
                summary['overall_quality'] = total_quality / total_records
            
            return summary
            
        except Exception as e:
            logger.error(f"获取用户数据摘要失败: {e}")
            raise DatabaseError(f"获取用户数据摘要失败: {str(e)}")
    
    @with_retry(max_attempts=3, retry_exceptions=(DatabaseError,))
    @with_timeout(30.0)
    async def search_health_data(
        self,
        user_id: Union[uuid.UUID, str],
        search_criteria: Dict[str, Any],
        limit: int = 100,
        offset: int = 0
    ) -> List[HealthDataRecord]:
        """
        搜索健康数据
        
        Args:
            user_id: 用户ID
            search_criteria: 搜索条件
            limit: 结果限制
            offset: 结果偏移
            
        Returns:
            健康数据记录列表
        """
        try:
            # 构建基础查询
            query = select(HealthDataRecord).where(
                HealthDataRecord.user_id == str(user_id)
            )
            
            # 添加搜索条件
            if 'data_types' in search_criteria:
                data_types = search_criteria['data_types']
                if isinstance(data_types, list):
                    query = query.where(HealthDataRecord.data_type.in_(data_types))
                else:
                    query = query.where(HealthDataRecord.data_type == data_types)
            
            if 'device_types' in search_criteria:
                device_types = search_criteria['device_types']
                if isinstance(device_types, list):
                    query = query.where(HealthDataRecord.device_type.in_(device_types))
                else:
                    query = query.where(HealthDataRecord.device_type == device_types)
            
            if 'start_time' in search_criteria:
                query = query.where(HealthDataRecord.timestamp >= search_criteria['start_time'])
            
            if 'end_time' in search_criteria:
                query = query.where(HealthDataRecord.timestamp <= search_criteria['end_time'])
            
            if 'min_quality_score' in search_criteria:
                query = query.where(HealthDataRecord.quality_score >= search_criteria['min_quality_score'])
            
            if 'is_validated' in search_criteria:
                query = query.where(HealthDataRecord.is_validated == search_criteria['is_validated'])
            
            if 'source' in search_criteria:
                query = query.where(HealthDataRecord.source.ilike(f"%{search_criteria['source']}%"))
            
            # 值范围搜索
            if 'value_min' in search_criteria or 'value_max' in search_criteria:
                # 这里需要根据具体的数据库实现来处理JSON字段查询
                # SQLite和PostgreSQL的JSON查询语法不同
                pass
            
            # 排序和分页
            query = query.order_by(HealthDataRecord.timestamp.desc())
            query = query.offset(offset).limit(limit)
            
            result = await self.session.execute(query)
            records = result.scalars().all()
            
            logger.debug(f"搜索到 {len(records)} 条健康数据记录")
            return records
            
        except Exception as e:
            logger.error(f"搜索健康数据失败: {e}")
            raise DatabaseError(f"搜索健康数据失败: {str(e)}")
    
    @with_retry(max_attempts=3, retry_exceptions=(DatabaseError,))
    @with_timeout(30.0)
    async def get_recent_health_data(
        self,
        user_id: Union[uuid.UUID, str],
        data_type: Optional[str] = None,
        hours: int = 24,
        limit: int = 1000
    ) -> List[HealthDataRecord]:
        """
        获取最近的健康数据
        
        Args:
            user_id: 用户ID
            data_type: 数据类型（可选）
            hours: 最近小时数
            limit: 结果限制
            
        Returns:
            健康数据记录列表
        """
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            query = select(HealthDataRecord).where(
                and_(
                    HealthDataRecord.user_id == str(user_id),
                    HealthDataRecord.timestamp >= start_time
                )
            )
            
            if data_type:
                query = query.where(HealthDataRecord.data_type == data_type)
            
            query = query.order_by(HealthDataRecord.timestamp.desc()).limit(limit)
            
            result = await self.session.execute(query)
            records = result.scalars().all()
            
            logger.debug(f"获取到最近 {hours} 小时内的 {len(records)} 条健康数据记录")
            return records
            
        except Exception as e:
            logger.error(f"获取最近健康数据失败: {e}")
            raise DatabaseError(f"获取最近健康数据失败: {str(e)}")
    
    @with_retry(max_attempts=3, retry_exceptions=(DatabaseError,))
    @with_timeout(30.0)
    async def cleanup_old_data(
        self,
        retention_days: int = 365,
        batch_size: int = 1000
    ) -> int:
        """
        清理旧数据
        
        Args:
            retention_days: 保留天数
            batch_size: 批处理大小
            
        Returns:
            删除的记录数
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=retention_days)
            
            # 分批删除
            total_deleted = 0
            
            while True:
                # 查找要删除的记录ID
                query = select(HealthDataRecord.id).where(
                    HealthDataRecord.timestamp < cutoff_time
                ).limit(batch_size)
                
                result = await self.session.execute(query)
                record_ids = [row[0] for row in result.fetchall()]
                
                if not record_ids:
                    break
                
                # 删除这批记录
                delete_query = delete(HealthDataRecord).where(
                    HealthDataRecord.id.in_(record_ids)
                )
                
                result = await self.session.execute(delete_query)
                deleted_count = result.rowcount
                total_deleted += deleted_count
                
                await self.session.commit()
                
                logger.info(f"删除了 {deleted_count} 条旧健康数据记录")
                
                # 如果删除的记录数少于批大小，说明已经删除完毕
                if deleted_count < batch_size:
                    break
            
            logger.info(f"数据清理完成，总共删除了 {total_deleted} 条记录")
            return total_deleted
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"清理旧数据失败: {e}")
            raise DatabaseError(f"清理旧数据失败: {str(e)}")
    
    async def get_database_metrics(self) -> Dict[str, Any]:
        """
        获取数据库指标
        
        Returns:
            数据库指标
        """
        try:
            # 获取表大小和记录数
            tables_info = {}
            
            # 健康数据表
            health_data_query = select(
                func.count(HealthDataRecord.id).label('count')
            )
            result = await self.session.execute(health_data_query)
            health_data_count = result.scalar()
            
            tables_info['health_data_records'] = {
                'count': health_data_count
            }
            
            # 用户表
            user_query = select(func.count(User.id).label('count'))
            result = await self.session.execute(user_query)
            user_count = result.scalar()
            
            tables_info['users'] = {
                'count': user_count
            }
            
            # 数据质量统计
            quality_query = select(
                func.avg(HealthDataRecord.quality_score).label('avg_quality'),
                func.count(HealthDataRecord.id).filter(
                    HealthDataRecord.quality_score >= 0.8
                ).label('high_quality_count'),
                func.count(HealthDataRecord.id).filter(
                    HealthDataRecord.is_validated == True
                ).label('validated_count')
            )
            result = await self.session.execute(quality_query)
            quality_stats = result.first()
            
            return {
                'tables': tables_info,
                'data_quality': {
                    'average_quality_score': float(quality_stats.avg_quality or 0),
                    'high_quality_count': quality_stats.high_quality_count,
                    'validated_count': quality_stats.validated_count,
                    'high_quality_rate': quality_stats.high_quality_count / health_data_count if health_data_count > 0 else 0,
                    'validation_rate': quality_stats.validated_count / health_data_count if health_data_count > 0 else 0
                },
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"获取数据库指标失败: {e}")
            raise DatabaseError(f"获取数据库指标失败: {str(e)}") 