"""
Health Data Repository
"""

from datetime import datetime, date
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from ..model.health_data import ActivityDataDB, SleepDataDB, HeartRateDataDB, DataSource
from ..service.logging_config import LoggerMixin


class HealthDataRepository(LoggerMixin):
    """健康数据访问层"""
    
    async def create_activity_data(self, session: AsyncSession, activity_data: dict) -> ActivityDataDB:
        """创建活动数据"""
        try:
            activity = ActivityDataDB(**activity_data)
            session.add(activity)
            await session.flush()
            await session.refresh(activity)
            
            self.logger.info("创建活动数据成功", 
                           user_id=activity.user_id,
                           record_date=activity.record_date)
            return activity
            
        except Exception as e:
            self.logger.error("创建活动数据失败", error=str(e))
            raise
    
    async def get_activity_data(
        self,
        session: AsyncSession,
        user_id: str,
        start_date: date,
        end_date: date,
        source: Optional[DataSource] = None
    ) -> List[ActivityDataDB]:
        """获取活动数据"""
        try:
            stmt = select(ActivityDataDB).where(
                and_(
                    ActivityDataDB.user_id == user_id,
                    ActivityDataDB.record_date >= start_date,
                    ActivityDataDB.record_date <= end_date
                )
            )
            
            if source:
                stmt = stmt.where(ActivityDataDB.source == source.value)
            
            stmt = stmt.order_by(desc(ActivityDataDB.record_date))
            
            result = await session.execute(stmt)
            return result.scalars().all()
            
        except Exception as e:
            self.logger.error("获取活动数据失败",
                            user_id=user_id,
                            error=str(e))
            raise
    
    async def create_sleep_data(self, session: AsyncSession, sleep_data: dict) -> SleepDataDB:
        """创建睡眠数据"""
        try:
            sleep = SleepDataDB(**sleep_data)
            session.add(sleep)
            await session.flush()
            await session.refresh(sleep)
            
            self.logger.info("创建睡眠数据成功", 
                           user_id=sleep.user_id,
                           sleep_date=sleep.sleep_date)
            return sleep
            
        except Exception as e:
            self.logger.error("创建睡眠数据失败", error=str(e))
            raise
    
    async def get_sleep_data(
        self,
        session: AsyncSession,
        user_id: str,
        start_date: date,
        end_date: date,
        source: Optional[DataSource] = None
    ) -> List[SleepDataDB]:
        """获取睡眠数据"""
        try:
            stmt = select(SleepDataDB).where(
                and_(
                    SleepDataDB.user_id == user_id,
                    SleepDataDB.sleep_date >= start_date,
                    SleepDataDB.sleep_date <= end_date
                )
            )
            
            if source:
                stmt = stmt.where(SleepDataDB.source == source.value)
            
            stmt = stmt.order_by(desc(SleepDataDB.sleep_date))
            
            result = await session.execute(stmt)
            return result.scalars().all()
            
        except Exception as e:
            self.logger.error("获取睡眠数据失败",
                            user_id=user_id,
                            error=str(e))
            raise
    
    async def create_heart_rate_data(self, session: AsyncSession, heart_rate_data: dict) -> HeartRateDataDB:
        """创建心率数据"""
        try:
            heart_rate = HeartRateDataDB(**heart_rate_data)
            session.add(heart_rate)
            await session.flush()
            await session.refresh(heart_rate)
            
            self.logger.info("创建心率数据成功", 
                           user_id=heart_rate.user_id,
                           record_date=heart_rate.record_date)
            return heart_rate
            
        except Exception as e:
            self.logger.error("创建心率数据失败", error=str(e))
            raise
    
    async def get_heart_rate_data(
        self,
        session: AsyncSession,
        user_id: str,
        start_date: date,
        end_date: date,
        source: Optional[DataSource] = None
    ) -> List[HeartRateDataDB]:
        """获取心率数据"""
        try:
            stmt = select(HeartRateDataDB).where(
                and_(
                    HeartRateDataDB.user_id == user_id,
                    HeartRateDataDB.record_date >= start_date,
                    HeartRateDataDB.record_date <= end_date
                )
            )
            
            if source:
                stmt = stmt.where(HeartRateDataDB.source == source.value)
            
            stmt = stmt.order_by(desc(HeartRateDataDB.record_time))
            
            result = await session.execute(stmt)
            return result.scalars().all()
            
        except Exception as e:
            self.logger.error("获取心率数据失败",
                            user_id=user_id,
                            error=str(e))
            raise 