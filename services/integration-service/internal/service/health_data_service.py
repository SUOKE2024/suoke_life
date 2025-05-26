"""
Health Data Service - Health Data Management
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ..model.health_data import (
    ActivityData, SleepData, HeartRateData, DataSource,
    HealthDataSummary, HealthDataRequest, HealthDataResponse
)
from ..repository.health_data_repository import HealthDataRepository
from .database import db_service
from .redis_client import redis_service
from .logging_config import LoggerMixin
from .config import get_settings


class HealthDataService(LoggerMixin):
    """健康数据管理服务"""
    
    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.health_data_repo = HealthDataRepository()
    
    async def store_activity_data(
        self,
        user_id: str,
        activity_data: List[ActivityData]
    ) -> int:
        """存储活动数据"""
        try:
            stored_count = 0
            
            async with db_service.get_session() as session:
                for data in activity_data:
                    # 转换为数据库模型
                    activity_dict = data.dict()
                    activity_dict.pop('id', None)  # 移除ID字段
                    
                    await self.health_data_repo.create_activity_data(
                        session, activity_dict
                    )
                    stored_count += 1
                
                await session.commit()
            
            # 清除相关缓存
            await self._invalidate_health_data_cache(user_id, "activity")
            
            self.logger.info("存储活动数据成功",
                           user_id=user_id,
                           count=stored_count)
            
            return stored_count
            
        except Exception as e:
            self.logger.error("存储活动数据失败",
                            user_id=user_id,
                            error=str(e))
            raise
    
    async def store_sleep_data(
        self,
        user_id: str,
        sleep_data: List[SleepData]
    ) -> int:
        """存储睡眠数据"""
        try:
            stored_count = 0
            
            async with db_service.get_session() as session:
                for data in sleep_data:
                    # 转换为数据库模型
                    sleep_dict = data.dict()
                    sleep_dict.pop('id', None)  # 移除ID字段
                    
                    await self.health_data_repo.create_sleep_data(
                        session, sleep_dict
                    )
                    stored_count += 1
                
                await session.commit()
            
            # 清除相关缓存
            await self._invalidate_health_data_cache(user_id, "sleep")
            
            self.logger.info("存储睡眠数据成功",
                           user_id=user_id,
                           count=stored_count)
            
            return stored_count
            
        except Exception as e:
            self.logger.error("存储睡眠数据失败",
                            user_id=user_id,
                            error=str(e))
            raise
    
    async def store_heart_rate_data(
        self,
        user_id: str,
        heart_rate_data: List[HeartRateData]
    ) -> int:
        """存储心率数据"""
        try:
            stored_count = 0
            
            async with db_service.get_session() as session:
                for data in heart_rate_data:
                    # 转换为数据库模型
                    heart_rate_dict = data.dict()
                    heart_rate_dict.pop('id', None)  # 移除ID字段
                    
                    await self.health_data_repo.create_heart_rate_data(
                        session, heart_rate_dict
                    )
                    stored_count += 1
                
                await session.commit()
            
            # 清除相关缓存
            await self._invalidate_health_data_cache(user_id, "heart_rate")
            
            self.logger.info("存储心率数据成功",
                           user_id=user_id,
                           count=stored_count)
            
            return stored_count
            
        except Exception as e:
            self.logger.error("存储心率数据失败",
                            user_id=user_id,
                            error=str(e))
            raise
    
    async def get_activity_data(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
        source: Optional[DataSource] = None
    ) -> List[ActivityData]:
        """获取活动数据"""
        try:
            # 尝试从缓存获取
            cache_key = redis_service.get_health_data_key(
                user_id, "activity", f"{start_date}_{end_date}"
            )
            cached_data = await redis_service.get(cache_key)
            
            if cached_data and not source:
                return [ActivityData(**item) for item in cached_data]
            
            # 从数据库获取
            async with db_service.get_session() as session:
                activity_data_db = await self.health_data_repo.get_activity_data(
                    session, user_id, start_date, end_date, source
                )
                
                activity_data = [
                    ActivityData.from_orm(data_db)
                    for data_db in activity_data_db
                ]
                
                # 缓存结果（仅当无过滤条件时）
                if not source:
                    await redis_service.set(
                        cache_key,
                        [data.dict() for data in activity_data],
                        ttl=self.settings.cache.health_data_ttl
                    )
                
                return activity_data
                
        except Exception as e:
            self.logger.error("获取活动数据失败",
                            user_id=user_id,
                            error=str(e))
            raise
    
    async def get_sleep_data(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
        source: Optional[DataSource] = None
    ) -> List[SleepData]:
        """获取睡眠数据"""
        try:
            # 尝试从缓存获取
            cache_key = redis_service.get_health_data_key(
                user_id, "sleep", f"{start_date}_{end_date}"
            )
            cached_data = await redis_service.get(cache_key)
            
            if cached_data and not source:
                return [SleepData(**item) for item in cached_data]
            
            # 从数据库获取
            async with db_service.get_session() as session:
                sleep_data_db = await self.health_data_repo.get_sleep_data(
                    session, user_id, start_date, end_date, source
                )
                
                sleep_data = [
                    SleepData.from_orm(data_db)
                    for data_db in sleep_data_db
                ]
                
                # 缓存结果（仅当无过滤条件时）
                if not source:
                    await redis_service.set(
                        cache_key,
                        [data.dict() for data in sleep_data],
                        ttl=self.settings.cache.health_data_ttl
                    )
                
                return sleep_data
                
        except Exception as e:
            self.logger.error("获取睡眠数据失败",
                            user_id=user_id,
                            error=str(e))
            raise
    
    async def get_heart_rate_data(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
        source: Optional[DataSource] = None
    ) -> List[HeartRateData]:
        """获取心率数据"""
        try:
            # 尝试从缓存获取
            cache_key = redis_service.get_health_data_key(
                user_id, "heart_rate", f"{start_date}_{end_date}"
            )
            cached_data = await redis_service.get(cache_key)
            
            if cached_data and not source:
                return [HeartRateData(**item) for item in cached_data]
            
            # 从数据库获取
            async with db_service.get_session() as session:
                heart_rate_data_db = await self.health_data_repo.get_heart_rate_data(
                    session, user_id, start_date, end_date, source
                )
                
                heart_rate_data = [
                    HeartRateData.from_orm(data_db)
                    for data_db in heart_rate_data_db
                ]
                
                # 缓存结果（仅当无过滤条件时）
                if not source:
                    await redis_service.set(
                        cache_key,
                        [data.dict() for data in heart_rate_data],
                        ttl=self.settings.cache.health_data_ttl
                    )
                
                return heart_rate_data
                
        except Exception as e:
            self.logger.error("获取心率数据失败",
                            user_id=user_id,
                            error=str(e))
            raise
    
    async def get_health_summary(
        self,
        user_id: str,
        start_date: date,
        end_date: date
    ) -> HealthDataSummary:
        """获取健康数据汇总"""
        try:
            # 获取各类数据
            activity_data = await self.get_activity_data(user_id, start_date, end_date)
            sleep_data = await self.get_sleep_data(user_id, start_date, end_date)
            heart_rate_data = await self.get_heart_rate_data(user_id, start_date, end_date)
            
            # 计算汇总统计
            total_steps = sum(data.steps for data in activity_data if data.steps)
            total_distance = sum(data.distance for data in activity_data if data.distance)
            total_calories = sum(data.calories for data in activity_data if data.calories)
            
            avg_sleep_duration = 0
            if sleep_data:
                total_sleep_time = sum(data.total_sleep_time for data in sleep_data if data.total_sleep_time)
                avg_sleep_duration = total_sleep_time / len(sleep_data)
            
            avg_heart_rate = 0
            if heart_rate_data:
                total_heart_rate = sum(data.heart_rate for data in heart_rate_data if data.heart_rate)
                avg_heart_rate = total_heart_rate / len(heart_rate_data)
            
            summary = HealthDataSummary(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                total_steps=total_steps,
                total_distance=total_distance,
                total_calories=total_calories,
                avg_sleep_duration=avg_sleep_duration,
                avg_heart_rate=avg_heart_rate,
                activity_days=len(activity_data),
                sleep_days=len(sleep_data),
                heart_rate_records=len(heart_rate_data)
            )
            
            return summary
            
        except Exception as e:
            self.logger.error("获取健康数据汇总失败",
                            user_id=user_id,
                            error=str(e))
            raise
    
    # 私有方法
    
    async def _invalidate_health_data_cache(self, user_id: str, data_type: str):
        """清除健康数据缓存"""
        try:
            # 这里可以实现更精确的缓存清除逻辑
            # 暂时简单清除所有相关缓存
            pattern = f"health_data:{user_id}:{data_type}:*"
            # Redis没有直接的模式删除，这里只是示例
            self.logger.info("清除健康数据缓存", user_id=user_id, data_type=data_type)
        except Exception as e:
            self.logger.warning("清除健康数据缓存失败", error=str(e)) 